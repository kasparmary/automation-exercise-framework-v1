"""Business scenario: Login Validation.

Validates login behaviour across three conditions, sourced from CSV and
parametrized with Pytest:
  1. Valid registered user (credentials from environment variables)
  2. Valid email with invalid password
  3. Unknown email

The CSV uses the sentinel values 'ENV_EMAIL' / 'ENV_PASSWORD' for the valid
case so that no real secret ever lives in the repository; they are resolved
at runtime from the `credentials` fixture (see conftest.py).
"""

from pathlib import Path

import allure
import pytest

from pages.home_page import HomePage
from utilities.csv_reader import read_csv_data

DATA_FILE = Path(__file__).parent.parent / "data" / "login_data.csv"
LOGIN_TEST_DATA = read_csv_data(DATA_FILE)

ENV_EMAIL_SENTINEL = "ENV_EMAIL"
ENV_PASSWORD_SENTINEL = "ENV_PASSWORD"


def _resolve_credentials(login_case: dict[str, str], credentials: dict[str, str]) -> tuple[str, str]:
    """Substitute environment-variable sentinels in a CSV row with real values."""
    email = credentials["email"] if login_case["email"] == ENV_EMAIL_SENTINEL else login_case["email"]
    password = (
        credentials["password"] if login_case["password"] == ENV_PASSWORD_SENTINEL else login_case["password"]
    )
    return email, password


@allure.feature("Authentication")
@allure.story("Login Validation")
@pytest.mark.login
@pytest.mark.regression
@pytest.mark.parametrize(
    "login_case",
    LOGIN_TEST_DATA,
    ids=[row["test_case"] for row in LOGIN_TEST_DATA],
)
def test_login_validation(
    home_page: HomePage, credentials: dict[str, str], login_case: dict[str, str]
) -> None:
    """Login attempts succeed or fail according to the expected outcome in the CSV."""
    email, password = _resolve_credentials(login_case, credentials)
    expected_result = login_case["expected_result"]

    allure.dynamic.title(f"Login - {login_case['test_case']} -> expected: {expected_result}")
    allure.dynamic.description(
        "Verifies login form behaviour for a given email/password combination: "
        "successful login for valid credentials, and a clear error message for "
        "invalid password or unknown email."
    )

    with allure.step("Navigate to the Login page"):
        login_page = home_page.go_to_login()

    with allure.step(f"Attempt login with email '{email}'"):
        login_page.login(email, password)

    if expected_result == "success":
        with allure.step("Verify the user is logged in"):
            assert home_page.is_user_logged_in(), (
                "Expected user to be logged in after submitting valid credentials, "
                "but the 'Logged in as' indicator was not found."
            )
    else:
        with allure.step("Verify an invalid-credentials error message is shown"):
            login_page.expect_login_error()
