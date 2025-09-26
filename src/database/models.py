from sqlalchemy import Column, Integer, String, Float, DateTime
from src.database.async_database import Base


class TradingResult(Base):
    __tablename__ = "spimex_trading_results"

    id = Column(Integer, primary_key=True, index=True)
    exchange_product_id = Column(String, index=True)
    exchange_product_name = Column(String)
    oil_id = Column(String)
    delivery_basis_id = Column(String)
    delivery_basis_name = Column(String)
    delivery_type_id = Column(String)
    volume = Column(Float)
    total = Column(Float)
    count = Column(Integer)
    date = Column(DateTime)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
