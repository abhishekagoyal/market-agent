import os, sys, anthropic
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze_news(articles, country="US", category="finance"):
    if not articles:
        return "No articles fetched."
    from config.config_manager import load_config
    config  = load_config()
    cat_cfg = config["countries"].get(country, {}).get("categories", {}).get(category, {})
    role    = cat_cfg.get("prompt_role", "analyst")
    focus   = cat_cfg.get("prompt_focus", "key themes and risks")

    news_text = "\n\n".join([
        f"[{a['source']}] {a['title']}\n{a['summary']}"
        for a in articles
    ])

    prompt = f"""You are a {role}. Review today's headlines below.

{news_text}

Write a concise briefing (200-250 words) covering: {focus}.

Institutional tone. Be specific, not generic."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

if __name__ == "__main__":
    from fetcher import fetch_news
    country  = sys.argv[1] if len(sys.argv) > 1 else "US"
    category = sys.argv[2] if len(sys.argv) > 2 else "finance"
    print(analyze_news(fetch_news(country, category), country, category))