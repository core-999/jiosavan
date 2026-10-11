import os
from io import BytesIO

import aiohttp
from PIL import Image

from config import YOUTUBE_IMG_URL

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


async def get_thumb(videoid: str, user_id=None):
    """
    ဘယ် videoid လာလာ config ထဲက YOUTUBE_IMG_URL ကိုပဲ အမြဲတမ်း ပြန်ပေးမည်
    """
    return YOUTUBE_IMG_URL
