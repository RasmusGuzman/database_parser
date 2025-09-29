import asyncio
import time
from src.database.async_database import init_db
from src.parser.main_parser import SPIMEXParserService, ExcelParser, TradingResultRepository, SPIMEXHttpClient

# Основной цикл выполнения
async def main():
    await init_db()

    http_client = SPIMEXHttpClient()
    excel_parser = ExcelParser()
    repository = TradingResultRepository()
    service = SPIMEXParserService(http_client, excel_parser, repository)
    try:
        await service.run()
        print("Парсинг завершен успешно!")
    except Exception as e:
        print(f"Произошла ошибка при выполнении парсинга: {e}")



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Парсинг прерван пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        print("Программа завершает работу")
