from src.database.async_database import engine, Base, logger
from sqlalchemy import select, func
import asyncio


async def check_table_exists():
    """Проверка наличия таблицы."""
    async with engine.begin() as conn:
        try:
            exists_query = select(func.count()).select_from(Base.metadata.tables["spimex_trading_results"])

            try:
                result = await conn.execute(exists_query)
                record_count = result.scalar_one_or_none()

                if record_count is not None:
                    logger.info(f"Таблица spimex_trading_results существует и содержит {record_count} записей.")
                else:
                    logger.warning("Таблицы spimex_trading_results не найдено!")
            except Exception as e:
                logger.error(f"Ошибка при проверке таблицы: {e}")
        except Exception as e:
            logger.error(f"Ошибка при проверке наличия таблицы: {e}")


async def main():
    await check_table_exists()


if __name__ == "__main__":
    asyncio.run(main())