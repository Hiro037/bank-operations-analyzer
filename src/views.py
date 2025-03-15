from typing import Dict, List

import pandas as pd

from src.utils import (
    calculate_cashback,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_transactions_for_month,
    load_user_settings,
)


def get_card_summary(df: pd.DataFrame) -> List[Dict]:
    """
    Возвращает информацию по картам.

    :param df: DataFrame с транзакциями.
    :return: Список словарей с информацией по картам.
    """
    cards_summary = []

    # Уникальные номера карт
    unique_cards = df["Номер карты"].dropna().unique()

    for card in unique_cards:
        # Фильтруем транзакции по карте
        card_transactions = df[df["Номер карты"] == card]

        # Сумма расходов (только отрицательные операции)
        total_spent = card_transactions[card_transactions["Сумма операции"] < 0]["Сумма операции"].sum() * -1

        # Вычисляем кэшбэк
        cashback = calculate_cashback(total_spent)

        # Формируем информацию по карте
        card_info = {
            "last_digits": str(card)[-4:],  # Последние 4 цифры карты
            "total_spent": float(round(total_spent, 2)),  # Округляем до 2 знаков
            "cashback": float(round(cashback, 2)),  # Округляем до 2 знаков
        }

        # Добавляем информацию в список
        cards_summary.append(card_info)

    return cards_summary


def get_top_transactions(df: pd.DataFrame, n: int = 5) -> List[Dict]:
    """
    Возвращает топ-N транзакций по сумме платежа.

    :param df: DataFrame с транзакциями.
    :param n: Количество транзакций для возврата.
    :return: Список словарей с топ-N транзакциями.
    """
    # Сортируем транзакции по сумме операции (по убыванию)
    top_transactions = df.nlargest(n, "Сумма операции")

    # Формируем список словарей
    result = []
    for _, row in top_transactions.iterrows():
        transaction = {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": float(round(row["Сумма операции"], 2)),
            "category": row["Категория"],
            "description": row["Описание"],
        }
        result.append(transaction)

    return result


def generate_home_page_response(file_path: str, date_time_str: str, user_settings_file: str) -> Dict:
    """
    Генерирует JSON-ответ для страницы «Главная».

    :param file_path: Путь к Excel-файлу с транзакциями.
    :param date_time_str: Дата и время в формате 'YYYY-MM-DD'.
    :param user_settings_file: Путь к файлу с пользовательскими настройками.
    :return: JSON-ответ с данными для веб-страницы.
    """

    # Получаем приветствие
    greeting = get_greeting()

    # Фильтруем транзакции за текущий месяц
    transactions_df = get_transactions_for_month(file_path, date_time_str)

    # Получаем информацию по картам
    cards_summary = get_card_summary(transactions_df)

    # Получаем топ-5 транзакций
    top_transactions = get_top_transactions(transactions_df, n=5)

    # Загружаем пользовательские настройки
    try:
        user_settings = load_user_settings(user_settings_file)
    except FileNotFoundError:
        print(f"Ошибка: файл {user_settings_file} не найден.")
        user_settings = {"user_currencies": [], "user_stocks": []}
    user_currencies = user_settings.get("user_currencies", [])
    user_stocks = user_settings.get("user_stocks", [])

    # Получаем курсы валют
    currency_rates = get_currency_rates(user_currencies)

    # Получаем цены на акции
    stock_prices = get_stock_prices(user_stocks)

    # Формируем JSON-ответ
    response = {
        "greeting": greeting,
        "cards": cards_summary,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return response
