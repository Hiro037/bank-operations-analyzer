import json
from datetime import datetime
import pandas as pd

from src.views import generate_home_page_response
from src.services import simple_search
from src.reports import spending_by_category
from src.utils import load_user_settings


def display_menu():
    """Выводит интерактивное меню."""
    print("\n" + "=" * 40)
    print("Банковский анализатор операций")
    print("=" * 40)
    print("1. Главная страница")
    print("2. Поиск транзакций")
    print("3. Отчет по категориям")
    print("4. Выход")
    return input("Выберите действие (1-4): ")


def get_common_input():
    """Запрашивает общие параметры для всех команд."""
    transactions_file = input("Введите путь к файлу транзакций (Excel): ").strip()
    settings_file = input(
        "Введите путь к файлу настроек [по умолчанию: user_settings.json]: ").strip() or "user_settings.json"
    return transactions_file, settings_file


def run_home_page():
    """Запускает генерацию главной страницы."""
    transactions_file, settings_file = get_common_input()
    target_date = input("Введите дату (YYYY-MM-DD) [по умолчанию: сегодня]: ").strip() or datetime.now().strftime(
        "%Y-%m-%d")

    try:
        result = generate_home_page_response(
            file_path=transactions_file,
            date_time_str=target_date,
            user_settings_file=settings_file
        )
        print("\nРезультат:")
        print(json.dumps(result, ensure_ascii=False, indent=4))
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def run_search():
    """Запускает поиск транзакций."""
    transactions_file, _ = get_common_input()
    search_query = input("Введите поисковый запрос: ").strip()

    try:
        result = simple_search(transactions_file, search_query)
        print("\nНайденные транзакции:")
        print(result)
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def run_report():
    """Запускает отчет по категориям."""
    transactions_file, _ = get_common_input()
    category = input("Введите категорию (например, 'Фастфуд'): ").strip()
    target_date = input(
        "Введите дату отчета (YYYY-MM-DД) [по умолчанию: сегодня]: ").strip() or datetime.now().strftime("%Y-%m-%d")

    try:
        df = pd.read_excel(transactions_file)
        result = spending_by_category(df, category, target_date)
        print("\nОтчет по категории:")
        print(result)
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def main():
    """Основной цикл программы."""
    while True:
        choice = display_menu()

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