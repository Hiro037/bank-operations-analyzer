import os
import sys
from unittest.mock import patch

import pandas as pd

from src.views import generate_home_page_response, get_card_summary, get_top_transactions

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


# Фиктивные данные для тестов
def create_test_transactions() -> pd.DataFrame:
    data = {
        "Номер карты": ["*7197", "*7197", "*5091", "*5091", None],
        "Сумма операции": [-160.89, -64.00, -564.00, -7.07, -800.00],
        "Категория": ["Супермаркеты", "Супермаркеты", "Различные товары", "Каршеринг", "Переводы"],
        "Описание": ["Колхоз", "Колхоз", "Ozon.ru", "Ситидрайв", "Константин Л."],
        "Дата операции": ["2021-12-31", "2021-12-31", "2021-12-31", "2021-12-31", "2021-12-31"],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    return df


# Тесты для get_card_summary
def test_get_card_summary() -> None:
    df = create_test_transactions()
    result = get_card_summary(df)
    assert len(result) == 2
    assert result[0]["last_digits"] == "7197"
    assert result[0]["total_spent"] == 224.89
    assert result[0]["cashback"] == 2.25
    assert result[1]["last_digits"] == "5091"
    assert result[1]["total_spent"] == 571.07
    assert result[1]["cashback"] == 5.71


# Тесты для get_top_transactions
def test_get_top_transactions() -> None:
    df = create_test_transactions()
    result = get_top_transactions(df, n=3)
    assert len(result) == 3
    assert result[0]["amount"] == -7.07
    assert result[1]["amount"] == -64.0
    assert result[2]["amount"] == -160.89


# Тесты для generate_home_page_response
def test_generate_home_page_response() -> None:
    # Мокируем функции
    with patch("src.views.get_greeting", return_value="Добрый день!"), patch(
        "src.views.get_transactions_for_month", return_value=create_test_transactions()
    ), patch(
        "src.views.load_user_settings", return_value={"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    ), patch(
        "src.views.get_currency_rates", return_value=[{"currency": "USD", "rate": 73.21}]
    ), patch(
        "src.views.get_stock_prices", return_value=[{"stock": "AAPL", "price": 150.12}]
    ):

        # Вызываем функцию
        response = generate_home_page_response("dummy_path", "2021-12-31", "dummy_settings.json")

        # Проверяем результат
        assert response["greeting"] == "Добрый день!"
        assert len(response["cards"]) == 2
        assert len(response["top_transactions"]) == 5
        assert response["currency_rates"] == [{"currency": "USD", "rate": 73.21}]
        assert response["stock_prices"] == [{"stock": "AAPL", "price": 150.12}]
