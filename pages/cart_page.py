"""Page Object for the Shopping Cart page."""

from playwright.sync_api import Page, expect


class CartPage:
    """Encapsulates locators and actions for verifying cart contents."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        # Locators
        self.cart_rows = page.locator("#cart_info_table tbody tr")
        self.product_name_cells = self.cart_rows.locator("td.cart_description h4 a")

    def get_cart_product_names(self) -> list[str]:
        """Return the list of product names currently present in the cart."""
        expect(self.product_name_cells.first).to_be_visible()
        return self.product_name_cells.all_inner_texts()

    def is_product_in_cart(self, product_name: str) -> bool:
        """Return True if a product with the given (exact) name is in the cart."""
        return product_name in self.get_cart_product_names()
