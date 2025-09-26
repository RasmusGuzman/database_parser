import aiohttp
from datetime import datetime, timedelta
import asyncio
from typing import List, Dict, Protocol
from bs4 import BeautifulSoup
from src.database.async_database import get_db
from src.database.models import TradingResult
import logging
from src.config import BASE_URL
from src.config import SPIMEX_START_YEAR


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SPIMEX_START_DATE = datetime(SPIMEX_START_YEAR, 1, 1)

class HttpClientProtocol(Protocol):
    async def download_page(self, session: aiohttp.ClientSession, page_url: str) -> str:
        ...


class SPIMEXHttpClient(HttpClientProtocol):
    def __init__(self, base_url: str = BASE_URL):
        if not base_url.startswith(('http://', 'https://')):
            raise ValueError("Некорректный URL: должен начинаться с http:// или https://")
        self.base_url = base_url

    async def download_page(self, session: aiohttp.ClientSession, page_url: str) -> str:
        try:
            async with session.get(page_url, timeout=30) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logger.error(f"Ошибка при загрузке страницы: {e}")
            return ""

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


class HTMLParser:
    def parse(self, html: str) -> List[Dict]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            data = []

            for item in soup.find_all('div', class_='accordeon-inner__wrap-item'):
                try:
                    # Проверяем существование элементов перед обращением к ним
                    title_element = item.find('a', class_='accordeon-inner__item-title')
                    date_element = item.find('p').find('span')

                    if not title_element or not date_element:
                        continue  # Пропускаем неполные записи

                    link = title_element.get('href')
                    date_str = date_element.text.strip()

                    try:
                        date = datetime.strptime(date_str, '%d.%m.%Y')
                    except ValueError:
                        logger.error(f"Неверный формат даты: {date_str}")
                        continue


                    exchange_product_id = item.find('div', class_='product-id').text.strip() if item.find('div',
                                                                                                          class_='product-id') else None
                    oil_id = item.find('div', class_='oil-id').text.strip() if item.find('div',
                                                                                         class_='oil-id') else None

                    delivery_basis_id = item.find('div', class_='delivery_basis_id').text.strip() if item.find('div',
                                                                                         class_='delivery_basis_id') else None

                    delivery_basis_name = item.find('div', class_='delivery_basis_name').text.strip() if item.find('div',
                                                                                         class_='delivery_basis_name') else None
                    delivery_type_id = item.find('div', class_='delivery_type_id').text.strip() if item.find('div',
                                                                                         class_='delivery_type_id') else None
                    volume = item.find('div', class_='volume').text.strip() if item.find('div',
                                                                                         class_='volume') else None
                    total = item.find('div', class_='total').text.strip() if item.find('div',
                                                                                         class_='total') else None
                    count = item.find('div', class_='count').text.strip() if item.find('div',
                                                                                         class_='count') else None

                    created_on = item.find('div', class_='created_on').text.strip() if item.find('div',
                                                                                         class_='created_on') else None
                    updated_on = item.find('div', class_='updated_on').text.strip() if item.find('div',
                                                                                         class_='updated_on') else None

                    data.append({
                        'date': date,
                        'link': link,
                        'exchange_product_id': exchange_product_id,
                        'oil_id': oil_id,
                        'delivery_basis_id': delivery_basis_id,
                        'delivery_basis_name': delivery_basis_name,
                        'delivery_type_id': delivery_type_id,
                        'volume': volume,
                        'total': total,
                        'count': count,
                        'created_on': created_on,
                        'updated_on': updated_on
                    })
                except Exception as e:
                    logger.error(f"Ошибка при парсинге элемента: {e}")

            return data
        except Exception as e:
            logger.error(f"Ошибка при парсинге HTML: {e}")
            return []



class TradingResultRepository:
    async def save(self, data: List[Dict], date: datetime):
        async for db in get_db():
            try:
                records = [
                    TradingResult(
                        exchange_product_id=item.get('exchange_product_id') or '',
                        exchange_product_name=item.get('exchange_product_name') or '',
                        oil_id=item.get('oil_id') or '',
                        delivery_basis_id=item.get('delivery_basis_id') or '',
                        delivery_basis_name=item.get('delivery_basis_name') or '',
                        delivery_type_id=item.get('delivery_type_id') or '',
                        volume=item.get('volume') or 0,
                        total=item.get('total') or 0,
                        count=item.get('count') or 0,
                        date=date,
                        created_on=datetime.utcnow(),
                        updated_on=datetime.utcnow()
                    )
                    for item in data
                ]

                # Добавляем проверку на пустые записи
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
            parser: HTMLParser,
            repository: TradingResultRepository,
    ):
        self.http_client = http_client
        self.parser = parser
        self.repository = repository

    async def process_page(self, session: aiohttp.ClientSession, page_number: int):

        page_url = f"{self.http_client.base_url}?page=page-{page_number}"

        html = await self.http_client.download_page(session, page_url)

        if not html:
            return

        parsed_data = self.parser.parse(html)

        if not parsed_data:
            return

        # Группируем данные по датам для корректного сохранения
        for item in parsed_data:
            try:

                date = item['date']

                if date < SPIMEX_START_DATE:
                     logger.info("Данные из этого файла устарели")
                     return
                else:
                    await self.repository.save([item], date)
            except Exception as e:
                logger.error(f"Ошибка при обработке данных страницы {page_number}: {e}")

    async def run(self):
        async with aiohttp.ClientSession() as session:

            total_pages = await self.http_client.get_total_pages(session)
            if total_pages == 0:
                logger.error("Не удалось определить количество страниц")
                return

            logger.info(f"Всего страниц для обработки: {total_pages}")

            try:

                tasks = [self.process_page(session, page) for page in range(1, total_pages + 1)]
                await asyncio.gather(*tasks)
            except Exception as e:
                logger.error(f"Ошибка при обработке страниц")
