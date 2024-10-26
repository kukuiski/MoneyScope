
# MoneyScope

## Описание

**MoneyScope** — приложение для анализа транзакций из Excel. Генерирует JSON для веб-страниц, формирует отчёты, предоставляет дополнительные сервисы.

### Модули

#### views.py
Генерация JSON-ответов для главной страницы (транзакции, курсы валют, акции). Используются данные из `user_settings.json`.

Пример использования:
```python
from moneyscope.views import get_main_page
from moneyscope.utils import read_operations
response = get_main_page("2021-12-31 16:44:00")
print(response)
```

#### services.py
Анализ категорий с повышенным кешбэком. Функция `top_3_cashback_categories`.

Пример использования:
```python
from moneyscope.services import top_3_cashback_categories
from moneyscope.utils import read_operations
data = read_operations()
top_categories = top_3_cashback_categories(data, 2021, 12)
print(top_categories)
```

#### reports.py
Возвращает траты по заданной категории за последние три месяца от указанной даты.
Декоратор `save_report_to_file` сохраняет результат в файл.

Пример использования:
```python
from moneyscope.reports import spending_by_category
from moneyscope.utils import read_operations
data = read_operations()
report = spending_by_category(data, "Супермаркеты", "31.12.2021")
print(report)
```

#### utils.py
Загрузка и обработка транзакций. Функция `read_operations` загружает данные, преобразуя даты и фильтруя транзакции.
Возвращает пустой DataFrame при возникновении ошибок.

Пример использования:
```python
from moneyscope.utils import read_operations
data = read_operations()
print(data)
```

#### logger_config.py
Настраивает логирование с ротацией файлов. Логи сохраняются в `log/moneyscope.log`.

## Установка

Для установки всех зависимостей:

```bash
poetry install
```

Для активации окружения:

```bash
poetry shell
```

## Конфигурация

Пример данных находится в `.env_template`:

```ini
DATA_PATH=Путь к Excel-файлу с операциями
USER_SETTINGS_PATH=Абсолютный путь к JSON-файлу с настройками
REPORT_FILES_DIR=Абсолютный путь к папке для сохранения отчётов
LOG_FILES_DIR=Абсолютный путь к папке для сохранения логов
FMP_API_URL=https://financialmodelingprep.com/api/v3/quote/
FMP_API_KEY=Ключ к API FMP
```

В файле `.env` вы должны указать соответствующие пути и параметры для корректной работы приложения.

## Логи

Логи сохраняются в `log/moneyscope.log`.

## Использование

Запуск основного скрипта:

```bash
python main.py
```

## Тестирование

Запуск тестов:

```bash
pytest
```

Тесты покрывают ключевые функции модулей: `views.py`, `services.py`, `reports.py`, `utils.py`.
