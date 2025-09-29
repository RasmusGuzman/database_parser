import os
from datetime import datetime
from src.config import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATE_FORMAT = "%Y-%m-%d"
TODAY_DATE = datetime.now().strftime(DATE_FORMAT)



POSTGRES_ASYNC_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

)

POSTGRES_SYNC_URL = POSTGRES_ASYNC_URL.replace (
    'postgresql+asyncpg', 'postgresql'
)

FAKE_DATA = [
    {
        "exchange_product_id": "SP-12345",
        "exchange_product_name": "Нефть марки Urals",
        "oil_id": "OIL-1",
        "delivery_basis_id": "DB-101",
        "delivery_basis_name": "Порт Новороссийск",
        "delivery_type_id": "DT-1",
        "volume": 100000.0,
        "total": 7550000.0,  # volume * price
        "count": 1,
        "date": pd.Timestamp.now(),
        "created_on": pd.Timestamp.now(),
        "updated_on": pd.Timestamp.now()
    },
    {
        "exchange_product_id": "BR-67890",
        "exchange_product_name": "Бензин АИ-95",
        "oil_id": "OIL-2",
        "delivery_basis_id": "DB-102",
        "delivery_basis_name": "НПЗ Москва",
        "delivery_type_id": "DT-2",
        "volume": 50000.0,
        "total": 2637500.0,  # volume * price
        "count": 1,
        "date": pd.Timestamp.now(),
        "created_on": pd.Timestamp.now(),
        "updated_on": pd.Timestamp.now()
    },
    {
        "exchange_product_id": "GA-11111",
        "exchange_product_name": "Газ природный",
        "oil_id": "OIL-3",
        "delivery_basis_id": "DB-103",
        "delivery_basis_name": "Точка сдачи А",
        "delivery_type_id": "DT-3",
        "volume": 200000.0,
        "total": 5000000.0,  # volume * price
        "count": 1,
        "date": pd.Timestamp.now(),
        "created_on": pd.Timestamp.now(),
        "updated_on": pd.Timestamp.now()
    }
]
