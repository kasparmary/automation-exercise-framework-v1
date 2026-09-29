"""Page Object for the Products listing / search results page and the
'Add to cart' confirmation modal that appears on it."""

from typing import TYPE_CHECKING

from playwright.sync_api import Page, expect

if TYPE_CHECKING:
    from pages.cart_page import CartPage


class ProductsSearchPage:
    """Encapsulates locators and actions for searching products and adding
    a product to the cart from the search results grid."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        # Locators
        self.search_input = page.locator("#search_product")
        self.search_button = page.locator("#submit_search")
        self.searched_products_title = page.get_by_text("Searched Products", exact=True)
        self.product_items = page.locator(".product-image-wrapper")
        self.continue_shopping_button = page.get_by_role("button", name="Continue Shopping")
        self.view_cart_link = page.locator("u:has-text('View Cart')")

    def search_product(self, product_name: str) -> None:
        """Search for a product by name and wait for results to render."""
        self.search_input.fill(product_name)
        self.search_button.click()
        expect(self.searched_products_title).to_be_visible()

    def get_visible_product_names(self) -> list[str]:
        """Return the list of product names currently shown in the results grid."""
        names = self.product_items.locator(".productinfo p")
        expect(names.first).to_be_visible()
        return names.all_inner_texts()

    def is_product_visible(self, product_name: str) -> bool:
        """Return True if a product with the given (exact) name is present."""
        return product_name in self.get_visible_product_names()

    def add_product_to_cart_by_name(self, product_name: str) -> None:
        """Hover over the matching product card and add it to the cart.

        The site reveals an 'Add to cart' overlay link on hover, then shows
        a confirmation modal with 'Continue Shopping' / 'View Cart' actions.
        """
        product_card = self.product_items.filter(
            has=self.page.locator(".productinfo p", has_text=product_name)
        ).first
        product_card.hover()
        product_card.get_by_text("Add to cart").click()
        expect(self.view_cart_link).to_be_visible()

    def go_to_cart(self) -> "CartPage":
        """Click 'View Cart' from the add-to-cart confirmation modal."""
        from pages.cart_page import CartPage  # local import avoids circular import

        self.view_cart_link.click()
        expect(self.page).to_have_url(f"{self.base_url}/view_cart")
        return CartPage(self.page, self.base_url)
