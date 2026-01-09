import feedparser
import httpx
import asyncio
from datetime import datetime
from loguru import logger
from ...database import db

async def fetch_news(keyword: str):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    feed = feedparser.parse(response.text)

    for entry in feed.entries[:5]:
        await save_to_db(entry, keyword)

async def save_to_db(entry, keyword: str):
    mention_document = {
        "brand": keyword,
        "title": entry.title,
        "link": entry.link,
        "published": entry.published,
        "source": "google_news",
        "created_at": datetime.utcnow(),
        "is_processed": False
    }

    exist = await db.mentions.find_one({"link": entry.link})

    if not exist:
        await db.mentions.insert_one(mention_document)
        logger.success(f"Nova notícia salva: {entry.title[:50]}...")
    else:
        logger.warning(f"Notícia já existente: {entry.title[:50]}...")

