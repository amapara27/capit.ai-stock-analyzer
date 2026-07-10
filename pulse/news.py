import datetime as dt
import hashlib
import os
import time

import requests
import yfinance as yf

from pulse.config import CHROMA_DIR

# Rebrand in progress: Massive (ex-Polygon.io) still serves the polygon domain
MASSIVE_BASE = "https://api.polygon.io"


def _massive_get(path: str, params: dict) -> dict:
    params["apiKey"] = os.environ["MASSIVE_API_KEY"]
    time.sleep(13)  # free tier: 5 req/min
    resp = requests.get(MASSIVE_BASE + path, params=params, timeout=30)
    if resp.status_code == 429:
        time.sleep(60)
        resp = requests.get(MASSIVE_BASE + path, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _fetch_massive(ticker: str, limit: int) -> list[dict]:
    data = _massive_get("/v2/reference/news", {"ticker": ticker, "limit": limit})
    return [{
        "url": a.get("article_url", ""),
        "title": a.get("title", ""),
        "summary": a.get("description") or "",
        "published": a.get("published_utc", ""),
        "source": a.get("publisher", {}).get("name", "Massive"),
        "ticker": ticker,
    } for a in data.get("results", [])]


def _fetch_yfinance(ticker: str, limit: int) -> list[dict]:
    articles = []
    for item in yf.Ticker(ticker).news[:limit]:
        content = item.get("content", {}) or {}
        url = (content.get("canonicalUrl") or {}).get("url") or \
              (content.get("clickThroughUrl") or {}).get("url") or item.get("link")
        title = content.get("title") or item.get("title")
        if not url or not title:
            continue
        pub = content.get("pubDate") or item.get("providerPublishTime")
        if isinstance(pub, (int, float)):
            pub = dt.datetime.fromtimestamp(pub).isoformat()
        articles.append({
            "url": url,
            "title": title,
            "summary": content.get("summary") or "",
            "published": pub or "",
            "source": (content.get("provider") or {}).get("displayName") or item.get("publisher", "Yahoo Finance"),
            "ticker": ticker,
        })
    return articles


def fetch_news(ticker: str, limit: int = 10) -> list[dict]:
    """Fetch recent news for a ticker: Massive if a key is set, else yfinance."""
    if os.getenv("MASSIVE_API_KEY"):
        try:
            return _fetch_massive(ticker, limit)
        except requests.HTTPError as e:
            print(f"Massive request failed ({e}), falling back to yfinance")
    return _fetch_yfinance(ticker, limit)


def _collection():
    import chromadb  # deferred: first import downloads the ONNX embedder (~80MB)
    return chromadb.PersistentClient(path=CHROMA_DIR).get_or_create_collection("news")


def store_news(articles: list[dict]) -> int:
    """Upsert articles into Chroma; sha1(url) ids make re-runs idempotent. Returns new-doc count."""
    articles = [a for a in articles if a["url"]]
    if not articles:
        return 0
    col = _collection()
    ids = [hashlib.sha1(a["url"].encode()).hexdigest() for a in articles]
    existing = set(col.get(ids=ids)["ids"])
    col.upsert(
        ids=ids,
        documents=[f"{a['title']}\n{a['summary']}".strip() for a in articles],
        metadatas=[{"ticker": a["ticker"], "date": a["published"], "source": a["source"],
                    "url": a["url"], "title": a["title"]} for a in articles],
    )
    return len(set(ids) - existing)


def search_news(query: str, ticker: str | None = None, k: int = 5) -> list[dict]:
    """Semantic search over stored news; optionally filter to one ticker."""
    col = _collection()
    if col.count() == 0:
        return []
    res = col.query(query_texts=[query], n_results=min(k, col.count()),
                    where={"ticker": ticker} if ticker else None)
    return res["metadatas"][0]


if __name__ == "__main__":
    articles = fetch_news("AAPL")
    print(f"fetched {len(articles)} articles")
    assert articles, "no articles fetched"
    new = store_news(articles)
    print(f"stored {new} new docs (0 on re-run = dedup works)")
    hits = search_news("earnings", ticker="AAPL")
    print(f"search hits: {[h['title'][:60] for h in hits]}")
    assert hits, "search returned nothing"
    print("news self-check OK")
