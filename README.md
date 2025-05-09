# Pokémon TCG Stock Checker

A bot that monitors Pokémon TCG product availability across multiple websites and sends notifications via Telegram when items come in stock.

## Features

- Monitors multiple websites for Pokémon TCG products
- Focuses on booster boxes and elite trainer boxes
- Sends instant notifications via Telegram when items are in stock
- Sends daily status updates at 20:00
- Runs every 10 minutes
- Handles anti-bot protection with realistic browser headers

## Setup

1. Create a Telegram bot using [@BotFather](https://t.me/botfather)
2. Get your bot token and chat ID
3. Add these as secrets in your GitHub repository:
   - `BOT_TOKEN`: Your Telegram bot token
   - `CHAT_ID`: Your Telegram chat ID

## Websites Monitored

- Pokémon Center
- Board Game

## How to Use

The bot runs automatically every 10 minutes via GitHub Actions. You'll receive:
- Instant notifications when products come in stock
- Daily status updates at 20:00
- Test notification when the bot starts

## Development

To run locally:
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables:
   ```bash
   export BOT_TOKEN='your_bot_token'
   export CHAT_ID='your_chat_id'
   ```
4. Run the script: `python stock_checker.py` 