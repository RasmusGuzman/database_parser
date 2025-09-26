import asyncio
from src.database.async_database import init_db
from src.parser.main_parser import SPIMEXParserService, HTMLParser, TradingResultRepository, SPIMEXHttpClient


async def main():
    await init_db()

    http_client = SPIMEXHttpClient()
    parser = HTMLParser()
    repository = TradingResultRepository()
    service = SPIMEXParserService(http_client, parser, repository)
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
