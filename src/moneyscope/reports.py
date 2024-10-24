import functools
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd
from dotenv import load_dotenv

from moneyscope.logger_config import logger

load_dotenv()
report_files_dir = Path(str(os.getenv("REPORT_FILES_DIR")))


def save_report_to_file(filename: Optional[str] = "") -> Callable[..., Any]:
    """Декоратор для сохранения отчёта в файл.
    Файлы сохраняются в папке, путь к которой хранится в переменной REPORT_FILES_DIR.
    Если в декоратор не передавать наименование файла, он подставит имя функции с расширением json
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Выполняем функцию и получаем результат
            result = func(*args, **kwargs)

            # Записываем результат в файл в формате JSON
            nonlocal filename
            if not filename:
                filename = func.__name__ + ".json"
            report_file = report_files_dir / filename

            result.to_json(
                report_file, orient="records", date_format="iso", date_unit="s", force_ascii=False, indent=4
            )
            return result

        return wrapper

    return decorator


@save_report_to_file("spending_by_category.json")
def spending_by_category(transactions: pd.DataFrame, category: str, date_string: Optional[str] = "") -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца от переданной даты,
    либо от текущей, если дата не передана"""

    try:
        # Если дата не передана, используем текущую дату
        if not date_string:
            end_date = datetime.now()
            logger.info(f"Дата не передана, используется текущая дата: {end_date}")
        else:
            end_date = pd.to_datetime(date_string, format="%d.%m.%Y")
            logger.info(f"Используемая дата: {end_date}")

        # Вычисляем дату три месяца назад
        start_date = end_date - pd.DateOffset(months=3)
        logger.info(f"Начало периода: {start_date}, конец периода: {end_date}")

        # Увеличиваем конечную дату на один день минус одна секунда, чтобы включить конец последнего дня
        end_date = end_date + pd.DateOffset(days=1) - pd.Timedelta(seconds=1)

        # Фильтрация данных по категории и дате
        filtered_transactions = transactions[
            (transactions["Категория"] == category)
            & (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= end_date)
        ]

        logger.info(f"Найдено {len(filtered_transactions)} транзакций по категории '{category}' за указанный период")

        # Возвращаем отфильтрованные данные
        return filtered_transactions
    except Exception as e:
        # Логгируем любые ошибки, которые могут возникнуть
        logger.error(f"Ошибка в функции spending_by_category: {str(e)}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame в случае ошибки
