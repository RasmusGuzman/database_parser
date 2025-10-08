from concurrent.futures import ProcessPoolExecutor
from typing import Optional, List, Dict
from datetime import datetime
import os
import aiohttp
import asyncio
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
from src.database.async_database import get_db, AsyncSessionLocal
from src.database.models import TradingResult
import logging
from src.config import BASE_URL, LOAD_FILE_URL

from src.config import SPIMEX_START_YEAR
from src.settings import PARSER_DATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SPIMEX_START_DATE = pd.to_datetime(f'{SPIMEX_START_YEAR}-01-01')


class SPIMEXHttpClient:
    def __init__(self, base_url: str = BASE_URL, load_file_url: str = LOAD_FILE_URL):
        if not base_url.startswith(('http://', 'https://')):
            raise ValueError("Некорректный URL: должен начинаться с http:// или https://")
        if not load_file_url.startswith(('http://', 'https://')):
            raise ValueError("Некорректный URL: должен начинаться с http:// или https://")
        self.base_url = base_url
        self.load_file_url = load_file_url
        self.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}


    async def download_file(self, session: aiohttp.ClientSession, file_url: str) -> bytes:
        if "https://spimex.com/files/trades/result/upload/reports/" in file_url:
            try:
                async with session.get(file_url, timeout=30) as response:
                    response.raise_for_status()
                    data = await response.read()
                    return data
            except Exception as e:
                logger.error(f"Ошибка при скачивании файла: {e}")
                return b""
        return b""

    async def get_total_pages(self, session: aiohttp.ClientSession) -> int:
        html = await self.download_page(session, self.base_url)
        soup = BeautifulSoup(html, 'html.parser')
        pagination = soup.find('div', class_='bx-pagination')
        if not pagination:
            logger.error("Элемент пагинации не найден")
            return 0

        page_links = pagination.find('ul').find_all('a')
        if not page_links:
            logger.error("Номера страниц не найдены")
            return 0

        last_page = page_links[-2].text.strip()
        return int(last_page)

    async def download_page(self, session: aiohttp.ClientSession, page_url: str) -> Optional[str]:
        try:
            async with session.get(page_url, headers=self.headers, timeout=30) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientResponseError as cre:
            logger.error(f"HTTP ошибка ({cre.status}) при загрузке страницы {page_url}: {cre.message}")
        except aiohttp.ServerTimeoutError:
            logger.error(f"Тайм-аут при загрузке страницы {page_url}. Время ожидания превышено.")
        except aiohttp.ClientConnectionError:
            logger.error(f"Ошибка соединения при загрузке страницы {page_url}. Невозможно установить связь с сервером.")
        except aiohttp.ContentTypeError:
            logger.error(f"Неподдерживаемый тип контента при загрузке страницы {page_url}.")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке страницы {page_url}: {e}")
        return None


class ExcelParser:
    @staticmethod
    def parse_excel(content: bytes) -> list:

        try:
            excel_data = BytesIO(content)
            df = pd.read_excel(excel_data, skiprows=3, header=None)
            data = []
            date_check = False
            check_point = False
            for row in df.iterrows():
                check_row = row[1].to_dict()
                if not date_check:
                    date_str = check_row[1][-10:]
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                    if date_obj >= PARSER_DATE:
                        date_check = True
                if date_check:
                    if check_row[1] == 'Единица измерения: Метрическая тонна':
                        check_point = True
                    elif check_row[1] == 'Итого':
                        check_point = False
                    if check_point:
                        try:
                            count = int(check_row[14])
                            record = {
                                'exchange_product_id': str(check_row[1]),
                                'exchange_product_name': str(check_row[2]),
                                'oil_id': str(check_row[1])[:4],
                                'delivery_basis_id': str(check_row[1])[4:7],
                                'delivery_basis_name': str(check_row[3]),
                                'delivery_type_id': str(check_row[1])[-1],
                                'volume': check_row[4],
                                'total': check_row[5],
                                'count': count,
                                'date': pd.Timestamp.now().date(),
                                'created_on': pd.Timestamp.now(),
                                'updated_on': pd.Timestamp.now()
                            }
                            data.append(record)
                        except Exception:
                            pass

            return data
        except Exception as e:
            print(f"Ошибка при парсинге Excel: {e}")
            return []


class TradingResultRepository:
    async def save(self, data: list):
        async for db in get_db():
            try:
                records = [
                    TradingResult(
                        exchange_product_id=item.get('exchange_product_id'),
                        exchange_product_name=item.get('exchange_product_name'),
                        oil_id=item.get('oil_id'),
                        delivery_basis_id=item.get('delivery_basis_id'),
                        delivery_basis_name=item.get('delivery_basis_name'),
                        delivery_type_id=item.get('delivery_type_id'),
                        volume=float(item.get('volume')),
                        total=float(item.get('total')),
                        count=item.get('count'),
                        date=item.get('date'),
                        created_on=item.get('created_on'),
                        updated_on=item.get('updated_on')
                    ) for item in data
                ]

                if records:
                    db.add_all(records)
                    await db.commit()
            except Exception as e:
                logger.error(f"Ошибка при сохранении данных: {e}")
                await db.rollback()


class SPIMEXParserService:
    def __init__(
            self,
            http_client: SPIMEXHttpClient,
            excel_parser: ExcelParser,
            repository: TradingResultRepository,
    ):
        self.http_client = http_client
        self.excel_parser = excel_parser
        self.repository = repository

    async def process_page(self, session: aiohttp.ClientSession, page_number: int):
        page_url = f"{self.http_client.base_url}?page={page_number}"
        html = await self.http_client.download_page(session, page_url)
        soup = BeautifulSoup(html, 'html.parser')

        links = soup.select('.xls')

        executor = ProcessPoolExecutor(max_workers=os.cpu_count())
        loop = asyncio.get_event_loop()

        results = []
        for link in links:
            file_url = self.http_client.load_file_url + link['href']
            content = await self.http_client.download_file(session, file_url)

            if content:
                parsed_data = await loop.run_in_executor(executor, self.excel_parser.parse_excel, content)
                results.extend(parsed_data)
            await asyncio.sleep(0)
            await self.repository.save(results)

    async def limited_task(self, session, page, semaphore):
        async with semaphore:
            await self.process_page(session, page)

    async def run(self):
        async with aiohttp.ClientSession() as session:
            total_pages = await self.http_client.get_total_pages(session)

            if total_pages == 0:
                logger.error("Не удалось определить количество страниц")
                return

            logger.info(f"Всего страниц для обработки: {total_pages}")

            semaphore = asyncio.Semaphore(10)  # Устанавливаем предел на 10 параллельных задач

            tasks = [self.limited_task(session, page, semaphore) for page in range(1, total_pages + 1)]
            await asyncio.gather(*tasks)