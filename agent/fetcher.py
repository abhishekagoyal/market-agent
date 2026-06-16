import feedparser, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def fetch_news(country="US", category="finance", max_per_feed=5):
    from config.config_manager import load_config
    config = load_config()
    feeds = (
        config["countries"]
        .get(country, {})
        .get("categories", {})
        .get(category, {})
        .get("feeds", {})
    )
    articles = []
    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                articles.append({
                    "source":  source,
                    "title":   entry.get("title", ""),
                    "summary": entry.get("summary", "")[:300],
                    "link":    entry.get("link", ""),
                })
        except Exception as e:
            print(f"Skipping {source}: {e}")
    return articles

if __name__ == "__main__":
    country  = sys.argv[1] if len(sys.argv) > 1 else "US"
    category = sys.argv[2] if len(sys.argv) > 2 else "finance"
    print(f"\nFetching: {country} / {category}\n")
    for a in fetch_news(country, category):
        print(f"[{a['source']}] {a['title']}")