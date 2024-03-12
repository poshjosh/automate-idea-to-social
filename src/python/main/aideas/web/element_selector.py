import logging
from time import sleep
from typing import List, Callable, TypeVar

from selenium.common import NoSuchWindowException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as WaitCondition
from selenium.webdriver.support.wait import WebDriverWait, D

from .browser_cookie_store import BrowserCookieStore
from .stale_web_element import StaleWebElement
from ..config import parse_attributes, SearchConfig, SearchBy

logger = logging.getLogger(__name__)

INTERVAL: int = 2


class ElementNotFoundError(Exception):
    pass


class ElementSelector:
    @staticmethod
    def of(webdriver, domain: str, wait_timeout_seconds: float = 20) -> 'ElementSelector':
        return ElementSelector(
            webdriver, wait_timeout_seconds, BrowserCookieStore(webdriver, domain))

    def __init__(self,
                 webdriver: WebDriver,
                 wait_timeout_seconds: float,
                 browser_cookie_store: BrowserCookieStore):
        self.__webdriver = webdriver
        self.__select_by = By.XPATH
        self.__wait_timeout_seconds = wait_timeout_seconds
        self.__browser_cookie_store = browser_cookie_store

    def with_timeout(self, timeout: float) -> 'ElementSelector':
        if timeout == self.__wait_timeout_seconds:
            return self
        return ElementSelector(self.__webdriver, timeout, self.__browser_cookie_store)

    def select_element(self,
                       root_element: WebElement,
                       search_config: SearchConfig) -> WebElement:
        self.validate_search_inputs(root_element, search_config)

        search_from: str = search_config.get_search_from()
        search_for_list: [str] = search_config.get_search_for()

        no_search_for_list: bool = search_for_list is None or len(search_for_list) == 0

        if search_from is None or search_from == '':
            if no_search_for_list:
                raise ValueError('search-from and search-for are both None or empty')
            search_from_element = root_element
        else:
            search_from_element = self.__select_element(
                root_element, search_from,
                self.__wait_timeout_seconds, search_config.get_search_by())

        if search_from_element is None:
            raise ValueError(f'search-from is not valid: {search_from}')

        if no_search_for_list:
            return search_from_element

        tup: [WebElement, int] = self.__select_first_element(
            search_from_element, search_for_list, search_config.get_search_by())

        search_config.set_successful_query_index(tup[1])

        return tup[0]

    def load_page_bodies(self, link: str) -> List[WebElement]:
        self.validate_link(link)

        page_newly_loaded: bool = self.__load_page(link)
        page_bodies: List[WebElement] = self.__select_page_bodies()
        # We wait till the body elements are located
        # Then we save cookies, if the page is newly loaded.
        if page_newly_loaded:
            self.__browser_cookie_store.save()
        return page_bodies

    def get_webdriver(self):
        return self.__webdriver

    def get_wait_timeout_seconds(self):
        return self.__wait_timeout_seconds

    def get_browser_cookie_store(self):
        return self.__browser_cookie_store

    def __select_first_element(self,
                               search_from_element: WebElement,
                               search_for_list: [str],
                               search_by: SearchBy) -> [WebElement, int]:
        exception: Exception = None
        index: int = -1
        for search_for in search_for_list:
            index += 1
            timeout: float = self.__wait_timeout_seconds if index == 0 else INTERVAL
            try:
                selected = self.__select_element(
                    search_from_element, search_for, timeout, search_by)
                if selected is not None:
                    logger.debug(f'Found element using: {search_by} = {search_for}')
                    return selected, index
            except Exception as ex:
                exception = ex
                continue

        error_msg: str = f"Failed to select element, current url: {self.current_url()}."
        if exception is not None:
            raise ElementNotFoundError(error_msg) from exception
        else:
            raise ElementNotFoundError(error_msg)

    def __load_page(self, link: str) -> bool:
        if link == self.current_url():
            logger.debug(f'Already at: {link}')
            return False
        self.__browser_cookie_store.load()
        logger.debug(f'Opening page: {link}')
        self.__webdriver.get(link)
        return True

    def __select_page_bodies(self) -> List[WebElement]:
        body_elements: List[WebElement] = self.__webdriver.find_elements(By.TAG_NAME, 'body')
        if len(body_elements) == 0:
            raise ElementNotFoundError(f'No body elements found for {self.current_url()}')

        return body_elements

    def __select_element(self,
                         root_element: D,
                         search_for: str,
                         timeout_seconds: float,
                         by: SearchBy) -> WebElement:
        if by == SearchBy.SHADOW_ATTRIBUTE:
            return self.__select_shadow_by_attributes(
                root_element, timeout_seconds, parse_attributes(search_for))

        return self.__wait_for_element(root_element, search_for, timeout_seconds)

    def __select_shadow_by_attributes(self,
                                      root_element: D,
                                      timeout_seconds: float,
                                      attributes: dict[str, str]) -> WebElement:
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

        self.__collect_shadows(root_element, timeout_seconds, collect)

        if len(collection) == 0:
            raise ElementNotFoundError(
                f"No shadow element found by attributes: {attributes}")

        return collection[0]

    # Adapted from jaksco's answer here:
    # https://stackoverflow.com/questions/37384458/how-to-handle-elements-inside-shadow-dom-from-selenium
    def __collect_shadows(self,
                          root_element: D,
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

        elements = WebDriverWait(root_element, timeout_seconds).until(
                WaitCondition.presence_of_all_elements_located((By.CSS_SELECTOR, '*')))

        visit_all_elements(self.__webdriver, elements)

    def __wait_for_element(self,
                           root_element: D,
                           xpath: str,
                           timeout_seconds: float) -> WebElement:

        if timeout_seconds < 1:
            # TODO - Using a web element as root for the find lead to error
            #  selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element
            # return root_element.find_element(self.__select_by, xpath)
            return self.__webdriver.find_element(self.__select_by, xpath)

        def select_clickable_element(attempts: int = 0) -> WebElement:
            if attempts > 0:
                sleep(INTERVAL)
            return WebDriverWait(root_element, timeout_seconds).until(
                WaitCondition.element_to_be_clickable((self.__select_by, xpath)))

        def select_located_element() -> WebElement:
            sleep(INTERVAL)
            ignored_exceptions = [StaleElementReferenceException]
            return WebDriverWait(
                root_element, timeout_seconds, ignored_exceptions=ignored_exceptions).until(
                WaitCondition.presence_of_element_located((self.__select_by, xpath)))

        try:
            return select_clickable_element()
        except TimeoutException:
            logger.debug(f"Timeout for element using: {xpath}")
            return self.__webdriver.find_element(self.__select_by, xpath)
        except StaleElementReferenceException:
            logger.debug(f"Stale element using: {xpath}")
            return StaleWebElement(
                select_located_element(), select_clickable_element, timeout_seconds)

    @staticmethod
    def validate_search_inputs(root_element: WebElement,
                               search_config: SearchConfig) -> WebElement:
        if root_element is None:
            raise ValueError('root element for searching is None')
        if search_config is None:
            raise ValueError('search_config is None')
        return WebElement({}, None)

    @staticmethod
    def validate_link(link: str):
        if link is None or link == '':
            raise ValueError('link is None or empty')

    def current_url(self, result_if_none: str = None) -> str:
        try:
            return self.__webdriver.current_url
        except NoSuchWindowException as ignored:
            return result_if_none

    T = TypeVar('T')

    @staticmethod
    def run_till_success(func: Callable[[int], T], timeout: float = 60, interval: int = 1) -> T:
        from time import sleep
        from datetime import datetime, timedelta
        start = datetime.now()
        max_time = timedelta(seconds=timeout)
        trials = -1
        while True:
            try:
                trials += 1
                return func(trials)
            except Exception as ex:
                if datetime.now() - start > max_time:
                    raise ex
                sleep(interval)
