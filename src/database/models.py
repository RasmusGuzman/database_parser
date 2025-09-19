from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SpimexTradingResult(Base):
    __tablename__ = 'spimex_trading_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange_product_id = Column(String(10))
    exchange_product_name = Column(String(255))
    oil_id = Column(String(4))  # Первые четыре символа product_id
    delivery_basis_id = Column(String(3))  # Следующие три символа product_id
    delivery_basis_name = Column(String(255))
    delivery_type_id = Column(String(1))  # Последний символ product_id
    volume = Column(Float)
    total = Column(Float)
    count = Column(Integer)
    date = Column(DateTime)
    created_on = Column(DateTime, default=datetime.utcnow())
    updated_on = Column(DateTime, onupdate=datetime.utcnow(), nullable=True)