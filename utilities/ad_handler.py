"""Central, reusable handling for unexpected advertisement / overlay pop-ups.

automationexercise.com occasionally renders Google Ads iframes or consent
banners that overlap page content and intercept clicks. Rather than adding
ad-dismissal logic inside individual tests or page objects, this single
utility function is invoked from conftest.py (autouse fixture) before each
test interaction point, keeping every test and page object clean.

The function is intentionally defensive: if no overlay is present it returns
immediately without raising, since ads are transient and not guaranteed to
appear on every run.
"""

import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def dismiss_ad_overlays(page: Page, overlay_selectors: list[str]) -> None:
    """Detect and remove/close known ad and overlay elements if present.

    Args:
        page: The active Playwright Page.
        overlay_selectors: CSS selectors (from config.yaml -> ads.overlay_selectors)
            identifying known ad/overlay elements on the AUT.
    """
    for selector in overlay_selectors:
        try:
            locator = page.locator(selector)
            count = locator.count()
            if count == 0:
                continue

            for index in range(count):
                element = locator.nth(index)
                if not element.is_visible():
                    continue

                # Ads on this site are typically injected iframes/divs with no
                # close button; the safe, reusable action is to remove them
                # from the DOM so they stop intercepting clicks.
                element.evaluate("el => el.remove()")
                logger.info("Removed ad/overlay element matching selector: %s", selector)
        except Exception as error:  # noqa: BLE001 - defensive, must never fail a test
            logger.debug("Ad overlay check skipped for selector '%s': %s", selector, error)
