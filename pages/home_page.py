"""Page Object for the Automation Exercise home page."""

from typing import TYPE_CHECKING

from playwright.sync_api import Page, expect

if TYPE_CHECKING:
    from pages.login_page import LoginPage
    from pages.products_page import ProductsSearchPage


class HomePage:
    """Encapsulates locators and actions available on the home page."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        # Locators
        self.products_nav_link = page.get_by_role("link", name="Products", exact=True)
        self.signup_login_link = page.get_by_role("link", name="Signup / Login")
        self.logged_in_as_text = page.locator("li:has-text('Logged in as')")

    def open(self) -> None:
        """Navigate to the AUT home page."""
        self.page.goto(self.base_url)
        expect(self.page).to_have_title("Automation Exercise")

    def go_to_products(self) -> "ProductsSearchPage":
        """Navigate to the Products/Search page from the top navigation."""
        from pages.products_page import ProductsSearchPage  # local import avoids circular import

        self.products_nav_link.click()
        expect(self.page).to_have_url(f"{self.base_url}/products")
        return ProductsSearchPage(self.page, self.base_url)

    def go_to_login(self) -> "LoginPage":
        """Navigate to the Login/Signup page from the top navigation."""
        from pages.login_page import LoginPage  # local import avoids circular import

        self.signup_login_link.click()
        expect(self.page).to_have_url(f"{self.base_url}/login")
        return LoginPage(self.page, self.base_url)

    def is_user_logged_in(self) -> bool:
        """Return True if the header shows a 'Logged in as ...' indicator,
        confirming a successful login without depending on the exact
        display name used for the training account."""
        return self.logged_in_as_text.is_visible()
