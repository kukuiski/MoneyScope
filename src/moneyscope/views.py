import json
from datetime import datetime

import pandas as pd

from moneyscope.logger_config import logger
from moneyscope.utils import get_currency_rates, get_stock_prices, get_top_transactions


def get_greeting() -> str:
    # Получить текущее время
    current_hour = datetime.now().hour

    if 6 <= current_hour < 12:
        greeting = "Доброе утро"
    elif 12 <= current_hour < 18:
        greeting = "Добрый день"
    elif 18 <= current_hour < 22:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    return greeting


def aggregate_card_data(df: pd.DataFrame) -> list:
    """Получаем агрегированные (сводные) данные по картам:
    последние 4 цифры карты; общая сумма расходов; кешбэк."""

    # Убираем строки без номера карты
    df = df.dropna(subset=["Номер карты"]).copy()

    # Создаем новый столбец с последними 4 цифрами карты
    df.loc[:, "last_digits"] = df["Номер карты"].str[-4:]

    # Оставляем только расходы (минусовые операции)
    df = df[df["Сумма операции"] < 0]

    # Группируем по последним 4 цифрам карты и агрегируем данные
    grouped_df = (
        df.groupby("last_digits")
        .agg(
            total_spent=pd.NamedAgg(column="Сумма операции", aggfunc=lambda x: -x.sum()),
            cashback=pd.NamedAgg(column="Кэшбэк", aggfunc="sum"),
        )
        .reset_index()
    )

    # Преобразуем результат в список словарей
    result = grouped_df.to_dict(orient="records")

    return result


def get_main_page(operations: pd.DataFrame, time_str: str) -> str:
    """Функция для подготовки данных для Главной страницы.
    Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    Возвращает JSON-ответ с необходимыми данными"""
    try:
        date_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        start_of_month = datetime(date_time.year, date_time.month, 1)

        logger.info(f"Получены операции: {operations}")  # Логируем данные до фильтрации

        if operations.empty:
            logger.warning("DataFrame пустой. Операции не найдены.")
            return json.dumps({"error": "Нет операций для обработки"}, ensure_ascii=False, indent=4)

        operations_for_period = operations[
            (operations["Дата операции"] >= start_of_month) & (operations["Дата операции"] <= date_time)
        ]

        logger.info(f"Операции после фильтрации: {operations_for_period}")  # Логируем данные после фильтрации

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
