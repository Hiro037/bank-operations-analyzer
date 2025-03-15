import datetime
import logging
from typing import Any

import pandas as pd

# Настроим логирование
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


def spending_by_category(transactions: pd.DataFrame, category: str, date: Any = None) -> Any:
    # Если дата не передана, берем текущую дату
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Преобразуем строку в дату с помощью pandas
    date = pd.to_datetime(date)

    # Логируем начало выполнения функции
    logging.info(f"Фильтрация транзакций по категории: {category}, дата: {date}")

    # Фильтруем данные за последние 3 месяца
    three_months_ago = date - pd.DateOffset(months=3)

    # Логируем диапазон дат
    logging.info(f"Диапазон фильтрации: с {three_months_ago} по {date}")

    # Преобразуем колонку 'Дата платежа' в тип datetime
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")

    # Фильтруем данные
    filtered_data = transactions[
        # Преобразуем категорию в нижний регистр для сравнения
        (transactions["Категория"].str.lower() == category.lower())
        & (transactions["Дата платежа"] >= three_months_ago)  # Сравниваем с датой три месяца назад
        & (transactions["Дата платежа"] <= date)  # Сравниваем с конечной датой
    ]

    # Логируем количество найденных транзакций
    logging.info(f"Найдено {len(filtered_data)} транзакций для категории {category}")

    # Преобразуем 'Дата платежа' в строку с нужным форматом
    filtered_data["Дата платежа"] = filtered_data["Дата платежа"].dt.strftime("%Y-%m-%d")

    # Теперь преобразуем в JSON
    result_json = filtered_data[["Категория", "Сумма операции", "Дата платежа"]].to_json(
        orient="records", force_ascii=False
    )
    # Логируем завершение функции
    logging.info(f"Отчет сгенерирован для категории {category}")

    return result_json
