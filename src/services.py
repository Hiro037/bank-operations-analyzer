import json
import logging

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def simple_search(file_path: str, search_query: str) -> str:
    """
    Возвращает JSON-ответ с транзакциями, содержащими запрос в описании или категории.

    :param file_path: Путь к Excel-файлу с транзакциями.
    :param search_query: Строка для поиска.
    :return: JSON-строка с транзакциями.
    """
    logging.info(f"Начало поиска по запросу: '{search_query}'")

    try:
        # Чтение данных из Excel-файла
        df = pd.read_excel(file_path)

        # Фильтрация транзакций с использованием лямбда-функции
        filtered_transactions = df[
            df.apply(
                lambda row: search_query.lower() in str(row["Описание"]).lower()
                or search_query.lower() in str(row["Категория"]).lower(),
                axis=1,
            )
        ]

        # Преобразование в список словарей
        result = filtered_transactions.to_dict(orient="records")

        # Сериализация в JSON-строку
        json_result = json.dumps(result, ensure_ascii=False, indent=4)

        logging.info(f"Поиск завершен. Найдено {len(result)} транзакций.")
        return json_result

    except FileNotFoundError:
        logging.error(f"Файл {file_path} не найден.")
        return json.dumps([], ensure_ascii=False, indent=4)
    except KeyError as e:
        logging.error(f"Ошибка в структуре файла: отсутствует столбец {e}.")
        return json.dumps([], ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return json.dumps([], ensure_ascii=False, indent=4)
