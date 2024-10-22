import json
from unittest.mock import patch
import pytest
import pandas as pd
from moneyscope.views import get_main_page


# Тест с параметризацией данных (с данными и без)
@pytest.mark.parametrize(
    "operations_fixture, expected_cards_len, expected_top_transactions_len, expected_greeting",
    [
        ("operations_data", 3, 5, "Доброй ночи"),  # Ожидаем 3 карты и 5 транзакций с кешбэком
        ("empty_operations_data", 0, 0, None),  # Ожидаем пустые карты и транзакции
    ],
)
def test_get_main_page_with_parametrization(
    request: pytest.FixtureRequest,
    operations_fixture: str,
    expected_cards_len: int,
    expected_top_transactions_len: int,
    expected_greeting: str
) -> None:
    # Получаем нужную фикстуру с данными
    operations_df: pd.DataFrame = request.getfixturevalue(operations_fixture)

    # Мокаем функции, которые возвращают данные, кроме read_operations
    with patch("moneyscope.views.get_currency_rates", return_value={"USD": 75.0}), patch(
        "moneyscope.views.get_stock_prices", return_value={"AAPL": 150.0}
    ), patch("moneyscope.views.get_greeting", return_value="Доброй ночи"):

        # Изменяем тестовую дату на подходящую из данных
        result = get_main_page(operations_df, "2021-12-30 19:07:35")

        # Проверяем, что результат — это валидный JSON
        parsed_result = json.loads(result)

        # Проверяем, если нет данных, должен быть ключ "error"
        if operations_fixture == "empty_operations_data":
            assert "error" in parsed_result
            assert parsed_result["error"] == "Нет операций для обработки"
        else:
            # Проверяем ключи в результате
            assert "greeting" in parsed_result
            assert "cards" in parsed_result
            assert "top_transactions" in parsed_result
            assert "currency_rates" in parsed_result
            assert "stock_prices" in parsed_result

            # Проверяем длину карт и транзакций
            assert len(parsed_result["cards"]) == expected_cards_len
            assert len(parsed_result["top_transactions"]) == expected_top_transactions_len

            # Проверяем приветствие
            assert parsed_result["greeting"] == expected_greeting
