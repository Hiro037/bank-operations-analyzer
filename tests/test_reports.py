import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
import pytest

from src.reports import spending_by_category

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


# Фикстура с тестовыми данными
@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Категория": ["Еда", "транспорт", "ЕДА", "Развлечения", "Еда"],
            "Сумма операции": [-100, -50, -200, 300, -150],
            "Дата платежа": [
                (datetime.now() - timedelta(days=10)).strftime("%d.%m.%Y"),  # В пределах 3 мес
                (datetime.now() - timedelta(days=100)).strftime("%d.%m.%Y"),  # За пределами
                (datetime.now() - timedelta(days=5)).strftime("%d.%m.%Y"),  # В пределах
                (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"),  # Положительная сумма
                # Исправленная дата для теста с date='2024-12-08':
                (datetime.strptime("2024-12-08", "%Y-%m-%d") - timedelta(days=1)).strftime("%d.%m.%Y"),  # 2024-12-07
            ],
        }
    )


TEST_CASES: List[tuple[str, Optional[str], List[int]]] = [
    ("еда", None, [0, 2]),  # Регистронезависимость
    ("ТРАНСПОРТ", None, []),  # Нет трат в категории
    ("Еда", "2024-12-08", [4]),  # Дата транзакции 07.12.2024 входит в диапазон
    ("Развлечения", None, []),  # Положительная сумма
]


@pytest.mark.parametrize("category, date, expected_indices", TEST_CASES)
def test_spending_by_category(
    sample_transactions: pd.DataFrame, category: str, date: Optional[str], expected_indices: List[int]
) -> None:
    result: pd.DataFrame = spending_by_category(sample_transactions, category, date)

    # Преобразуем ожидаемые даты в строки
    expected_data: pd.DataFrame = sample_transactions.iloc[expected_indices].copy()
    expected_data["Дата платежа"] = pd.to_datetime(expected_data["Дата платежа"], format="%d.%m.%Y").dt.strftime(
        "%Y-%m-%d"
    )

    # Сравниваем DataFrame
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        expected_data[["Категория", "Сумма операции", "Дата платежа"]].reset_index(drop=True),
        check_dtype=False,
    )


def test_empty_dataframe() -> None:
    empty_df: pd.DataFrame = pd.DataFrame(columns=["Категория", "Сумма операции", "Дата платежа"])
    result: pd.DataFrame = spending_by_category(empty_df, "Еда")
    assert result.empty


def test_invalid_dates(sample_transactions: pd.DataFrame) -> None:
    # Дата в неверном формате
    with pytest.raises(ValueError):
        spending_by_category(sample_transactions, "Еда", "2023-13-01")

    # Некорректная дата в DataFrame
    invalid_df: pd.DataFrame = sample_transactions.copy()
    invalid_df.at[0, "Дата платежа"] = "32.01.2023"
    result: pd.DataFrame = spending_by_category(invalid_df, "Еда")
    assert len(result) < len(sample_transactions)  # Некорректные даты должны отфильтровываться
