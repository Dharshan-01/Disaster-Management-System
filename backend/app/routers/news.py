import json
import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db, NewsItem
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

SAMPLE_NEWS = [
    {
        "title": "Wildfire Spreads Across 10,000 Acres in California",
        "summary": "A fast-moving wildfire has consumed over 10,000 acres in Northern California, prompting mass evacuations.",
        "source": "Reuters",
        "published_at": "2024-01-15T08:00:00",
        "link": "https://reuters.com/sample-wildfire-article",
        "disaster_tags": ["wildfire", "evacuation"],
    },
    {
        "title": "Record Floods Hit Bangladesh: Millions Displaced",
        "summary": "Unprecedented flooding in Bangladesh has displaced over 2 million people following weeks of intense monsoon rainfall.",
        "source": "BBC News",
        "published_at": "2024-01-14T12:30:00",
        "link": "https://bbc.com/sample-flood-article",
        "disaster_tags": ["flood", "monsoon"],
    },
    {
        "title": "Category 4 Cyclone Approaches Philippines",
        "summary": "A powerful Category 4 cyclone is projected to make landfall in the Philippines within 48 hours.",
        "source": "AP News",
        "published_at": "2024-01-13T06:15:00",
        "link": "https://apnews.com/sample-cyclone-article",
        "disaster_tags": ["cyclone", "storm"],
    },
    {
        "title": "Magnitude 6.8 Earthquake Strikes Japan",
        "summary": "A 6.8 magnitude earthquake struck off the coast of Hokkaido, Japan, triggering a tsunami warning.",
        "source": "NHK World",
        "published_at": "2024-01-12T03:45:00",
        "link": "https://nhk.or.jp/sample-earthquake-article",
        "disaster_tags": ["earthquake", "tsunami"],
    },
    {
        "title": "Landslides in Nepal Block Major Highways",
        "summary": "Heavy monsoon rains triggered multiple landslides in Nepal, blocking key highways and stranding hundreds.",
        "source": "Al Jazeera",
        "published_at": "2024-01-11T14:20:00",
        "link": "https://aljazeera.com/sample-landslide-article",
        "disaster_tags": ["landslide", "monsoon"],
    },
    {
        "title": "Early Warning System Saves Lives in Flood-Prone Region",
        "summary": "A new AI-powered early warning system helped evacuate thousands before major floods hit.",
        "source": "Guardian",
        "published_at": "2024-01-10T09:00:00",
        "link": "https://theguardian.com/sample-early-warning-article",
        "disaster_tags": ["flood", "technology", "early-warning"],
    },
    {
        "title": "Drought Emergency Declared in Horn of Africa",
        "summary": "Five countries in the Horn of Africa have declared drought emergencies as food insecurity worsens.",
        "source": "UN News",
        "published_at": "2024-01-09T11:00:00",
        "link": "https://news.un.org/sample-drought-article",
        "disaster_tags": ["drought", "food-security"],
    },
    {
        "title": "Volcano Eruption Alert Issued for Iceland",
        "summary": "Icelandic authorities issued an eruption alert as seismic activity near Reykjanes Peninsula intensified.",
        "source": "Reuters",
        "published_at": "2024-01-08T16:30:00",
        "link": "https://reuters.com/sample-volcano-article",
        "disaster_tags": ["volcano", "seismic"],
    },
]

DISASTER_KEYWORDS = [
    "flood", "wildfire", "fire", "cyclone", "hurricane", "typhoon",
    "earthquake", "landslide", "tsunami", "drought", "storm", "disaster",
    "emergency", "evacuation", "volcano",
]


def _tag_news(title: str, summary: str) -> List[str]:
    text = (title + " " + summary).lower()
    return [kw for kw in DISASTER_KEYWORDS if kw in text]


def _fetch_rss_items() -> List[dict]:
    items = []
    if not settings.NEWS_RSS_FEEDS:
        return items
    try:
        import feedparser
        for feed_url in settings.NEWS_RSS_FEEDS.split(","):
            feed_url = feed_url.strip()
            if not feed_url:
                continue
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    published = entry.get("published_parsed")
                    if published:
                        pub_dt = datetime(*published[:6]).isoformat()
                    else:
                        pub_dt = datetime.utcnow().isoformat()
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    items.append({
                        "title": title,
                        "summary": summary,
                        "source": feed.feed.get("title", feed_url),
                        "published_at": pub_dt,
                        "link": entry.get("link", ""),
                        "disaster_tags": _tag_news(title, summary),
                    })
            except Exception as e:
                logger.warning(f"Failed to parse RSS feed {feed_url}: {e}")
    except ImportError:
        logger.warning("feedparser not installed")
    return items


@router.get("/news")
async def get_news(db: Session = Depends(get_db)):
    db_items = db.query(NewsItem).order_by(NewsItem.published_at.desc()).limit(50).all()

    if db_items:
        return {
            "news": [
                {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "source": item.source,
                    "published_at": item.published_at.isoformat(),
                    "link": item.link,
                    "disaster_tags": json.loads(item.disaster_tags) if item.disaster_tags else [],
                }
                for item in db_items
            ],
            "total": len(db_items),
            "source": "database",
        }

    return {
        "news": SAMPLE_NEWS,
        "total": len(SAMPLE_NEWS),
        "source": "sample",
    }


@router.get("/news/refresh")
async def refresh_news(db: Session = Depends(get_db)):
    rss_items = _fetch_rss_items()
    added = 0
    for item in rss_items:
        existing = db.query(NewsItem).filter(NewsItem.link == item["link"]).first()
        if not existing:
            news = NewsItem(
                title=item["title"],
                summary=item["summary"],
                source=item["source"],
                published_at=datetime.fromisoformat(item["published_at"]),
                link=item["link"],
                disaster_tags=json.dumps(item["disaster_tags"]),
            )
            db.add(news)
            added += 1

    if rss_items:
        db.commit()

    return {
        "status": "refreshed",
        "fetched": len(rss_items),
        "added": added,
        "timestamp": datetime.utcnow().isoformat(),
    }
