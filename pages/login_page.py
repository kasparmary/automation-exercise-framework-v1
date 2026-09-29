"""Page Object for the Login section of the combined Signup/Login page."""

from playwright.sync_api import Page, expect


class LoginPage:
    """Encapsulates locators and actions for the login form."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        # Locators - scoped to the "Login to your account" form to avoid
        # colliding with the signup form fields on the same page.
        self.login_form = page.locator("form", has=page.get_by_text("Login to your account"))
        self.email_input = self.login_form.locator("input[data-qa='login-email']")
        self.password_input = self.login_form.locator("input[data-qa='login-password']")
        self.login_button = self.login_form.locator("button[data-qa='login-button']")
        self.error_message = page.get_by_text("Your email or password is incorrect!")

    def login(self, email: str, password: str) -> None:
        """Submit the login form with the given credentials."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()

    def is_login_error_displayed(self) -> bool:
        """Return True if the invalid-credentials error message is shown."""
        return self.error_message.is_visible()

    def expect_login_error(self) -> None:
        """Assert that the invalid-credentials error message is shown."""
        expect(self.error_message).to_be_visible()
