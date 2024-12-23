from moneyscope.reports import spending_by_category
from moneyscope.services import top_3_cashback_categories
from moneyscope.utils import read_operations
from moneyscope.views import get_main_page


def main() -> None:
    """Основная функция для тестирования остальных"""
    print(get_main_page("2021-12-31 16:44:00"))
    ops = read_operations()
    ops_dict = ops.to_dict(orient="records")
    print(top_3_cashback_categories(ops_dict, 2021, 12))
    print(spending_by_category(ops, "Супермаркеты", "31.12.2021"))
    return None


if __name__ == "__main__":
    main()
