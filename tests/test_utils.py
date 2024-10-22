import pandas as pd
from unittest.mock import mock_open
from moneyscope.utils import (
    read_operations,
    get_top_transactions,
    load_user_settings,
    get_currency_rates,
    get_stock_prices,
)


# Тест для функции read_operations
def test_read_operations(operations_data, mocker):
    # Мокаем чтение файла, чтобы использовать данные из фикстуры
    mocker.patch("pandas.read_excel", return_value=operations_data)

    result = read_operations()

    # Проверяем, что данные были корректно загружены
    pd.testing.assert_frame_equal(result.reset_index(drop=True), operations_data)


def test_read_operations_missing_columns(mocker):
    # Мокаем DataFrame без некоторых нужных столбцов
    mock_data = pd.DataFrame({
        "Дата операции": ["30.12.2021 17:50:17"],
        "Категория": ["Супермаркеты"],
    })
    mocker.patch("pandas.read_excel", return_value=mock_data)

    # Проверяем, что вернется пустой DataFrame из-за отсутствия столбцов
    result = read_operations()
    assert result.empty


# Тест для функции get_top_transactions с данными
def test_get_top_transactions_with_data(operations_data):
    # Получаем результат
    result = get_top_transactions(operations_data, 5)

    # Ожидаемый результат, отсортированный по абсолютной сумме платежа
    expected_result = [
        {
            "date": "30.12.2021",
            "amount": 174000.0,
            "category": "Пополнения",
            "description": "Пополнение через Газпромбанк"
        },
        {
            "date": "29.12.2021",
            "amount": -1411.4,
            "category": "Ж/д билеты",
            "description": "РЖД"
        },
        {
            "date": "29.12.2021",
            "amount": -1411.4,
            "category": "Ж/д билеты",
            "description": "РЖД"
        },
        {
            "date": "30.12.2021",
            "amount": -349.0,
            "category": "Канцтовары",
            "description": "Mitrankov M.V."
        },
        {
            "date": "29.12.2021",
            "amount": -120.0,
            "category": "Фастфуд",
            "description": "Mouse Tail"
        }
    ]

    # Сравниваем результаты
    for res, expected in zip(result, expected_result):
        assert res["date"] == expected["date"]
        assert res["amount"] == expected["amount"]
        assert res["category"] == expected["category"]
        assert res["description"] == expected["description"]


# Тест для функции get_top_transactions с пустыми данными
def test_get_top_transactions_with_empty_data(empty_transactions_data):
    # Проверяем, что с пустыми данными результат будет пустым
    result = get_top_transactions(empty_transactions_data, 5)

    # Ожидаем, что результат будет пустым списком
    assert result == []
    assert len(result) == 0


# Тест для функции load_user_settings
def test_load_user_settings(mock_open_file):
    result = load_user_settings()

    # Проверяем, что настройки загружены корректно
    assert result == {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}


def test_load_user_settings_invalid_data(mocker):
    # Мокаем открытие и чтение некорректного файла
    mock_open_data = mock_open(read_data="invalid json")
    mocker.patch("builtins.open", mock_open_data)

    result = load_user_settings()

    # Проверяем, что при ошибке возвращается пустой словарь
    assert result == {}


# Тест для функции get_currency_rates
def test_get_currency_rates(mock_requests_get, mock_open_file):
    # Мокаем успешный ответ от API
    mock_requests_get.return_value.json.return_value = [{"price": 75.0}]
    mock_requests_get.return_value.status_code = 200

    result = get_currency_rates()

    # Проверяем результат
    assert result == [{"currency": "USD", "rate": 75.0}]
    mock_requests_get.assert_called_once()


def test_get_currency_rates_no_settings(mock_requests_get, mocker):
    # Мокаем пустые пользовательские настройки
    mocker.patch("moneyscope.utils.load_user_settings", return_value={})

    result = get_currency_rates()

    # Проверяем, что результат пуст
    assert result == []
    mock_requests_get.assert_not_called()


# Тест для функции get_stock_prices
def test_get_stock_prices(mock_requests_get, mock_open_file):
    # Мокаем успешный ответ от API
    mock_requests_get.return_value.json.return_value = [{"price": 150.0}]
    mock_requests_get.return_value.status_code = 200

    result = get_stock_prices()

    # Проверяем результат
    assert result == [{"stock": "AAPL", "price": 150.0}]
    mock_requests_get.assert_called_once()


def test_get_stock_prices_no_settings(mock_requests_get, mocker):
    # Мокаем пустые пользовательские настройки
    mocker.patch("moneyscope.utils.load_user_settings", return_value={})

    result = get_stock_prices()

    # Проверяем, что результат пуст
    assert result == []
    mock_requests_get.assert_not_called()
