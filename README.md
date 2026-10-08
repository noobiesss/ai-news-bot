# Daily AI News Telegram Bot

## Setup
1. Message your bot once on Telegram (send "hi").
2. Get your chat ID: open https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates in a browser
   and read `message.chat.id`.
3. Push this folder to a **private** GitHub repo.
4. Repo > Settings > Secrets and variables > Actions > add:
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
   - ANTHROPIC_API_KEY (from console.anthropic.com)
5. Actions tab > "Daily AI News" > Run workflow to test.

Runs daily at 12:00 PM MYT. Note: GitHub cron can be delayed by several minutes.

## Local test
export TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... ANTHROPIC_API_KEY=...
pip install -r requirements.txt && python daily_ai_news.py
