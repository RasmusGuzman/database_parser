from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DBAPIError
import logging

from src.settings import POSTGRES_ASYNC_URL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(filename)s:%(lineno)d: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

DATABASE_URL = POSTGRES_ASYNC_URL

try:
    engine: AsyncEngine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True
    )
    logger.info("Создан движок БД")
except Exception as e:
    logger.error(f"Ошибка при создании движка: {str(e)}")
    raise

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False
)

Base = declarative_base()

async def check_db_connection():
    try:
        logger.info("Проверяем подключение к БД...")
        async with engine.connect():
            logger.info("Подключение к БД успешно")
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {str(e)}")
        raise

async def init_db():
    try:
        async with engine.begin() as conn:
            try:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("База данных успешно инициализиорвана")
            except DBAPIError as e:
                logger.error(f"Ошибка SQLAlchemy DBAPI: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

async def get_db():
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        logger.error(f"Ошибка при получении сессии: {str(e)}")
        raise
