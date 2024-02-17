import logging
from typing import List, Callable, Union, Literal
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import D, T, WebDriverWait

logger = logging.getLogger(__name__)


def get_web_page_bodies(webdriver, link: str) -> List[WebElement]:
    webdriver.get(link)

    webdriver.maximize_window()

    return webdriver.find_elements(By.TAG_NAME, 'body')


def is_button(element: WebElement) -> bool:
    if (element.tag_name == 'button'
            or element.get_attribute('type') == 'button'
            or element.get_attribute('type') == 'submit'):
        return True
    return False


def select_first(element: WebElement,
                 test: Callable[[WebElement], bool],
                 result_if_none: WebElement) -> WebElement:
    if element is None:
        raise ValueError(f'Expected a value for element, but found: {element}')
    if test(element) is True:
        return element
    child_elements = element.find_elements(By.XPATH, '*')
    for child_element in child_elements:
        if test(child_element) is True:
            return child_element
        else:
            return select_first(child_element, test, result_if_none)
    return result_if_none


def wait_until(pivot: D,
               timeout: float,
               method: Callable[[D], Union[Literal[False], T]],
               message: str = "") -> T:
    return WebDriverWait(pivot, timeout).until(method, message)


def execute_for_bool(func: Callable[[any], any], arg: any) -> bool:
    try:
        func(arg)
    except Exception as ex:
        logger.warning(f'Error: {ex}')
        return False
    else:
        return True
