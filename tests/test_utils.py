import os
import sys
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.utils import (calculate_cashback, get_currency_rates, get_greeting,
                       get_stock_prices, get_transactions_for_month,
                       load_user_settings)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


# ---------- Тест для get_greeting ----------
def test_get_greeting():
    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 3, 15, 9)  # Утро
        assert get_greeting() == "Доброе утро!"

        mock_datetime.now.return_value = datetime(2024, 3, 15, 14)  # День
        assert get_greeting() == "Добрый день!"

        mock_datetime.now.return_value = datetime(2024, 3, 15, 20)  # Вечер
        assert get_greeting() == "Добрый вечер!"

        mock_datetime.now.return_value = datetime(2024, 3, 15, 2)  # Ночь
        assert get_greeting() == "Доброй ночи!"


# ---------- Тест для get_transactions_for_month ----------
@pytest.fixture
def sample_transactions():
    return pd.DataFrame({
        "Дата операции": ["01.12.2021 12:30:00", "15.12.2021 14:00:00", "05.11.2021 10:20:00"],
        "Сумма операции": [-500, -200, -1500]
    })


@patch("utils.pd.read_excel")
def test_get_transactions_for_month(mock_read_excel, sample_transactions):
    mock_read_excel.return_value = sample_transactions

    result = get_transactions_for_month("fake_path.xlsx", "2021-12-31")

    assert len(result) == 2  # Только транзакции за декабрь 2021
    assert result.iloc[0]["Сумма операции"] == -500
    assert result.iloc[1]["Сумма операции"] == -200


# ---------- Тест для get_currency_rates ----------
@patch("utils.requests.get")
@patch("utils.os.getenv", return_value="fake_api_key")
def test_get_currency_rates(mock_getenv, mock_requests_get):
    mock_response = {
        "Realtime Currency Exchange Rate": {"5. Exchange Rate": "75.5"}
    }
    mock_requests_get.return_value.json.return_value = mock_response

    result = get_currency_rates(["USD"])

    assert len(result) == 1
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] == 75.5


# ---------- Тест для get_stock_prices ----------
@patch("utils.requests.get")
@patch("utils.os.getenv", return_value="fake_api_key")
def test_get_stock_prices(mock_getenv, mock_requests_get):
    mock_response = {
        "Global Quote": {"05. price": "145.3"}
    }
    mock_requests_get.return_value.json.return_value = mock_response

    result = get_stock_prices(["AAPL"])

    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 145.3


# ---------- Тест для load_user_settings ----------
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}')
def test_load_user_settings(mock_file):
    result = load_user_settings("fake_path.json")

    assert result["user_currencies"] == ["USD"]
    assert result["user_stocks"] == ["AAPL"]


# ---------- Тест для calculate_cashback ----------
@pytest.mark.parametrize("spent, expected", [
    (100, 1.0),
    (250, 2.5),
    (0, 0.0),
    (999, 9.99)
])
def test_calculate_cashback(spent, expected):
    assert calculate_cashback(spent) == expected
