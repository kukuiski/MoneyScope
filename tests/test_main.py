from unittest.mock import patch
from moneyscope.main import main


@patch("moneyscope.main.read_operations")
@patch("moneyscope.main.get_main_page")
@patch("moneyscope.main.top_3_cashback_categories")
@patch("moneyscope.main.spending_by_category")
def test_main(mock_spending_by_category, mock_top_3_cashback_categories, mock_get_main_page, mock_read_operations):
    # Настройка моков для возврата тестовых данных
    mock_read_operations.return_value = "test_operations"
    mock_get_main_page.return_value = "main_page_result"
    mock_top_3_cashback_categories.return_value = "cashback_result"
    mock_spending_by_category.return_value = "spending_result"

    # Запускаем main и проверяем вызовы
    main()

    # Проверяем, что функции были вызваны с правильными аргументами
    mock_read_operations.assert_called_once()
    mock_get_main_page.assert_called_once_with("test_operations", "2021-12-31 16:44:00")
    mock_top_3_cashback_categories.assert_called_once_with("test_operations", 2021, 12)
    mock_spending_by_category.assert_called_once_with("test_operations", "Супермаркеты", "31.12.2021")
