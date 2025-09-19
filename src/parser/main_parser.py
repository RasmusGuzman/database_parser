from typing import List, Dict
from datetime import datetime
from src.settings import DATE_FORMAT


def clean_value(value: str) -> float | int | str:
    value = value.strip()
    if ',' in value or '.' in value:
        return float(value.replace(',', ''))
    elif value.isdigit():
        return int(value)
    else:
        return value


def parse_pdf_file(pdf_file) -> List[Dict]:

    results = []
    tables = pdf_file.extract_tables()

    # Проход по каждой таблице документа
    for table in tables:
        headers = table.pop(0)  # Убираем заголовки

        # Проверяем наличие нужной таблицы ("Метрическая тонна")
        if any("Метрическая тонна" in header.lower() for header in headers):
            for row in table:
                # Извлекаем нужные поля
                exchange_product_id = row[headers.index("Код инструмента")]
                exchange_product_name = row[headers.index("Наименование инструмента")]
                delivery_basis_name = row[headers.index("Базис поставки")]
                volume = clean_value(row[headers.index("Объем договоров")])
                total = clean_value(row[headers.index("Сумма сделок")])
                count = clean_value(row[headers.index("Количество договоров")])

                # Добавляем запись, если количество договоров > 0
                if isinstance(count, int) and count > 0:
                    result_row = {
                        "exchange_product_id": exchange_product_id,
                        "exchange_product_name": exchange_product_name,
                        "oil_id": exchange_product_id[:4],
                        "delivery_basis_id": exchange_product_id[4:7],
                        "delivery_basis_name": delivery_basis_name,
                        "delivery_type_id": exchange_product_id[-1],
                        "volume": volume,
                        "total": total,
                        "count": count,
                        "date": datetime.strptime(headers[0].split(':')[1].strip(), DATE_FORMAT),
                        "created_on": datetime.utcnow(),
                        "updated_on": None
                    }

                    results.append(result_row)
    return results