import datetime
import logging
from typing import Any, Callable, Optional

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


def save_report(func: Optional[Callable] = None, filename: Optional[str] = None) -> Callable:
    """
    Декоратор для сохранения отчёта (DataFrame) в JSON-файл.
    - Если filename не передан, используется имя по умолчанию.
    - Если передан, сохраняем результат в указанный файл.
    """

    def decorator_report(func: Callable) -> Callable:
        def wrapper_report(*args: Any, **kwargs: Any) -> pd.DataFrame:
            # Вызываем исходную функцию, получаем DataFrame
            df_result: pd.DataFrame = func(*args, **kwargs)

            # Если не задано имя файла, используем имя по умолчанию
            output_file: str = filename or "default_report.json"

            # Сохраняем DataFrame в JSON
            df_result.to_json(output_file, orient="records", force_ascii=False, date_format="iso")
            logging.info(f"Отчёт сохранён в файл: {output_file}")

            # Возвращаем DataFrame дальше по коду
            return df_result

        return wrapper_report

    # Если декоратор вызывается без параметров: @save_report
    if func:
        return decorator_report(func)
    # Если декоратор вызывается с параметрами: @save_report(filename="...")
    return decorator_report


@save_report  # Можно также использовать @save_report(filename="my_report.json")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Фильтрует транзакции по категории за последние 3 месяца от указанной даты,
    возвращает только «траты».

    Параметры:
        transactions (pd.DataFrame): DataFrame с колонками:
            'Категория', 'Сумма операции', 'Дата платежа'.
        category (str): Категория для фильтрации.
        date (str, optional): Дата в формате 'YYYY-MM-DD'. По умолчанию — текущая дата.

    Возвращает:
        pd.DataFrame: DataFrame с отфильтрованными транзакциями.
    """
    # Если дата не передана, берем текущую
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Преобразуем строку в дату
    date_dt: pd.Timestamp = pd.to_datetime(date)

    logging.info(f"Фильтрация транзакций по категории: '{category}', дата: {date_dt}")

    # Дата три месяца назад
    three_months_ago: pd.Timestamp = date_dt - pd.DateOffset(months=3)
    logging.info(f"Диапазон фильтрации: с {three_months_ago.date()} по {date_dt.date()}")

    # Убеждаемся, что 'Дата платежа' имеет тип datetime
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y", errors="coerce")

    # Фильтруем:
    # 1. Категория (без учёта регистра)
    # 2. Дата в интервале [three_months_ago, date_dt]
    # 3. «Траты» => Сумма операции < 0
    filtered_data: pd.DataFrame = transactions[
        (transactions["Категория"].str.lower() == category.lower())
        & (transactions["Дата платежа"] >= three_months_ago)
        & (transactions["Дата платежа"] <= date_dt)
        & (transactions["Сумма операции"] < 0)
    ]

    logging.info(f"Найдено {len(filtered_data)} транзакций для категории '{category}'")

    # Преобразуем дату в удобный формат (YYYY-MM-DD) для вывода
    filtered_data["Дата платежа"] = filtered_data["Дата платежа"].dt.strftime("%Y-%m-%d")

    logging.info(f"Отчет сгенерирован для категории '{category}'")

    # Возвращаем именно DataFrame
    return filtered_data[["Категория", "Сумма операции", "Дата платежа"]]
