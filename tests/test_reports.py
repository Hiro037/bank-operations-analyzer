import json
import os
import sys

import pandas as pd
import pytest

from src.reports import spending_by_category

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


# Фикстура для создания тестового DataFrame
@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    data = {
        "Категория": ["Фастфуд", "Фастфуд", "Продукты", "Транспорт", "Фастфуд"],
        "Сумма операции": [100, 200, 300, 400, 500],
        "Дата платежа": ["01.10.2021", "15.11.2021", "01.12.2021", "01.01.2022", "31.12.2021"],
    }
    df = pd.DataFrame(data)

    # Преобразуем колонку 'Дата платежа' в datetime
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y")

    # Отладочная информация
    print("Данные в sample_transactions:")
    print(df)

    return df


# Тест на корректность фильтрации по категории и дате
def test_spending_by_category_default_date(sample_transactions: pd.DataFrame) -> None:
    # Вызываем функцию
    result = spending_by_category(sample_transactions, "Фастфуд", "2021-12-31")

    # Ожидаемый результат (только транзакции за последние 3 месяца)
    expected_result = [
        {"Категория": "Фастфуд", "Сумма операции": 100, "Дата платежа": "2021-10-01"},
        {"Категория": "Фастфуд", "Сумма операции": 200, "Дата платежа": "2021-11-15"},
        {"Категория": "Фастфуд", "Сумма операции": 500, "Дата платежа": "2021-12-31"},
    ]

    # Проверяем результат
    assert json.loads(result) == expected_result


# Тест на случай, если категория не найдена
def test_spending_by_category_no_match(sample_transactions: pd.DataFrame) -> None:
    result = spending_by_category(sample_transactions, "Развлечения", "2021-12-31")
    assert json.loads(result) == []


# Тест на корректность обработки даты в формате строки
def test_spending_by_category_date_string(sample_transactions: pd.DataFrame) -> None:
    result = spending_by_category(sample_transactions, "Фастфуд", "2021-12-31")
    expected_result = [
        {"Категория": "Фастфуд", "Сумма операции": 100, "Дата платежа": "2021-10-01"},
        {"Категория": "Фастфуд", "Сумма операции": 200, "Дата платежа": "2021-11-15"},
        {"Категория": "Фастфуд", "Сумма операции": 500, "Дата платежа": "2021-12-31"},
    ]
    assert json.loads(result) == expected_result


# Тест на корректность обработки пустого DataFrame
def test_spending_by_category_empty_dataframe() -> None:
    empty_df = pd.DataFrame(columns=["Категория", "Сумма операции", "Дата платежа"])
    result = spending_by_category(empty_df, "Фастфуд", "2021-12-31")
    assert json.loads(result) == []
