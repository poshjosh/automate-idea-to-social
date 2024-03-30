import uuid

from selenium.webdriver.remote.webelement import WebElement

from ..web.noop_cookie_store import NoopCookieStore
from .....main.app.aideas.config import SearchConfigs
from .....main.app.aideas.env import get_cookies_file_path
from .....main.app.aideas.web.element_selector import ElementSelector


class TestElementSelector(ElementSelector):
    @staticmethod
    def of(webdriver, domain, wait_timeout_seconds: float = 20) -> 'ElementSelector':
        cookie_store = NoopCookieStore(webdriver, get_cookies_file_path(domain))
        return TestElementSelector(
            webdriver, wait_timeout_seconds, cookie_store)

    def with_timeout(self, timeout: float) -> 'ElementSelector':
        return TestElementSelector(
            self.get_webdriver(), timeout, self.get_browser_cookie_store())

    def select_element(self, search_configs: SearchConfigs) -> WebElement:
        self.validate_search_inputs(search_configs)
        return WebElement({}, str(uuid.uuid4().hex))

    def load_page(self, link: str) -> bool:
        self.validate_link(link)
        return True
