import json

import pandas as pd

from moneyscope.logger_config import logger


def top_3_cashback_categories(data: list, year: int, month: int) -> str:
    """Функция для анализа выгодности категорий повышенного кешбэка."""
    try:
        if not data:
            logger.warning("Список пуст. Операции отсутствуют.")
            return json.dumps({"error": "Нет данных для анализа кешбэка"}, ensure_ascii=False, indent=4)

        # Преобразуем список словарей в DataFrame
        df = pd.DataFrame(data)

        # Преобразуем столбец "Дата операции" в формат datetime с дефисами
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%Y-%m-%d %H:%M:%S", errors="coerce")

        # Убедимся, что преобразование прошло успешно
        if df["Дата операции"].isnull().any():
            logger.error("Некорректные даты в данных операций.")
            return json.dumps({"error": "Некорректные данные в поле 'Дата операции'"}, ensure_ascii=False, indent=4)

        # Фильтрация по году, месяцу (используем поле "Дата операции") и положительному кешбэку
        filtered_df = df[
            (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month) & (df["Кэшбэк"] > 0)
        ]
        logger.info(f"Найдено {len(filtered_df)} операций с положительным кешбэком за указанный период")

        # Проверка, есть ли данные после фильтрации
        if filtered_df.empty:
            logger.warning(f"Нет операций с положительным кешбэком за {year}-{month}")
            return json.dumps({"error": f"Нет операций с кешбэком за {year}-{month}"}, ensure_ascii=False, indent=4)

        # Суммируем кешбэк по категориям
        cashback_by_category = filtered_df.groupby("Категория")["Кэшбэк"].sum().nlargest(3)

        # Преобразуем результат в JSON
        result = cashback_by_category.to_dict()
        logger.info("Результат успешно преобразован в JSON")
        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        # Логгируем любую ошибку
        logger.error(f"Ошибка в функции top_3_cashback_categories: {str(e)}")
        return json.dumps(
            {"error": "Произошла ошибка при расчёте топ-3 категорий кэшбэка"}, ensure_ascii=False, indent=4
        )
