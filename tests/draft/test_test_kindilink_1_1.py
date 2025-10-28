import pytest
from playwright.sync_api import Page

@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    print("beforeEach")
    page.goto("https://doe.sys-dev.net/kindilink/attendance")
    yield
    print("afterEach")


def test_page_title(page: Page):
    """
    Verify the page title is correct.
    """
    assert page.title() == "Kindilink"