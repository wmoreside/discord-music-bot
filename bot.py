import asyncio
import os

import discord
import yt_dlp
from discord import app_commands
from dotenv import load_dotenv
from yt_dlp.utils import DownloadError

load_dotenv()

TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = os.environ["GUILD_ID"]
GUILD = discord.Object(GUILD_ID)

FFMPEG_BEFORE = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
FFMPEG_OPTIONS = "-vn"

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
}

# Incremented whenever /play or /stop is called to invalidate the current session.
# Tracks will only loop after stopping if the session has not changed.
session = 0


class MusicBot(discord.Client):
    async def setup_hook(self):
        await tree.sync(guild=GUILD)


client = MusicBot(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)


def get_stream_url(url: str) -> str:
    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:  # type: ignore
        info = ydl.extract_info(url, download=False)

    stream_url = None if info is None else info.get("url")

    if not isinstance(stream_url, str):
        raise DownloadError("No playable audio stream found.")

    return stream_url


async def play_looped(voice: discord.VoiceClient, url: str, my_session: int):
    # Stream URLs expire after a while, so re-resolve on every loop iteration.
    stream_url = await asyncio.to_thread(get_stream_url, url)

    # Just in case.
    if my_session != session or not voice.is_connected():
        return

    source = discord.FFmpegPCMAudio(
        stream_url,
        before_options=FFMPEG_BEFORE,
        options=FFMPEG_OPTIONS,
    )

    def restart(_):
        if my_session == session and voice.is_connected():
            asyncio.run_coroutine_threadsafe(
                play_looped(voice, url, my_session),
                client.loop,
            )

    voice.play(source, after=restart)


@tree.command(name="play", description="Play a song from a YouTube link", guild=GUILD)
@app_commands.describe(url="A YouTube link")
async def play(interaction: discord.Interaction, url: str):
    global session

    user = interaction.user
    if not isinstance(user, discord.Member):
        return

    guild = interaction.guild
    if guild is None:
        return

    if user.voice is None or user.voice.channel is None:
        await interaction.response.send_message(
            "You need to be in a voice channel to use /play.",
            ephemeral=True,
        )
        return

    # Resolving the URL can take a few seconds, so acknowledge early.
    await interaction.response.defer()

    session += 1

    voice = guild.voice_client
    channel = user.voice.channel
    if not isinstance(voice, discord.VoiceClient):
        voice = await channel.connect()
    elif voice.channel != channel:
        await voice.move_to(channel)

    if voice.is_playing():
        voice.stop()

    try:
        await play_looped(voice, url, session)
    except DownloadError:
        await interaction.followup.send(
            "Couldn't play that link. Make sure it's a valid YouTube URL.",
        )
        return

    await interaction.followup.send(f"Now playing: {url}")


@tree.command(name="stop", description="Stop playing and disconnect", guild=GUILD)
async def stop(interaction: discord.Interaction):
    global session

    session += 1

    guild = interaction.guild
    voice = None if guild is None else guild.voice_client
    if not isinstance(voice, discord.VoiceClient):
        await interaction.response.send_message("Nothing is playing.", ephemeral=True)
        return

    voice.stop()
    await voice.disconnect()
    await interaction.response.send_message("Bye!")


client.run(TOKEN)
