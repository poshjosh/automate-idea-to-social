import logging
import time
from enum import unique
from typing import Tuple

from selenium.common import StaleElementReferenceException, ElementClickInterceptedException, \
    ElementNotInteractableException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.remote.webelement import WebElement

from .action_handler import BaseActionId, TARGET
from .browser_action_handler import BrowserActionHandler, WEB_DRIVER
from ..action.action import Action
from ..action.action_result import ActionResult
from ..run_context import RunContext
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

    def execute_on(
            self, run_context: RunContext, action: Action, target: TARGET = None) -> ActionResult:
        result: ActionResult = ActionResult.none()
        key = action.get_name_without_negation() if action.is_negation() else action.get_name()
        try:
            if isinstance(target, ReloadableWebElement):
                # We use the actual web element for the action
                # When we used the ReloadableWebElement, the action fails with message:
                # TypeError: Object of type ReloadableWebElement is not JSON serializable
                result = self.__execute_on(run_context, action, key, target.load())
            elif isinstance(target, WebElement):
                result = self.__execute_on(run_context, action, key, target)
            elif target is None:
                result = super().execute_on(run_context, action, target)
            else:
                raise ValueError(f"Invalid target type: {type(target)}")

        except (StaleElementReferenceException, ElementNotInteractableException) as ex:
            if isinstance(target, ReloadableWebElement):
                logger.warning(f'Encountered {ex.__class__.__name__}'
                               f', will reload element and retry: {action}')
                try:
                    result = self.__execute_on(run_context, action, key, target.reload())
                except Exception as ex:
                    ElementActionHandler.throw_error(ex, action)
            else:
                ElementActionHandler.throw_error(ex, action)
        except Exception as ex:
            ElementActionHandler.throw_error(ex, action)

        if action.is_negation():
            result = result.flip()

        return result

    def __execute_on(self,
                     run_context: RunContext,
                     action: Action,
                     key: str,
                     element: WebElement) -> ActionResult:
        try:
            return self.__do_execute_on(run_context, action, key, element)
        except Exception as ex:
            self.__print_element_attr(ex, element, 'outerHTML')
            raise ex

    def __do_execute_on(self,
                        run_context: RunContext,
                        action: Action,
                        key: str,
                        element: WebElement) -> ActionResult:
        driver = self.get_web_driver()
        result: any = None
        if key == ElementActionId.CLEAR_TEXT.value:
            element.send_keys(Keys.CONTROL, 'a')
            element.send_keys(Keys.DELETE)
            element.clear()  # May not work under certain conditions, so we try the following
        elif key == ElementActionId.CLICK.value:
            click_on_element: bool = action.get_arg_bool(True)
            target: WebElement = element if click_on_element is True else None
            self.__click(driver, target)
        elif key == ElementActionId.CLICK_AND_HOLD.value:
            ActionChains(driver).click_and_hold(element).perform()
        elif key == ElementActionId.CLICK_AND_HOLD_CURRENT_POSITION.value:
            ActionChains(driver).click_and_hold(None).perform()
        elif key == ElementActionId.ENTER.value:
            element.send_keys(Keys.ENTER)
        elif key == ElementActionId.ENTER_TEXT.value:
            element.send_keys(action.get_arg_str())
            result = action.get_arg_str()
        elif key == ElementActionId.EXECUTE_SCRIPT_ON.value:
            result = driver.execute_script(action.get_arg_str(), element)
        elif key == ElementActionId.GET_ATTRIBUTE.value:
            result = element.get_attribute(action.get_arg_str())
        elif key == ElementActionId.GET_TEXT.value:
            text = element.text
            result = text if not text else text.strip()
        elif key == ElementActionId.IS_DISPLAYED.value:
            success = element.is_displayed()
            result = ActionResult(action, success, success)
        elif key == ElementActionId.MOVE_TO_ELEMENT.value:
            ActionChains(driver).move_to_element(element).perform()
        elif key == ElementActionId.MOVE_TO_ELEMENT_OFFSET.value:
            self.__move_to_element_offset(self.get_web_driver(), action, element)
        elif key == ElementActionId.RELEASE.value:
            on_element: bool = action.get_arg_bool(True)
            ActionChains(driver).release(element if on_element is True else None).perform()
        elif key == ElementActionId.SEND_KEYS.value:
            for char in action.get_arg_str():
                element.send_keys(char)
                time.sleep(0.5)
            result = action.get_arg_str()
        else:
            return super()._execute(run_context, action, key)  # Success state has already been printed
        result = result if isinstance(result, ActionResult) else ActionResult.success(action, result)
        logger.debug(f'{result}')
        return result

    @staticmethod
    def __click(webdriver: WEB_DRIVER, element: WebElement = None):
        try:
            # Click means only click. We have a separate action for move_to_element
            # Adding move_to_element here will disrupt some reasonable expectations
            # For example. When we move to bottom right before clicking,
            # we don't expect additional movements before the click is effected.
            # If you need to, explicitly specify move_to_element before click
            if element is None:
                ActionChains(webdriver).click().perform()
            else:
                element.click()
        except ElementClickInterceptedException as ex:
            logger.warning('Element click intercepted. Will try clicking via JavaScript.')
            if element:
                webdriver.execute_script("arguments[0].click();", element)
            else:
                raise ex

    @staticmethod
    def __move_to_element_offset(webdriver, action: Action, element: WebElement):
        start: str = action.get_first_arg_as_str()
        if not start:
            raise ValueError("No start point provided for move_to_element_offset")

        element_size: dict = element.size

        offset_from_center: Tuple[int, int] = (0, 0) if start == 'center' \
            else ElementActionHandler.__compute_offset_relative_to_center(element_size, start)

        args: list[str] = action.get_args_as_str_list()
        additional_offset: Tuple[int, int] = (
            ElementActionHandler.__compute_additional_offset(element_size, args[1:]))

        # We add the offset provided by the user
        x = offset_from_center[0] + additional_offset[0]
        y = offset_from_center[1] + additional_offset[1]

        logger.debug(f"Element size: {element_size}, "
                     f"offset from center: {offset_from_center}, "
                     f"additional offset: {additional_offset}, "
                     f"total offset from center: ({x}, {y})")
        ActionChains(webdriver).move_to_element_with_offset(element, x, y).perform()

    @staticmethod
    def __compute_offset_relative_to_center(size: dict, start: str) -> Tuple[int, int]:
        width = size['width']
        height = size['height']

        half_w = width/2
        half_h = height/2

        # We calculate how much to move from the center of the element to these positions
        # x-axis increases towards the right, y-axis increases towards the bottom
        if start == "top-left":
            point = -half_w, -half_h
        elif start == "top-right":
            point = half_w, -half_h
        elif start == "bottom-left":
            point = -half_w, half_h
        elif start == "bottom-right":
            point = half_w, half_h
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
