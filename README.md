# discord-music-bot

A minimal Discord bot that loops the audio of a single YouTube link. Intended to be run locally and used in one server.

## Commands

- `/play <url>` - joins your voice channel and plays the linked track on repeat, indefinitely. Running `/play` again replaces the current track.
- `/stop` - stops playback and leaves the voice channel.

## Requirements

- Python 3
- FFmpeg on your PATH
- A Discord bot application invited to your server with the `bot` and `applications.commands` scopes and Connect + Speak permissions

## Setup

1. Install dependencies:

   ```sh
   pip install .
   ```

2. Copy `.env.example` to `.env` and fill in:

   - `DISCORD_TOKEN` - your bot token
   - `GUILD_ID` - your server's ID

## Run

```sh
python bot.py
```
