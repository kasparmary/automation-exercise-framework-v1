"""Business scenario: Add Product to Cart.

Search for a product, add it to the cart from the search results, and
verify it appears correctly in the cart.
"""

from pathlib import Path

import allure
import pytest

from pages.home_page import HomePage
from utilities.csv_reader import read_csv_data

DATA_FILE = Path(__file__).parent.parent / "data" / "cart_products.csv"
CART_TEST_DATA = read_csv_data(DATA_FILE)


@allure.feature("Shopping Cart")
@allure.story("Add Product to Cart")
@pytest.mark.cart
@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.parametrize(
    "cart_case",
    CART_TEST_DATA,
    ids=[row["test_case"] for row in CART_TEST_DATA],
)
def test_add_product_to_cart(home_page: HomePage, cart_case: dict[str, str]) -> None:
    """Adding a searched product to the cart results in it appearing in the cart."""
    search_term = cart_case["search_term"]
    expected_product = cart_case["expected_product_in_cart"]

    allure.dynamic.title(f"Add '{search_term}' to cart and verify it appears in the cart")
    allure.dynamic.description(
        "End-to-end flow: search for a product, add it to the cart from the "
        "search results grid, then verify it is present on the cart page."
    )

    with allure.step(f"Search for '{search_term}'"):
        products_page = home_page.go_to_products()
        products_page.search_product(search_term)

    with allure.step(f"Add '{expected_product}' to the cart"):
        products_page.add_product_to_cart_by_name(expected_product)

    with allure.step("Open the cart"):
        cart_page = products_page.go_to_cart()

    with allure.step(f"Verify '{expected_product}' is present in the cart"):
        assert cart_page.is_product_in_cart(expected_product), (
            f"Expected product '{expected_product}' was not found in the cart. "
            f"Found: {cart_page.get_cart_product_names()}"
        )
