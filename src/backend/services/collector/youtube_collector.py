import asyncio
from yt_dlp import YoutubeDL
from datetime import datetime
from loguru import logger
from ...database import db

class YoutubeCollector:
    def __init__(self):
        self.ydl_opts = {
            'getcomments': True,
            'skip_download': True,
            'extract_flat': True,
        }

    async def collect_video_comments(self, video_url: str, brand: str):
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: self.extract_info(video_url))

        comments = info.get('comments', [])

        for comment in comments[:50]:
            mention = {
                "source": "youtube",
                "brand": brand,
                "external_id": comment.get('id'),
                "content": comment.get('text'),
                "author": comment.get('author'),
                "url": video_url,
                "created_at": datetime.utcnow(),
                "is_processed": False
            }

            await db.mentions.update_one(
                {"external_id": mention["external_id"], "source": "youtube"},
                {"$set": mention },
                upsert=True
            )

def _extract(self, url):
        with YoutubeDL(self.ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)