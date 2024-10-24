import json
from datetime import datetime

from moneyscope.logger_config import logger
from moneyscope.utils import (
    aggregate_card_data,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    read_operations,
)


def get_main_page(time_str: str) -> str:
    """Функция для подготовки данных для Главной страницы.
    Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    Возвращает JSON-ответ с необходимыми данными"""
    operations = read_operations()
    try:
        logger.info(f"Операции после чтения: {operations.head()}")  # Логируем первые строки для проверки
        date_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        start_of_month = datetime(date_time.year, date_time.month, 1)

        if operations.empty:
            logger.warning("DataFrame пустой. Операции не найдены.")
            return json.dumps({"error": "Нет операций для обработки"}, ensure_ascii=False, indent=4)

        operations_for_period = operations[
            (operations["Дата операции"] >= start_of_month) & (operations["Дата операции"] <= date_time)
        ]

        logger.info(f"Операции за указанный период: {operations_for_period}")  # Логируем после фильтрации

        if operations_for_period.empty:
            logger.warning("Операции за указанный период не найдены.")
            return json.dumps({"error": "Нет операций за указанный период"}, ensure_ascii=False, indent=4)

        result = {
            "greeting": get_greeting(),
            "cards": aggregate_card_data(operations_for_period),
            "top_transactions": get_top_transactions(operations_for_period),
            "currency_rates": get_currency_rates(),
            "stock_prices": get_stock_prices(),
        }

        logger.info("Данные для главной страницы успешно сформированы")
        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка в функции get_main_page: {str(e)}")
        return json.dumps(
            {"error": "Не удалось сформировать данные для главной страницы"}, ensure_ascii=False, indent=4
        )
