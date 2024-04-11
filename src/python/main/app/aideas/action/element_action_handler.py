import logging
import time
from enum import unique
from typing import Tuple

from selenium.common import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.remote.webelement import WebElement

from .action_handler import execute_for_result, BaseActionId
from .browser_action_handler import BrowserActionHandler, WEB_DRIVER
from ..action.action import Action
from ..action.action_result import ActionResult
from ..web.reloadable_web_element import ReloadableWebElement

logger = logging.getLogger(__name__)


@unique
class ElementActionId(BaseActionId):
    CLEAR_TEXT = ('clear_text', False)
    CLICK = ('click', False)
    CLICK_AND_HOLD = ('click_and_hold', False)
    CLICK_AND_HOLD_CURRENT_POSITION = ('click_and_hold_current_position', False)
    ENTER = ('enter', False)
    ENTER_TEXT = ('enter_text', False)
    EXECUTE_SCRIPT_ON = ('execute_script_on', False)
    GET_ATTRIBUTE = 'get_attribute'
    GET_TEXT = 'get_text'
    IS_DISPLAYED = 'is_displayed'
    MOVE_TO_ELEMENT = ('move_to_element', False)
    MOVE_TO_ELEMENT_OFFSET = ('move_to_element_offset', False)
    RELEASE = ('release', False)
    SEND_KEYS = ('send_keys', False)


class ElementActionHandler(BrowserActionHandler):
    @staticmethod
    def to_action_id(action: str) -> BaseActionId:
        try:
            return BrowserActionHandler.to_action_id(action)
        except ValueError:
            return ElementActionId(action)

    def __init__(self,
                 web_driver: WEB_DRIVER,
                 wait_timeout_seconds: float):
        super().__init__(
            web_driver, wait_timeout_seconds)

    def with_timeout(self, timeout: float) -> 'ElementActionHandler':
        if timeout == self.get_wait_timeout_seconds():
            return self
        return ElementActionHandler(self.get_web_driver(), timeout)

    def execute_on(self, action: Action, element: WebElement) -> ActionResult:
        key = action.get_name_without_negation() if action.is_negation() else action.get_name()
        try:
            if isinstance(element, ReloadableWebElement):
                # We use the actual web element for the action
                # When we used the ReloadableWebElement, the action fails with message:
                # TypeError: Object of type ReloadableWebElement is not JSON serializable
                element = element.load()

            result = self._execute_on(key, action, element)

        except StaleElementReferenceException as ex:
            logger.warning('Element is stale')
            if isinstance(element, ReloadableWebElement):
                element = element.reload()
                logger.debug(f'Retrying action after reloading element: {action}')
                result = self._execute_on(key, action, element)
            else:
                raise ex

        if action.is_negation():
            result = result.flip()
        return result

    def _execute_on(self, key: str, action: Action, element: WebElement) -> ActionResult:
        try:
            return self.__do_execute_on(key, action, element)
        except Exception as ex:
            self.__print_element_attr(ex, element, 'outerHTML')
            raise ex

    def __do_execute_on(self, key: str, action: Action, element: WebElement) -> ActionResult:
        driver = self.get_web_driver()
        if key == ElementActionId.CLEAR_TEXT.value:
            def clear_text(tgt: WebElement):
                tgt.send_keys(Keys.CONTROL, 'a')
                tgt.send_keys(Keys.DELETE)
                tgt.clear()  # May not work under certain conditions, so we try the following

            result = execute_for_result(clear_text, element, action)
        elif key == ElementActionId.CLICK.value:
            result = execute_for_result(lambda arg: self.__click(driver, arg), element, action)
        elif key == ElementActionId.CLICK_AND_HOLD.value:
            def click_and_hold(tgt: WebElement):
                ActionChains(driver).click_and_hold(tgt).perform()

            result = execute_for_result(click_and_hold, element, action)
        elif key == ElementActionId.CLICK_AND_HOLD_CURRENT_POSITION.value:
            def click_and_hold_current_position(_: WebElement):
                ActionChains(driver).click_and_hold(None).perform()

            result = execute_for_result(click_and_hold_current_position, element, action)
        elif key == ElementActionId.ENTER.value:
            result = execute_for_result(lambda arg: arg.send_keys(Keys.ENTER), element, action)
        elif key == ElementActionId.ENTER_TEXT.value:
            text: str = ' '.join(action.get_args())
            result = execute_for_result(lambda arg: arg.send_keys(text), element, action)
        elif key == ElementActionId.EXECUTE_SCRIPT_ON.value:
            result = self.__execute_script_on(self.get_web_driver(), action, element)
        elif key == ElementActionId.GET_ATTRIBUTE.value:
            attr_name = action.get_first_arg()
            result = execute_for_result(lambda arg: element.get_attribute(arg), attr_name, action)
        elif key == ElementActionId.GET_TEXT.value:
            text = element.text
            result = ActionResult(action, True, text if not text else text.strip())
        elif key == ElementActionId.IS_DISPLAYED.value:
            success = element.is_displayed()
            result = ActionResult(action, success, success)
        elif key == ElementActionId.MOVE_TO_ELEMENT.value:
            def move_to_element(tgt: WebElement):
                ActionChains(driver).move_to_element(tgt).perform()

            result = execute_for_result(move_to_element, element, action)
        elif key == ElementActionId.MOVE_TO_ELEMENT_OFFSET.value:
            result = self.__move_to_element_offset(self.get_web_driver(), action, element)
        elif key == ElementActionId.RELEASE.value:
            def release(on_element: bool):
                ActionChains(driver).release(element if on_element is True else None).perform()
            result = execute_for_result(release, bool(action.get_first_arg()), action)
        elif key == ElementActionId.SEND_KEYS.value:
            def send_keys(txt: str):
                for char in txt:
                    element.send_keys(char)
                    time.sleep(0.5)
                return txt

            result = execute_for_result(send_keys, ' '.join(action.get_args()), action)
        else:
            return super()._execute(key, action)  # Success state has already been printed
        logger.debug(f'{result}')
        return result

    @staticmethod
    def __click(webdriver: WEB_DRIVER, element: WebElement):
        try:
            # Click means only click. We have a separate action for move_to_element
            # Adding move_to_element here will disrupt some reasonable expectations
            # For example. When we move to bottom right before clicking,
            # we don't expect additional movements before the click is effected.
            # If you need to, explicitly specify move_to_element before click
            element.click()
        except ElementClickInterceptedException:
            logger.warning('Element click intercepted. Will try clicking via JavaScript.')
            webdriver.execute_script("arguments[0].click();", element)

    @staticmethod
    def __execute_script_on(webdriver, action: Action, element: WebElement) -> ActionResult:
        def execute_on(script: str):
            return webdriver.execute_script(script, element)
        return execute_for_result(execute_on, ' '.join(action.get_args()), action)

    @staticmethod
    def __move_to_element_offset(webdriver, action: Action, element: WebElement):
        start: str = action.get_first_arg()
        if not start:
            raise ValueError("No start point provided for move_to_element_offset")

        element_size: dict = element.size

        offset_from_center: Tuple[int, int] = (0, 0) if start == 'center' \
            else ElementActionHandler.__compute_offset_relative_to_center(element_size, start)

        additional_offset: Tuple[int, int] = (
            ElementActionHandler.__compute_additional_offset(element_size, action.get_args()[1:]))

        # We add the offset provided by the user
        x = offset_from_center[0] + additional_offset[0]
        y = offset_from_center[1] + additional_offset[1]

        return ElementActionHandler.__move_to_center_offset(
            webdriver, element, (x, y), action)

    @staticmethod
    def __move_to_center_offset(
            webdriver, element: WebElement, offset: Tuple[int, int], action: Action):
        def move_to_element_with_offset(tgt: WebElement):
            ActionChains(webdriver).move_to_element_with_offset(
                tgt, offset[0], offset[1]).perform()
        return execute_for_result(move_to_element_with_offset, element, action)

    @staticmethod
    def __compute_offset_relative_to_center(size: dict, start: str) -> Tuple[int, int]:
        width = size['width']
        height = size['height']

        half_w = width/2
        half_h = height/2

        # We calculate how much to move from the center of the element to these positions
        if start == "top-left":
            point = -half_w, half_h
        elif start == "top-right":
            point = half_w, half_h
        elif start == "bottom-left":
            point = -half_w, -half_h
        elif start == "bottom-right":
            point = half_w, -half_h
        else:
            raise ValueError(f"Invalid start point: {start}")

        return int(point[0]), int(point[1])

    @staticmethod
    def __compute_additional_offset(size: dict, args: list[str]) -> Tuple[int, int]:
        x: Tuple[int, str] = (
            ElementActionHandler.__split_to_value_and_units(args[0] if args else None))
        y: Tuple[int, str] = (
            ElementActionHandler.__split_to_value_and_units(args[1] if len(args) > 1 else None))
        return ElementActionHandler.__compute_offset(size, x, y)

    @staticmethod
    def __compute_offset(size: dict, x: Tuple[int, str], y: Tuple[int, str]) -> Tuple[int, int]:

        if x[1] == 'px':
            x = x[0]
        elif x[1] == '%':
            width = size['width']
            x = int(width * x[0] / 100)
        else:
            raise ValueError(f"Invalid unit: {x[0]}{x[1]}")
        if y[1] == 'px':
            y = y[0]
        elif y[1] == '%':
            height = size['height']
            y = int(height * y[0] / 100)
        else:
            raise ValueError(f"Invalid unit: {y[0]}{y[1]}")
        return x, y

    @staticmethod
    def __split_to_value_and_units(text: str) -> Tuple[int, str]:
        if text and text.endswith('px'):
            return int(text[:-2]), 'px'
        if text and text.endswith('%'):
            return int(text[:-1]), '%'
        if text:
            return int(text), 'px'
        return 0, 'px'

    @staticmethod
    def __print_element_attr(exception: Exception, element: WebElement, attribute_name: str):
        if element:
            logger.debug(f'After {type(exception)}, printing element attribute: {attribute_name}'
                         f'\n{"="*64}\n{element.get_attribute(attribute_name)}\n{"="*64}')
            return
        logger.debug(f'After {type(exception)}, printing element: \n{"="*64}\n{element}\n{"="*64}')
