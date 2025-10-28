import pytest
from playwright.sync_api import Page

@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    print("beforeEach")
    page.goto("https://doe.sys-dev.net/kindilink/attendance")
    yield
    print("afterEach")

def test_page_content_exists(page: Page):
    """
    Verify that some content is loaded on the page (basic check).
    This will need to be updated with actual content. For now checks for html tag.
    """
    page.locator("html").first().wait_for()
    assert page.locator("html").count() == 1