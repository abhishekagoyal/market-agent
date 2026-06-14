import os, sys, anthropic
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))
from categories import CATEGORIES

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze_news(articles, category="finance"):
    if not articles:
        return "No articles fetched."

    cat = CATEGORIES.get(category, CATEGORIES["finance"])

    news_text = "\n\n".join([
        f"[{a['source']}] {a['title']}\n{a['summary']}"
        for a in articles
    ])

    prompt = f"""You are a {cat['prompt_role']}. Review today's headlines below.

{news_text}

Write a concise briefing (200-250 words) covering: {cat['prompt_focus']}.

Institutional tone. Be specific, not generic."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

if __name__ == "__main__":
    from fetcher import fetch_news
    category = sys.argv[1] if len(sys.argv) > 1 else "finance"
    print(f"\nAnalyzing: {CATEGORIES[category]['label']}\n")
    print(analyze_news(fetch_news(category), category))