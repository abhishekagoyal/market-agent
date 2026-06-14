import feedparser
from categories import CATEGORIES

def fetch_news(category="finance", max_per_feed=5):
    feeds = CATEGORIES.get(category, CATEGORIES["finance"])["feeds"]
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
    import sys
    category = sys.argv[1] if len(sys.argv) > 1 else "finance"
    print(f"\nFetching: {CATEGORIES[category]['label']}\n")
    for a in fetch_news(category):
        print(f"[{a['source']}] {a['title']}")