import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def simple_search(transactions: list, search_query: str) -> str:
    """
    Возвращает JSON-ответ с транзакциями, содержащими запрос в описании или категории.

    :param transactions: Список транзакций в формате списка словарей.
    :param search_query: Строка для поиска.
    :return: JSON-строка с найденными транзакциями.
    """
    logging.info(f"Начало поиска по запросу: '{search_query}'")

    try:
        # Фильтрация транзакций с использованием функции filter и лямбда-функции
        filtered_transactions = list(
            filter(
                lambda t: search_query.lower() in str(t.get("Описание", "")).lower()
                or search_query.lower() in str(t.get("Категория", "")).lower(),
                transactions,
            )
        )

        # Сериализация результата в JSON-строку
        json_result = json.dumps(filtered_transactions, ensure_ascii=False, indent=4)

        logging.info(f"Поиск завершен. Найдено {len(filtered_transactions)} транзакций.")
        return json_result

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return json.dumps([], ensure_ascii=False, indent=4)
