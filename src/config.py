import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from redis import Redis

if os.path.isfile(".env"):
    load_dotenv(".env")


REDIS_URL = "redis://redis-db:6379"

redis = Redis(
    host="redis-db",
    port=6379,
    charset="utf-8",
    decode_responses=True,
)
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
TMP_DIRECTORY = Path("/tmp/serve/")


TMP_DIRECTORY.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.DEBUG, force=True)
logger = logging.getLogger("core")
