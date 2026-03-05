# PatchUp Telegram Bot

Telegram bot for PatchUp that walks a lead through an end-to-end 3D printing order flow.

## What it does

- Greets users with clear onboarding instructions and service flow.
- Presents simple options:
  - `🛠️ Start Order`
  - `📦 View Order`
  - `💬 Submit Feedback`
- Runs this workflow for **Start Order**:
  1. Lead enters via Telegram
  2. Structured request collected
  3. Review + slicing
  4. Quote sent (24h expiry)
  5. User accepts quote
  6. Deposit requested + proof
  7. Deposit confirmed
  8. Printing
  9. Completion notice
  10. Balance payment
  11. Delivery/meetup
  12. Feedback request

## Setup

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and copy the token.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set your token:

   ```bash
   export TELEGRAM_BOT_TOKEN="<your_token>"
   ```
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

In Telegram, send `/start` to begin.
Once running, open your bot in Telegram and send `/start`.
