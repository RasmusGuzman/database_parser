from typing import List, Dict


def clean_value(value: str) -> float | int | str:
    value = value.strip()
    if ',' in value or '.' in value:
        return float(value.replace(',', ''))
    elif value.isdigit():
        return int(value)
    else:
        return value


def parse_html_content(html: str) -> List[Dict]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'trading-results'})

    if not table:
        return []

    headers = [header.text.strip() for header in table.find_all('th')]
    results = []

    rows = table.find_all('tr')[1:]  # Пропускаем заголовок
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < len(headers):
            continue

        try:
            row_data = {
                'exchange_product_id': clean_value(cols[headers.index('Код инструмента')].text),
                'exchange_product_name': clean_value(cols[headers.index('Наименование инструмента')].text),
                'delivery_basis_name': clean_value(cols[headers.index('Базис поставки')].text),
                'volume': clean_value(cols[headers.index('Объем договоров')].text),
                'total': clean_value(cols[headers.index('Сумма сделок')].text),
                'count': clean_value(cols[headers.index('Количество договоров')].text)
            }

            if row_data['count'] > 0:
                row_data['oil_id'] = row_data['exchange_product_id'][:4]
                row_data['delivery_basis_id'] = row_data['exchange_product_id'][4:7]
                row_data['delivery_type_id'] = row_data['exchange_product_id'][-1]
                results.append(row_data)

        except Exception as e:
            print(f"Ошибка при парсинге строки: {e}")
            continue

    return results
