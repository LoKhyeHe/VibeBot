# PatchUp Telegram Bot

A simple Telegram bot that greets users with a welcome message about **PatchUp**, a one-stop 3D printing service platform.

## Features

- `/start`: Sends a PatchUp welcome message.
- `/help`: Shows available commands.

## Setup

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and get the bot token.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variable:
   ```bash
   export TELEGRAM_BOT_TOKEN="<your_token>"
   ```
   Or copy `.env.example` and load it in your environment.

## Run

```bash
python bot.py
```

Once running, open your bot in Telegram and send `/start`.
