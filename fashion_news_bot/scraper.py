"""
Fetches fresh fashion articles from NewsAPI and RSS feeds.

The scraper module interacts with the News API (if enabled via
configuration) and any RSS feeds specified in the environment.  It
deduplicates articles based on a hash of the source, URL and title and
returns only those that have not been seen before.
"""

import hashlib
import logging
from typing import List, Dict

import requests
import feedparser

from .config import settings
from .storage import load_published_hashes

logger = logging.getLogger(__name__)


def _hash_article(source: str, url: str, title: str) -> str:
    """Generate a SHA256 hash for an article based on its source, URL and title."""
    base = f"{source}|{url}|{title}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def fetch_from_newsapi() -> List[Dict]:
    """Fetch articles from NewsAPI, if configured.

    Returns an empty list if NewsAPI is disabled or no key is provided.
    """
    if not settings.use_newsapi:
        logger.info("NewsAPI está desactivado por configuración (USE_NEWSAPI=false).")
        return []
    if not settings.newsapi_key:
        logger.warning("NEWSAPI_KEY no configurada. Saltando NewsAPI.")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": settings.newsapi_query,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": settings.max_articles_per_run * 5,
    }
    headers = {"Authorization": settings.newsapi_key}
    logger.info("Solicitando noticias a NewsAPI…")
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        logger.error("Error al consultar NewsAPI: %s", e)
        return []
    data = resp.json()
    articles = []
    for a in data.get("articles", []):
        articles.append({
            "source": a.get("source", {}).get("name"),
            "url": a.get("url"),
            "title": a.get("title"),
            "description": a.get("description"),
            "content": a.get("content"),
            "image_url": a.get("urlToImage"),
            "published_at": a.get("publishedAt"),
            "author": a.get("author"),
            "origin": "newsapi",
        })
    logger.info("NewsAPI devolvió %d artículos", len(articles))
    return articles


def fetch_from_rss() -> List[Dict]:
    """Fetch articles from configured RSS feeds."""
    results: List[Dict] = []
    for feed_url in settings.rss_feeds:
        if not feed_url:
            continue
        logger.info("Leyendo RSS: %s", feed_url)
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            image_url = None
            # extraer imagen de enclosure o media_content
            if "media_content" in entry and entry.media_content:
                image_url = entry.media_content[0].get("url")
            elif "links" in entry:
                for l in entry.links:
                    if l.get("rel") == "enclosure" and "image" in l.get("type", ""):
                        image_url = l.get("href")
                        break
            results.append({
                "source": feed.feed.get("title", "RSS"),
                "url": entry.get("link"),
                "title": entry.get("title"),
                "description": entry.get("summary"),
                "content": entry.get("summary"),
                "image_url": image_url,
                "published_at": entry.get("published"),
                "author": getattr(entry, "author", None),
                "origin": "rss",
            })
    logger.info("RSS total: %d artículos", len(results))
    return results


def get_fresh_fashion_articles(limit: int = None) -> List[Dict]:
    """Return a list of new, deduplicated articles.

    Articles already present in the published database are filtered out.  A
    limit can be specified to restrict the number of returned articles.
    """
    if limit is None:
        limit = settings.max_articles_per_run
    published_hashes = load_published_hashes()
    candidates: List[Dict] = []
    # aggregate from sources
    candidates.extend(fetch_from_newsapi())
    candidates.extend(fetch_from_rss())
    fresh = []
    for art in candidates:
        h = _hash_article(art.get("source", ""), art.get("url", ""), art.get("title", ""))
        art["hash"] = h
        if h not in published_hashes:
            fresh.append(art)
    logger.info("Artículos nuevos detectados: %d", len(fresh))
    # sort by published date descending (if available)
    fresh.sort(key=lambda x: x.get("published_at") or "", reverse=True)
    return fresh[:limit]