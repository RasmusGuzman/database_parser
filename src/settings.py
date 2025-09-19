import os
from datetime import datetime
from src.config import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATE_FORMAT = "%Y-%m-%d"
TODAY_DATE = datetime.now().strftime(DATE_FORMAT)

POSTGRES_SYNC_URL = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
POSTGRES_ASYNC_URL = POSTGRES_SYNC_URL.replace(
    'postgresql', 'postgresql+asyncpg'
)