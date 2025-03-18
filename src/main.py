import json
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from src.reports import spending_by_category
from src.services import simple_search
from src.views import generate_home_page_response


def display_menu() -> str:
    """Выводит интерактивное меню."""
    print("\n" + "=" * 40)
    print("Банковский анализатор операций")
    print("=" * 40)
    print("1. Главная страница")
    print("2. Поиск транзакций")
    print("3. Отчет по категориям")
    print("4. Выход")
    return input("Выберите действие (1-4): ")


def get_common_input() -> tuple[str, str]:
    """Запрашивает общие параметры для всех команд."""
    transactions_file: str = input("Введите путь к файлу транзакций (Excel): ").strip()
    settings_file: str = (
        input("Введите путь к файлу настроек [по умолчанию: user_settings.json]: ").strip() or "user_settings.json"
    )
    return transactions_file, settings_file


def run_home_page() -> None:
    """Запускает генерацию главной страницы."""
    transactions_file, settings_file = get_common_input()
    target_date: str = input("Введите дату (YYYY-MM-DD) [по умолчанию: сегодня]: ").strip() or datetime.now().strftime(
        "%Y-%m-%d"
    )

    try:
        result: Dict[str, Any] = generate_home_page_response(
            file_path=transactions_file, date_time_str=target_date, user_settings_file=settings_file
        )
        print("\nРезультат:")
        print(json.dumps(result, ensure_ascii=False, indent=4))
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def run_search() -> None:
    """Запускает поиск транзакций."""
    transactions_file, _ = get_common_input()
    search_query: str = input("Введите поисковый запрос: ").strip()
    transactions: pd.DataFrame = pd.read_excel(transactions_file)
    transactions_as_dict: List = transactions.to_dict(orient="records")

    try:
        result: str = simple_search(transactions_as_dict, search_query)
        print("\nНайденные транзакции:")
        print(result)
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def run_report() -> None:
    """Запускает отчет по категориям."""
    transactions_file, _ = get_common_input()
    category: str = input("Введите категорию (например, 'Фастфуд'): ").strip()
    target_date: str = input(
        "Введите дату отчета (YYYY-MM-DД) [по умолчанию: сегодня]: "
    ).strip() or datetime.now().strftime("%Y-%m-%d")

    try:
        df: pd.DataFrame = pd.read_excel(transactions_file)
        result: pd.DataFrame = spending_by_category(df, category, target_date)
        print("\nОтчет по категории:")
        print(result)
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def main() -> None:
    """Основной цикл программы."""
    while True:
        choice: str = display_menu()

        if choice == "1":
            run_home_page()
        elif choice == "2":
            run_search()
        elif choice == "3":
            run_report()
        elif choice == "4":
            print("До свидания!")
            break
        else:
            print("Неверный ввод. Попробуйте снова.")


if __name__ == "__main__":
    main()
