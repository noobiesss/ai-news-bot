import os
import sys
import requests
import anthropic

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")

PROMPT = """Search the web for the most important AI news from the last 24 hours
(model releases, research, major company moves, regulation, notable tools).
Write a Telegram digest:
- Start with a one-line headline: "AI News Digest"
- 5 to 7 items, each: a short bold-free title, 1-2 sentence summary, and the source URL
- Prioritize significance over volume; skip rumors and duplicates
- Plain text only, no markdown symbols. Keep under 3500 characters."""


def generate_digest() -> str:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 6}],
        messages=[{"role": "user", "content": PROMPT}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    if not text:
        raise RuntimeError("Empty digest returned")
    return text


def send_telegram(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for i in range(0, len(text), 4000):  # Telegram limit is 4096
        r = requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": text[i : i + 4000],
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        r.raise_for_status()


if __name__ == "__main__":
    try:
        send_telegram(generate_digest())
    except Exception as e:
        print(f"Failed: {type(e).__name__}", file=sys.stderr)
        sys.exit(1)
