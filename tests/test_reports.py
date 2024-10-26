import pandas as pd

from moneyscope.reports import spending_by_category


def test_spending_by_category_with_data(operations_data: pd.DataFrame) -> None:
    # Тест с данными по категории "Ж/д билеты"
    result = spending_by_category(operations_data, "Ж/д билеты", "30.12.2021")

    # Ожидаемый результат
    expected_data = {
        "Дата операции": ["2021-12-29 22:32:24", "2021-12-29 22:28:47"],
        "Категория": ["Ж/д билеты", "Ж/д билеты"],
        "Сумма операции": [-1411.4, -1411.4],
    }

    expected_df = pd.DataFrame(expected_data)
    expected_df["Дата операции"] = pd.to_datetime(expected_df["Дата операции"])

    # Сравниваем только нужные столбцы
    result = result[["Дата операции", "Категория", "Сумма операции"]]

    # Сравниваем DataFrame
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df)


def test_spending_by_category_no_data_for_category(operations_data: pd.DataFrame) -> None:
    # Тест для категории, которая не присутствует в данных ("Одежда")
    result = spending_by_category(operations_data, "Одежда", "30.12.2021")

    # Проверяем, что результат — это пустой DataFrame
    assert result.empty


def test_spending_by_category_no_data_in_period(operations_data: pd.DataFrame) -> None:
    # Тест для категории "Фастфуд", но за период, где нет транзакций (более 3 месяцев назад)
    result = spending_by_category(operations_data, "Фастфуд", "01.01.2021")

    # Проверяем, что результат — это пустой DataFrame
    assert result.empty


def test_spending_by_category_with_empty_data(empty_operations_data: pd.DataFrame) -> None:
    # Тест с пустыми данными
    result = spending_by_category(empty_operations_data, "Супермаркеты", "30.12.2021")

    # Проверяем, что результат — это пустой DataFrame
    assert result.empty
