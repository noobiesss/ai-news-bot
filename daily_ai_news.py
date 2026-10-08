import os
import sys
import html
import time
from datetime import datetime, timezone, timedelta

import feedparser
import requests

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

FEEDS = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "MIT Tech Review": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    "VentureBeat": "https://venturebeat.com/category/ai/feed/",
    "Ars Technica": "https://arstechnica.com/ai/feed/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
}
MAX_PER_SOURCE = 3
MAX_TOTAL = 12
HOURS = 24


def entry_time(e):
    t = e.get("published_parsed") or e.get("updated_parsed")
    return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc) if t else None


def collect():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS)
    items, seen = [], set()
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue  # skip a broken feed, keep going
        count = 0
        for e in feed.entries:
            ts = entry_time(e)
            title = e.get("title", "").strip()
            link = e.get("link", "")
            if not ts or ts < cutoff or not title or title.lower() in seen:
                continue
            seen.add(title.lower())
            items.append((ts, source, title, link))
            count += 1
            if count >= MAX_PER_SOURCE:
                break
    items.sort(reverse=True)
    return items[:MAX_TOTAL]


def build_message(items):
    if not items:
        return "AI News Digest\n\nNo new AI articles found in the last 24 hours."
    lines = ["<b>AI News Digest</b>", ""]
    for _, source, title, link in items:
        lines.append(
            f'• <a href="{html.escape(link, quote=True)}">{html.escape(title)}</a> '
            f"<i>({html.escape(source)})</i>"
        )
    return "\n".join(lines)


def send(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text[:4000],
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=30,
    )
    r.raise_for_status()


if __name__ == "__main__":
    try:
        send(build_message(collect()))
    except Exception as e:
        print(f"Failed: {type(e).__name__}", file=sys.stderr)
        sys.exit(1)
