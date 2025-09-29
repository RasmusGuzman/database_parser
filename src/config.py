from dotenv import load_dotenv
import os

load_dotenv()

# Базовые настройки БД
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
BASE_URL = os.getenv("BASE_URL")
LOAD_FILE_URL = os.getenv("LOAD_FILE_URL")

# Настройки парсинга
SPIMEX_START_YEAR = int(os.getenv("SPIMEX_START_YEAR", 2023))
