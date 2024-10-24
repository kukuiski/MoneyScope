import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

import pandas as pd
import requests
from dotenv import load_dotenv

from moneyscope.logger_config import logger

# Читаем переменную с путём к operations.xlsx и загружаем путь
load_dotenv()
xlsx_path = Path(str(os.getenv("DATA_PATH")))
user_settings_path = Path(str(os.getenv("USER_SETTINGS_PATH")))
fmp_api_url = os.getenv("FMP_API_URL")
fmp_api_key = os.getenv("FMP_API_KEY")


def read_operations() -> pd.DataFrame:
    """Функция для чтения списка операций из XLSX-файла с основными проверками"""
    required_columns = {
        "Дата операции",
        "Дата платежа",
        "Сумма платежа",
        "Категория",
        "Описание",
        "Кэшбэк",
        "Сумма операции",
        "Номер карты",
    }
    try:
        # Попытка прочитать Excel-файл
        df = pd.read_excel(xlsx_path, parse_dates=False)
        logger.info(f"Файл {xlsx_path} успешно прочитан")

        # Проверяем наличие необходимых столбцов
        if not required_columns.issubset(df.columns):
            missing_columns = required_columns - set(df.columns)
            raise ValueError(f"Отсутствуют обязательные столбцы: {', '.join(missing_columns)}")

        # Преобразуем столбцы "Дата операции" и "Дата платежа" в datetime
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y", errors="coerce")
        logger.info("Даты успешно преобразованы в формат datetime")

    except ValueError as ve:
        # Логгируем ошибку отсутствия столбцов
        logger.error(f"Ошибка структуры файла {xlsx_path}: {str(ve)}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame при ошибке структуры

    except Exception as e:
        # Логгируем любую ошибку, которая произошла
        logger.error(f"Ошибка при обработке файла {xlsx_path}: {str(e)}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame при любой ошибке

    return df


def get_top_transactions(transactions: pd.DataFrame, number: int = 5) -> list:
    """Функция возвращает топ-5 транзакций по модулю суммы платежа"""

    # Проверяем, что DataFrame не пуст
    if transactions.empty:
        return []

    # Создаём копию объекта DataFrame
    transactions = transactions.copy()

    # Преобразуем столбец 'Сумма платежа' в абсолютные значения
    transactions.loc[:, "abs_amount"] = transactions["Сумма платежа"].abs()

    # Сортируем по абсолютной сумме и выбираем топ-5 транзакций
    top_transactions = transactions.sort_values(by="abs_amount", ascending=False).head(number)

    # Формируем список словарей с необходимыми данными
    result = top_transactions.apply(
        lambda row: {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": row["Сумма платежа"],
            "category": row["Категория"],
            "description": row["Описание"],
        },
        axis=1,
    ).tolist()

    return result


def load_user_settings() -> Dict:
    """Читает настройки из JSON файла и возвращает словарь"""
    try:
        with open(user_settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        if isinstance(settings, dict):
            logger.info("Настройки успешно загружены")
            return settings
        else:
            logger.error("Загруженные данные не являются словарем")
            return {}
    except Exception as e:
        logger.error(f"Ошибка при загрузке пользовательских настроек: {str(e)}")
        return {}


def get_currency_rates() -> list:
    """Получает курсы валют по отношению к рублю через API financialmodelingprep.com"""
    # Загружаем список валют из настроек
    currencies = load_user_settings().get("user_currencies")
    if not currencies:
        return []

    rates = []

    # Шаг 2: Запрашиваем курсы валют для каждой пары
    for currency in currencies:
        pair = currency + "RUB"
        url = f"{fmp_api_url}{pair}?apikey={fmp_api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data:
                rate = {"currency": currency, "rate": data[0]["price"]}  # Берём цену из ответа
                rates.append(rate)
        except requests.RequestException:
            continue

    return rates


def get_stock_prices() -> list:
    """Получает стоимость акций через API financialmodelingprep.com"""
    # Загружаем список символов акций из настроек
    stock_symbols = load_user_settings().get("user_stocks")
    if not stock_symbols:
        return []

    prices = []

    # Шаг 2: Запрашиваем курсы валют для каждой пары
    for stock in stock_symbols:
        url = f"{fmp_api_url}{stock}?apikey={fmp_api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data:
                price = {"stock": stock, "price": data[0]["price"]}  # Берём цену из ответа
                prices.append(price)
        except requests.RequestException:
            continue

    return prices


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
