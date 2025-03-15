import json
import os
import sys
import unittest
from typing import Any
from unittest.mock import patch

import pandas as pd

from src.services import simple_search

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


class TestSimpleSearch(unittest.TestCase):

    @patch("pandas.read_excel")
    def test_simple_search_found(self, mock_read_excel: Any) -> None:
        # Создаем мок DataFrame
        mock_data = pd.DataFrame(
            {
                "Описание": ["Покупка продуктов", "Оплата интернета", "Покупка книг"],
                "Категория": ["Еда", "Интернет", "Книги"],
            }
        )
        mock_read_excel.return_value = mock_data

        # Вызываем функцию с тестовым запросом
        result = simple_search("dummy_path.xlsx", "Покупка")

        # Проверяем результат
        expected_result = [
            {"Описание": "Покупка продуктов", "Категория": "Еда"},
            {"Описание": "Покупка книг", "Категория": "Книги"},
        ]
        self.assertEqual(json.loads(result), expected_result)

    @patch("pandas.read_excel")
    def test_simple_search_not_found(self, mock_read_excel: Any) -> None:
        # Создаем мок DataFrame
        mock_data = pd.DataFrame(
            {"Описание": ["Оплата интернета", "Оплата телефона"], "Категория": ["Интернет", "Телефон"]}
        )
        mock_read_excel.return_value = mock_data

        # Вызываем функцию с тестовым запросом
        result = simple_search("dummy_path.xlsx", "Книги")

        # Проверяем результат
        self.assertEqual(json.loads(result), [])

    @patch("pandas.read_excel")
    def test_simple_search_file_not_found(self, mock_read_excel: Any) -> None:
        # Мокируем исключение FileNotFoundError
        mock_read_excel.side_effect = FileNotFoundError

        # Вызываем функцию
        result = simple_search("nonexistent_path.xlsx", "Покупка")

        # Проверяем результат
        self.assertEqual(json.loads(result), [])

    @patch("pandas.read_excel")
    def test_simple_search_key_error(self, mock_read_excel: Any) -> None:
        # Создаем мок DataFrame с отсутствующим столбцом
        mock_data = pd.DataFrame(
            {"Description": ["Покупка продуктов", "Оплата интернета"], "Category": ["Еда", "Интернет"]}
        )
        mock_read_excel.return_value = mock_data

        # Вызываем функцию
        result = simple_search("dummy_path.xlsx", "Покупка")

        # Проверяем результат
        self.assertEqual(json.loads(result), [])

    @patch("pandas.read_excel")
    def test_simple_search_general_exception(self, mock_read_excel: Any) -> None:
        # Мокируем общее исключение
        mock_read_excel.side_effect = Exception("Some error")

        # Вызываем функцию
        result = simple_search("dummy_path.xlsx", "Покупка")

        # Проверяем результат
        self.assertEqual(json.loads(result), [])
