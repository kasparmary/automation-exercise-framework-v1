"""Shared Pytest fixtures: configuration loading, credentials, page setup,
central ad-overlay handling and Allure failure evidence capture.
"""

import os
from collections.abc import Generator
from pathlib import Path
from typing import Any

import allure
import pytest
from playwright.sync_api import Page

from pages.home_page import HomePage
from utilities.ad_handler import dismiss_ad_overlays
from utilities.yaml_reader import load_yaml_config

PROJECT_ROOT = Path(__file__).parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


@pytest.fixture(scope="session")
def config() -> dict[str, Any]:
    """Load framework/application configuration once per test session."""
    return load_yaml_config(CONFIG_PATH)


@pytest.fixture(scope="session")
def base_url(config: dict[str, Any]) -> str:
    """Base URL of the AUT, from config.yaml."""
    return config["app"]["base_url"]


@pytest.fixture(scope="session")
def credentials() -> dict[str, str]:
    """Valid training-user credentials, sourced from environment variables.

    Required environment variables:
        AUTOMATION_EXERCISE_EMAIL
        AUTOMATION_EXERCISE_PASSWORD
    """
    email = os.environ.get("AUTOMATION_EXERCISE_EMAIL")
    password = os.environ.get("AUTOMATION_EXERCISE_PASSWORD")

    if not email or not password:
        pytest.fail(
            "Missing required environment variables 'AUTOMATION_EXERCISE_EMAIL' and/or "
            "'AUTOMATION_EXERCISE_PASSWORD'. Export them before running the tests "
            "(see README.md)."
        )
    return {"email": email, "password": password}


# ---------------------------------------------------------------------------
# Browser / page configuration (overrides pytest-playwright defaults)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Extend pytest-playwright's default context args with our viewport."""
    viewport = config["browser"]["viewport"]
    return {
        **browser_context_args,
        "viewport": {"width": viewport["width"], "height": viewport["height"]},
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(
    browser_type_launch_args: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """Extend pytest-playwright's default launch args with channel/headless
    settings so tests run against Google Chrome, per framework requirements."""
    return {
        **browser_type_launch_args,
        "channel": config["browser"]["channel"],
        "headless": config["browser"]["headless"],
        "slow_mo": config["browser"]["slow_mo_ms"],
    }


@pytest.fixture
def page(page: Page, config: dict[str, Any]) -> Generator[Page, None, None]:
    """Wrap pytest-playwright's `page` fixture to apply framework-wide
    defaults: default timeouts and central ad/overlay handling.

    Ad overlays are dismissed automatically:
      * once right after any full page navigation, and
      * this same handler is safe to call from within page objects if a
        specific flow needs it, keeping the logic in one reusable place.
    """
    timeouts = config["timeouts"]
    page.set_default_timeout(timeouts["default_timeout_ms"])
    page.set_default_navigation_timeout(timeouts["navigation_timeout_ms"])

    overlay_selectors = config["ads"]["overlay_selectors"]

    def _handle_navigation(_frame) -> None:
        # Only react to main-frame navigations, and give the page a brief
        # moment to render any injected ad content before checking.
        if _frame == page.main_frame:
            page.wait_for_timeout(min(timeouts["page_load_wait_ms"], 1500))
            dismiss_ad_overlays(page, overlay_selectors)

    page.on("framenavigated", _handle_navigation)

    yield page

    page.remove_listener("framenavigated", _handle_navigation)


@pytest.fixture
def home_page(page: Page, base_url: str) -> HomePage:
    """Provide a HomePage object already navigated to the AUT home page."""
    home = HomePage(page, base_url)
    home.open()
    return home


# ---------------------------------------------------------------------------
# Allure evidence capture on failure
# ---------------------------------------------------------------------------


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot and page URL to the Allure report on test failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page_fixture: Page | None = item.funcargs.get("page")
        if page_fixture is not None:
            try:
                allure.attach(
                    page_fixture.screenshot(full_page=True),
                    name="screenshot-on-failure",
                    attachment_type=allure.attachment_type.PNG,
                )
                allure.attach(
                    page_fixture.url,
                    name="page-url-on-failure",
                    attachment_type=allure.attachment_type.TEXT,
                )
            except Exception:  # noqa: BLE001 - never fail the test due to evidence capture
                pass
