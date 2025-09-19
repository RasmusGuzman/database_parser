from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.settings import POSTGRES_SYNC_URL

engine = create_engine(POSTGRES_SYNC_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_sync_db():

    try:
        Base.metadata.create_all(engine)
        print("База данных успешно инициализирована.")
    except Exception as e:
        print(f"Произошла ошибка при создании базы данных: {e}")

