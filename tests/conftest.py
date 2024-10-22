import pandas as pd
import pytest
from unittest.mock import patch, mock_open

# Фикстура для создания DataFrame с операциями
@pytest.fixture
def operations_data() -> pd.DataFrame:
    data = {
        "Дата операции": [
            "30.12.2021 17:50:17",
            "30.12.2021 14:48:25",
            "29.12.2021 22:32:24",
            "29.12.2021 22:28:47",
            "29.12.2021 16:22:08",
        ],
        "Номер карты": ["*4556", "*7197", "*4556", "*4556", "*5091"],
        "Сумма операции": [174000.0, -349.0, -1411.4, -1411.4, -120.0],
        "Кэшбэк": [None, None, 70.0, 70.0, None],
        "Категория": ["Пополнения", "Канцтовары", "Ж/д билеты", "Ж/д билеты", "Фастфуд"],
        "Описание": ["Пополнение через Газпромбанк", "Mitrankov M.V.", "РЖД", "РЖД", "Mouse Tail"],
        "Дата платежа": ["30.12.2021", "30.12.2021", "30.12.2021", "30.12.2021", "29.12.2021"],
        "Сумма платежа": [174000.0, -349.0, -1411.4, -1411.4, -120.0],
        "Валюта операции": ["RUB", "RUB", "RUB", "RUB", "RUB"],
        "Валюта платежа": ["RUB", "RUB", "RUB", "RUB", "RUB"],
        "MCC": [None, 5943.0, 4112.0, 4112.0, 5814.0],
        "Бонусы (включая кэшбэк)": [0, 6, 70, 70, 1],
        "Округление на инвесткопилку": [0, 0, 0, 0, 0],
        "Сумма операции с округлением": [174000.0, 349.0, 1411.4, 1411.4, 120.0],
    }

    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y", errors="coerce")

    return df


# Фикстура для пустого DataFrame
@pytest.fixture
def empty_operations_data() -> pd.DataFrame:
    return pd.DataFrame()


# Фикстура с данными операций, где есть кешбэк
@pytest.fixture
def cashback_operations_data() -> pd.DataFrame:
    data = {
        "Дата операции": [
            "2021-12-30 16:44:00",
            "2021-12-30 16:42:00",
            "2021-12-30 16:39:00",
            "2021-11-30 15:44:00",
            "2021-10-30 01:23:00",
        ],
        "Категория": ["Супермаркеты", "Супермаркеты", "Аптеки", "Фастфуд", "Фастфуд"],
        "Кэшбэк": [30, 25, 15, 50, 5],
    }

    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    return df


# Фикстура с данными транзакций
@pytest.fixture
def transactions_data() -> pd.DataFrame:
    data = {
        "Дата операции": [
            "2021-12-30 16:44:00",
            "2021-11-28 12:30:00",
            "2021-10-15 18:45:00",
            "2021-09-20 09:10:00",
            "2021-08-25 11:20:00",
        ],
        "Категория": ["Супермаркеты", "Аптеки", "Фастфуд", "Супермаркеты", "Супермаркеты"],
        "Сумма операции": [-160.89, -50.00, -200.00, -500.00, -75.00],
    }

    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    return df


# Фикстура для пустого DataFrame
@pytest.fixture
def empty_transactions_data() -> pd.DataFrame:
    # Создаем пустой DataFrame с необходимыми столбцами
    return pd.DataFrame(columns=["Дата операции", "Категория", "Сумма операции", "Сумма платежа", "Описание"])


# Фикстура для мока API-запросов
@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


# Фикстура для мока чтения JSON-файлов
@pytest.fixture
def mock_open_file(mocker):
    mock_open_data = mock_open(read_data='{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}')
    mocker.patch("builtins.open", mock_open_data)
