CATEGORIES = {
    "finance": {
        "label": "Finance & Markets",
        "feeds": {
            "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
            "MarketWatch":   "https://feeds.marketwatch.com/marketwatch/topstories/",
            "CNBC":          "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        },
        "prompt_role":  "capital markets analyst",
        "prompt_focus": "macro/market themes, key risks, and a sector or asset class in focus",
        "schedule": {"hour": 8, "minute": 30},
    },
    "tech": {
        "label": "Technology",
        "feeds": {
            "TechCrunch":   "https://techcrunch.com/feed/",
            "The Verge":    "https://www.theverge.com/rss/index.xml",
            "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
        },
        "prompt_role":  "technology industry analyst",
        "prompt_focus": "key product launches, industry trends, and companies to watch",
        "schedule": {"hour": 8, "minute": 0},
    },
    "real_estate": {
        "label": "Real Estate",
        "feeds": {
            "HousingWire": "https://www.housingwire.com/feed/",
            "Inman":       "https://www.inman.com/feed/",
        },
        "prompt_role":  "real estate market analyst",
        "prompt_focus": "market trends, mortgage rates, and regional hotspots",
        "schedule": None,
    },
    "fashion": {
        "label": "Fashion & Retail",
        "feeds": {
            "WWD":         "https://wwd.com/feed/",
            "Fashionista": "https://fashionista.com/.rss/excerpt/",
        },
        "prompt_role":  "fashion industry analyst",
        "prompt_focus": "brand news, trend directions, and retail performance",
        "schedule": None,
    },
}