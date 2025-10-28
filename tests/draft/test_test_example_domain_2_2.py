import pytest
from playwright.sync_api import Page

def test_learn_more_link(page: Page):
    """
    Verify the "Learn more" link exists and points to the correct URL.
    """
    page.goto("https://example.com")
    learn_more_link = page.locator("text=Learn more")
    assert learn_more_link.is_visible()
    assert learn_more_link.get_attribute("href") == "https://iana.org/domains/example"