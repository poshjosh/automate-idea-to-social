import logging
from typing import List, Callable
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

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


def execute_for_bool(func: Callable[[any], any], arg: any) -> bool:
    try:
        func(arg)
    except Exception as ex:
        logger.warning(f'Error: {ex}')
        return False
    else:
        return True
