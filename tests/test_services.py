import json
import os
import sys
from typing import Any, Dict, List

import pytest

from src.services import simple_search

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Тестовые данные
SAMPLE_TRANSACTIONS: List[Dict[str, Any]] = [
    {"Описание": "Покупка еды", "Категория": "Продукты"},
    {"Описание": "Такси", "Категория": "Транспорт"},
    {"Описание": "Кино", "Категория": "Развлечения"},
    {"Категория": "Еда"},  # Тест на отсутствие "Описание"
    {"Описание": "TEST", "Категория": "test"},  # Для проверки регистра
]

TEST_CASES: List[tuple[str, List[int]]] = [
    # (search_query, expected_indices)
    ("еды", [0]),  # Поиск по описанию (регистр)
    ("ТРАНСПОРТ", [1]),  # Поиск по категории (регистр)
    ("кино", [2]),  # Точное совпадение
    ("Еда", [3]),  # Совпадение в разных полях
    ("нет", []),  # Нет совпадений
    ("test", [4]),  # Регистронезависимость
    ("", list(range(5))),  # Пустой запрос → все транзакции
]


@pytest.mark.parametrize("search_query, expected_indices", TEST_CASES)
def test_simple_search(search_query: str, expected_indices: List[int]) -> None:
    # Вызов функции
    result: str = simple_search(SAMPLE_TRANSACTIONS, search_query)

    # Проверка результата
    expected_result: List[Dict[str, Any]] = [SAMPLE_TRANSACTIONS[i] for i in expected_indices]
    assert json.loads(result) == expected_result


def test_empty_transactions() -> None:
    # Пустой список транзакций
    result: str = simple_search([], "test")
    assert json.loads(result) == []


def test_invalid_transaction_structure() -> None:
    # Транзакции с некорректными полями
    transactions: List[Dict[str, Any]] = [{"WrongField": "value"}]
    result: str = simple_search(transactions, "test")
    assert json.loads(result) == []


def test_missing_fields() -> None:
    # Отсутствие обоих полей
    transactions: List[Dict[str, Any]] = [{"ДругоеПоле": "значение"}]
    result: str = simple_search(transactions, "test")
    assert json.loads(result) == []
