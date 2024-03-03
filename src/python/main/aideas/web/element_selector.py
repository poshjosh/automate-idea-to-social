import logging
from typing import List, Tuple, Callable

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as WaitCondition
from selenium.webdriver.support.wait import WebDriverWait, D

from .browser_cookie_store import BrowserCookieStore
from .element_search_config import ElementSearchConfig, SearchBy

logger = logging.getLogger(__name__)


class ElementSelector:
    @staticmethod
    def of(webdriver, domain: str, wait_timeout_seconds: float = 20) -> 'ElementSelector':
        return ElementSelector(
            webdriver, wait_timeout_seconds, BrowserCookieStore(webdriver, domain))

    def __init__(self,
                 webdriver,
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
                       element_name: str,
                       search_config: ElementSearchConfig) -> WebElement:
        self.validate_search_inputs(root_element, element_name, search_config)

        search_from: str = search_config.get_search_from()
        search_for_list: [str] = search_config.get_search_for()

        no_search_for_list: bool = search_for_list is None or len(search_for_list) == 0

        if search_from is None or search_from == '':
            if no_search_for_list:
                raise ValueError(
                    f'search_from and search_for are both None or empty for {element_name}')
            search_from_element = root_element
        else:
            search_from_element = self.__select_element(
                root_element, element_name, search_from,
                self.__wait_timeout_seconds, search_config.get_search_by())

        if search_from_element is None:
            raise ValueError(f'For {element_name} search_from is not valid: {search_from}')

        if no_search_for_list:
            return search_from_element

        return self.__select_first_element(
            search_from_element, element_name, search_for_list, search_config.get_search_by())

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
                               element_name: str,
                               search_for_list: [str],
                               search_by: SearchBy) -> WebElement:
        exception: Exception = None
        index: int = -1
        for search_for in search_for_list:
            index += 1
            timeout: float = self.__wait_timeout_seconds if index == 0 else 2
            try:
                selected = self.__select_element(
                    search_from_element, element_name, search_for, timeout, search_by)
                if selected is not None:
                    return selected
            except Exception as ex:
                logger.debug(f'Failed to select {element_name} using: {search_by} = {search_for}')
                exception = ex
                continue

        if exception is not None:
            raise exception
        else:
            raise ValueError(f"Failed to select {element_name} element, "
                             f"current url: {self.__webdriver.current_url}.")

    def __load_page(self, link: str) -> bool:
        if link == self.__webdriver.current_url:
            logger.debug(f'Already at: {link}')
            return False
        self.__browser_cookie_store.load()
        logger.debug(f'Opening page: {link}')
        self.__webdriver.get(link)
        return True

    def __select_page_bodies(self) -> List[WebElement]:
        body_elements: List[WebElement] = self.__webdriver.find_elements(By.TAG_NAME, 'body')
        if len(body_elements) == 0:
            raise ValueError(f'No body elements found for {self.__webdriver.current_url}')

        return body_elements

    def __select_element(self,
                         root_element: D,
                         element_name: str,
                         search_for: str,
                         timeout_seconds: float,
                         by: SearchBy) -> WebElement:
        if by == SearchBy.SHADOW_ATTRIBUTE:
            return self.__select_shadow_by_attribute(
                root_element, timeout_seconds, ElementSearchConfig.to_attr(search_for))

        return self.__wait_until_element_is_clickable(
            root_element, element_name, search_for, timeout_seconds)

    def __select_shadow_by_attribute(self,
                                     root_element: D,
                                     timeout_seconds: float,
                                     attr: Tuple[str, str]) -> WebElement:
        collection: list = []
        attr_name = attr[0]
        attr_value = attr[1]

        logger.debug(f"Selecting shadow element by attribute: {attr_name}={attr_value}")

        def collector(element) -> bool:
            try:
                candidate = element.get_attribute(attr_name)
                if candidate is None:
                    return False
                if attr_value in candidate:
                    logger.debug(f"Found shadow element having attribute: {attr_name}={candidate}")
                    collection.append(element)
                    return True
                return False
            except Exception as ignored:
                return False

        self.__collect_shadows(root_element, timeout_seconds, collector)

        if len(collection) == 0:
            raise ValueError(f"No shadow element found by attribute: {attr_name}={attr_value}")

        return collection[0]

    # Adapted from jaksco's answer here:
    # https://stackoverflow.com/questions/37384458/how-to-handle-elements-inside-shadow-dom-from-selenium
    def __collect_shadows(self,
                          root_element: D,
                          timeout_seconds: float,
                          collector: Callable[[WebElement], bool]) -> None:

        def visit_all_elements(driver, elements):
            for element in elements:
                shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
                if shadow_root:
                    shadow_elements = driver.execute_script(
                        'return arguments[0].shadowRoot.querySelectorAll("*")', element)
                    visit_all_elements(driver, shadow_elements)
                else:
                    if collector(element):
                        break

        elements = WebDriverWait(root_element, timeout_seconds).until(
            WaitCondition.presence_of_all_elements_located((By.CSS_SELECTOR, '*')))

        visit_all_elements(self.__webdriver, elements)

    def __wait_until_element_is_clickable(self,
                                          root_element: D,
                                          element_name: str,
                                          xpath: str,
                                          timeout_seconds: float) -> WebElement:
        try:
            return WebDriverWait(root_element, timeout_seconds).until(
                WaitCondition.element_to_be_clickable((self.__select_by, xpath)))
        except TimeoutException:
            logger.debug(
                f'Timed out selecting {element_name}, '
                f'current url: {self.__webdriver.current_url}.')
            return root_element.find_element(self.__select_by, xpath)

    @staticmethod
    def validate_search_inputs(root_element: WebElement,
                               element_name: str,
                               search_config: ElementSearchConfig) -> WebElement:
        if root_element is None:
            raise ValueError('root element for searching is None')
        if element_name is None or element_name == '':
            raise ValueError('element_name is None or empty')
        if search_config is None:
            raise ValueError('search_config is None')
        return WebElement({}, None)

    @staticmethod
    def validate_link(link: str):
        if link is None or link == '':
            raise ValueError('link is None or empty')
