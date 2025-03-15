import json
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Доброе утро!"
    elif 12 <= hour < 18:
        return "Добрый день!"
    elif 18 <= hour < 23:
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


def get_transactions_for_month(file_path: str, target_date_str: str) -> pd.DataFrame:
    """
    Фильтрует транзакции с начала месяца по указанную дату.

    :param file_path: Путь к Excel-файлу с транзакциями.
    :param target_date_str: Дата, до которой нужно фильтровать транзакции (в формате 'YYYY-MM-DD').
    :return: Отфильтрованный DataFrame с транзакциями.
    """
    # Чтение данных из Excel
    df = pd.read_excel(file_path)

    # Преобразуем столбец 'Дата операции' в формат datetime (без времени)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S").dt.date

    # Преобразуем target_date_str в объект date
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()

    # Определяем начало месяца
    start_of_month = target_date.replace(day=1)

    # Фильтруем транзакции с начала месяца по указанную дату
    filtered_df = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= target_date)]

    return filtered_df


def get_currency_rates(user_currencies: List) -> List[Dict]:
    """
    Возвращает текущие курсы валют.
    """
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise ValueError("Ошибка: API_KEY не найден в .env")

    currency_rates = []

    for currency in user_currencies:
        url = (
            f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency}"
            f"&to_currency=RUB&apikey={API_KEY}"
        )
        response = requests.get(url)
        data = response.json()

        if "Realtime Currency Exchange Rate" in data:
            rate = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
            if rate:
                response_dict = {"currency": currency, "rate": float(rate)}
                currency_rates.append(response_dict)
        else:
            pass

    return currency_rates


def get_stock_prices(user_stocks: Dict) -> List[Dict]:
    """
    Возвращает текущие цены на акции.
    """
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise ValueError("Ошибка: API_KEY не найден в .env")

    stock_prices = []

    for stock in user_stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "Global Quote" in data:
            price = data["Global Quote"]["05. price"]
            if price:
                response_dict = {"stock": stock, "price": float(price)}
                stock_prices.append(response_dict)
        else:
            pass

    return stock_prices


def load_user_settings(user_settings_file: str) -> Any:
    """
    Загружает пользовательские настройки из user_settings.json.
    """
    with open(user_settings_file) as f:
        data = json.load(f)
    return data


def calculate_cashback(total_spent: float) -> float:
    """
    Вычисляет кешбэк (1 рубль на каждые 100 рублей).
    """
    return total_spent / 100
