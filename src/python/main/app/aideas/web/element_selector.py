import logging
from datetime import datetime
from time import sleep
from typing import List, Callable

from selenium.common import NoSuchWindowException, StaleElementReferenceException, \
    NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as WaitCondition
from selenium.webdriver.support.wait import WebDriverWait, D

from .browser_cookie_store import BrowserCookieStore
from .reloadable_web_element import ReloadableWebElement
from ..config import parse_query, SearchBy, SearchConfig, SearchConfigs
from ..env import get_cookies_file_path

logger = logging.getLogger(__name__)

INTERVAL: int = 2


class ElementNotFoundError(Exception):
    pass


class ElementSelector:
    @classmethod
    def of(cls, webdriver, domain: str, wait_timeout_seconds: float = 20) -> 'ElementSelector':
        cookie_store = BrowserCookieStore(webdriver, get_cookies_file_path(domain))
        return cls(webdriver, wait_timeout_seconds, cookie_store)

    def __init__(self,
                 webdriver: WebDriver,
                 wait_timeout_seconds: float,
                 browser_cookie_store: BrowserCookieStore):
        self.__webdriver = webdriver
        self.__wait_timeout_seconds = wait_timeout_seconds
        self.__browser_cookie_store = browser_cookie_store

    def with_timeout(self, timeout: float) -> 'ElementSelector':
        if timeout == self.__wait_timeout_seconds:
            return self
        return self.__class__(self.__webdriver, timeout, self.__browser_cookie_store)

    def select_element(self, search_configs: SearchConfigs) -> WebElement:
        self.validate_search_inputs(search_configs)

        search_from = search_configs.search_from()
        if not search_from:
            root = self.__webdriver
        else:
            # The root does not have to be clickable etc.,
            # so we don't use reloadable web element here.
            root = self.__select_first_element(self.__webdriver, search_from)
            if root is None:
                raise ValueError(f'search-from is not valid: {search_from}')

        def load_element(attempts: int = 0) -> WebElement:
            if attempts > 0:
                sleep(INTERVAL)
            return self.__select_first_element(root, search_configs.search_for())

        element = load_element()

        return ReloadableWebElement(element, load_element, self.__wait_timeout_seconds)

    def load_page(self, link: str) -> bool:
        self.validate_link(link)

        if link == self.current_url():
            logger.debug(f'Already at: {link}')
            return False

        self.__browser_cookie_store.load()

        logger.debug(f'Opening page: {link}')
        self.__webdriver.get(link)

        # We wait till the body elements are located
        # Then we save cookies, if the page is newly loaded.
        try:
            self.__select_page_bodies()
        except Exception:
            logger.warning(f'Error selecting body elements of page: {link}')

        self.__browser_cookie_store.save()
        return True

    def get_webdriver(self):
        return self.__webdriver

    def get_wait_timeout_seconds(self):
        return self.__wait_timeout_seconds

    def get_browser_cookie_store(self):
        return self.__browser_cookie_store

    def __select_first_element(self, root: D, search_config: SearchConfig) -> WebElement:
        search_by = search_config.get_search_by()
        queries = search_config.get_queries()
        exception: Exception | None = None
        index: int = -1
        start_time = datetime.now()
        for query in queries:
            index += 1
            try:
                time_spent: float = (datetime.now() - start_time).total_seconds()
                time_left: float = self.__wait_timeout_seconds - time_spent

                if time_left < 0:
                    time_left = 0

                selected = self.__select_element(root, search_by, query, time_left)

                if selected is not None:
                    search_config.reorder_queries(index)
                    logger.debug(f'Found element using: {search_by} = {query}')
                    return selected

            except Exception as ex:
                exception = ex
                continue

        error_msg: str = (f"Failed to select element using: {search_by} = {queries}, "
                          f"current url: {self.current_url()}.")
        if exception is not None:
            raise ElementNotFoundError(error_msg) from exception
        else:
            raise ElementNotFoundError(error_msg)

    def __select_page_bodies(self) -> List[WebElement]:
        body_elements: List[WebElement] = self.__webdriver.find_elements(By.TAG_NAME, 'body')
        if len(body_elements) == 0:
            raise ElementNotFoundError(f'No body elements found for {self.current_url()}')

        return body_elements

    def __select_element(self,
                         root: D,
                         by: SearchBy,
                         query: str,
                         timeout_seconds: float) -> WebElement:

        if by == SearchBy.SHADOW_ATTRIBUTE:
            return self.__select_shadow_by_attributes(
                self.__webdriver, root, parse_query(query), timeout_seconds)

        return self.__select_element_by_xpath(root, query, timeout_seconds)

    @staticmethod
    def __select_shadow_by_attributes(webdriver,
                                      root,
                                      attributes: dict[str, str],
                                      timeout_seconds: float) -> WebElement:
        collection: list = []

        def has_attribute(element: WebElement, name: str, value: str) -> bool:
            candidate = element.get_attribute(name)
            return False if candidate is None else value in candidate

        def has_attributes(element: WebElement, attrs: dict[str, str]) -> bool:
            for name, value in attrs.items():
                if not has_attribute(element, name, value):
                    return False
            return True

        def collect(element) -> bool:
            try:
                if has_attributes(element, attributes):
                    logger.debug(f"Found shadow element having attributes: {attributes}")
                    collection.append(element)
                    return True
                return False
            except Exception:
                return False

        ElementSelector.__collect_shadows(webdriver, root, timeout_seconds, collect)

        if len(collection) == 0:
            raise NoSuchElementException(f"No shadow element found by attributes: {attributes}")

        return collection[0]

    # Adapted from here:
    # https://stackoverflow.com/questions/37384458/how-to-handle-elements-inside-shadow-dom-from-selenium
    @staticmethod
    def __collect_shadows(webdriver,
                          root,
                          timeout_seconds: float,
                          collect: Callable[[WebElement], bool]) -> None:

        def visit_all_elements(driver, elements):
            for element in elements:
                shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
                if shadow_root:
                    shadow_elements = driver.execute_script(
                        'return arguments[0].shadowRoot.querySelectorAll("*")', element)
                    visit_all_elements(driver, shadow_elements)
                else:
                    if collect(element):
                        break

        all_elements = WebDriverWait(root, timeout_seconds).until(
                WaitCondition.presence_of_all_elements_located((By.CSS_SELECTOR, '*')))

        visit_all_elements(webdriver, all_elements)

    @staticmethod
    def __select_element_by_xpath(root: D,
                                  xpath: str,
                                  timeout_seconds: float) -> WebElement:
        search_by: By = By.XPATH
        if timeout_seconds < 1:
            return root.find_element(search_by, xpath)
        else:
            try:
                return WebDriverWait(root, timeout_seconds).until(
                    WaitCondition.element_to_be_clickable((search_by, xpath)))
            except TimeoutException:
                # Element exists but, we timed-out waiting for the above condition
                logger.debug(f"Selecting element directly, "
                             f"despite timeout: {timeout_seconds} using: {xpath}")
                return root.find_element(search_by, xpath)
            except StaleElementReferenceException:
                logger.debug(f"Selecting element directly, despite staleness using: {xpath}")
                return root.find_element(search_by, xpath)

    @staticmethod
    def validate_search_inputs(search_configs: SearchConfigs):
        if search_configs is None:
            raise ValueError(f'Search config is invalid: {search_configs}')
        if not search_configs.search_for():
            raise ValueError(f'search-for is invalid: {search_configs.search_for()}')
        if not search_configs.search_for().get_queries():
            raise ValueError(
                f'search-for queries are invalid: {search_configs.search_for().get_queries()}')

    @staticmethod
    def validate_link(link: str):
        if link is None or link == '':
            raise ValueError('link is None or empty')

    def current_url(self, result_if_none: str = None) -> str:
        try:
            return self.__webdriver.current_url
        except NoSuchWindowException:
            return result_if_none
