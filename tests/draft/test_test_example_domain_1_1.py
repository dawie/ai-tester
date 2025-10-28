import pytest
from playwright.sync_api import Page

def test_page_title(page: Page):
    """
    Verify the page title is correct.
    """
    page.goto("https://example.com")
    assert page.title() == "Example Domain"