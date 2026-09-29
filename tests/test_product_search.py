"""Business scenario: Product Search.

Search for products using CSV-driven test data and verify that the
expected product is returned in the search results.
"""

from pathlib import Path

import allure
import pytest

from pages.home_page import HomePage
from utilities.csv_reader import read_csv_data

DATA_FILE = Path(__file__).parent.parent / "data" / "search_products.csv"
SEARCH_TEST_DATA = read_csv_data(DATA_FILE)


@allure.feature("Product Catalog")
@allure.story("Product Search")
@pytest.mark.search
@pytest.mark.regression
@pytest.mark.parametrize(
    "search_case",
    SEARCH_TEST_DATA,
    ids=[row["test_case"] for row in SEARCH_TEST_DATA],
)
def test_search_product_returns_expected_result(home_page: HomePage, search_case: dict[str, str]) -> None:
    """Searching for a product returns the expected product in the results."""
    search_term = search_case["search_term"]
    expected_product = search_case["expected_product_name"]

    allure.dynamic.title(f"Search for '{search_term}' returns '{expected_product}'")
    allure.dynamic.description(
        "Verifies that searching the product catalog for a given keyword "
        "surfaces the expected product in the search results grid."
    )

    with allure.step(f"Navigate to Products page and search for '{search_term}'"):
        products_page = home_page.go_to_products()
        products_page.search_product(search_term)

    with allure.step(f"Verify '{expected_product}' is present in the search results"):
        assert products_page.is_product_visible(expected_product), (
            f"Expected product '{expected_product}' was not found in search "
            f"results for term '{search_term}'. "
            f"Found: {products_page.get_visible_product_names()}"
        )
