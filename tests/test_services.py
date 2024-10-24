import json

from moneyscope.services import top_3_cashback_categories


def test_top_3_cashback_categories_with_data(operations_data_list: list) -> None:
    # Тест с данными
    result = top_3_cashback_categories(operations_data_list, 2021, 12)

    # Проверяем, что результат — это валидный JSON
    parsed_result = json.loads(result)

    # Ожидаемый результат (только за декабрь)
    expected_result = {
        "Супермаркеты": 55,  # Суммируем кешбэк для Супермаркетов (30 + 25)
        "Аптеки": 15,  # Кэшбэк для Аптек
    }

    # Проверяем, что результат содержит правильные категории и суммы
    assert parsed_result == expected_result


def test_top_3_cashback_categories_no_data_for_month(operations_data_list: list) -> None:
    # Тест для месяца, в котором нет данных с кешбэком
    result = top_3_cashback_categories(operations_data_list, 2021, 9)

    # Проверяем, что результат — это валидный JSON
    parsed_result = json.loads(result)

    # Проверяем, что в результате ошибка
    assert "error" in parsed_result
    assert parsed_result["error"] == "Нет операций с кешбэком за 2021-9"


def test_top_3_cashback_categories_with_empty_data(empty_operations_data_list: list) -> None:
    # Тест с пустыми данными
    result = top_3_cashback_categories(empty_operations_data_list, 2021, 12)

    # Проверяем, что результат — это валидный JSON
    parsed_result = json.loads(result)

    # Проверяем, что в результате ошибка
    assert "error" in parsed_result
    assert parsed_result["error"] == "Нет данных для анализа кешбэка"
