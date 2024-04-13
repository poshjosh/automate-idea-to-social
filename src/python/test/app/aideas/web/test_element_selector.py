import uuid

from selenium.webdriver.remote.webelement import WebElement

from ..web.noop_cookie_store import NoopCookieStore
from .....main.app.aideas.config import SearchConfigs
from .....main.app.aideas.env import get_cookies_file_path
from .....main.app.aideas.web.element_selector import ElementSelector


class TestWebElement(WebElement):
    def __init__(self,
                 is_displayed: bool = True, is_enabled: bool = True, is_selected: bool = False):
        super().__init__({}, str(uuid.uuid4().hex))
        self.__is_displayed = is_displayed
        self.__is_enabled = is_enabled
        self.__is_selected = is_selected

    def is_displayed(self) -> bool:
        return self.__is_displayed

    def is_enabled(self) -> bool:
        return self.__is_enabled

    def is_selected(self) -> bool:
        return self.__is_selected


class TestElementSelector(ElementSelector):
    @classmethod
    def of(cls, webdriver, domain, wait_timeout_seconds: float = 20) -> 'ElementSelector':
        cookie_store = NoopCookieStore(webdriver, get_cookies_file_path(domain))
        return cls(webdriver, wait_timeout_seconds, cookie_store)

    def select_element(self, search_configs: SearchConfigs) -> WebElement:
        self.validate_search_inputs(search_configs)
        return TestWebElement()

    def load_page(self, link: str) -> bool:
        self.validate_link(link)
        return True
