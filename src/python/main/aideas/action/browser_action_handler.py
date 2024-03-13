import logging
from typing import TypeVar, Union

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as WaitCondition
from selenium.webdriver.support.wait import WebDriverWait

from ..action.action import Action
from ..action.action_handler import ActionHandler, execute_for_result
from ..action.action_result import ActionResult

logger = logging.getLogger(__name__)

WEB_DRIVER = TypeVar("WEB_DRIVER", bound=Union[webdriver.Chrome, webdriver.Remote])
ALERT_ACTION = TypeVar("ALERT_ACTION", bound=Union['accept', 'dismiss'])


class BrowserActionHandler(ActionHandler):
    def __init__(self,
                 web_driver: WEB_DRIVER,
                 wait_timeout_seconds: float):
        self.__web_driver = web_driver
        self.__wait_timeout_seconds = wait_timeout_seconds

    def with_timeout(self, timeout: float) -> 'BrowserActionHandler':
        if timeout == self.__wait_timeout_seconds:
            return self
        return BrowserActionHandler(self.__web_driver, timeout)

    def _execute(self, key: str, action: Action) -> ActionResult:
        if key.endswith("alert"):  # accept_alert|dismiss_alert
            result = self.__handle_alert(action)
        elif key == "execute_script":
            result = self.__execute_script(action)
        elif key == "execute_script_on":
            result = self.__execute_script_on(action)
        elif key == "refresh":
            result = self.__refresh(action)
        else:
            return super()._execute(key, action)
        logger.debug(f'{result}')
        return result

    def get_web_driver(self) -> WEB_DRIVER:
        return self.__web_driver

    def get_wait_timeout_seconds(self) -> float:
        return self.__wait_timeout_seconds

    def __handle_alert(self, action: Action) -> ActionResult:
        how: str = action.get_name().split("_")[0]  # accept|dismiss
        value: str = action.get_first_arg('')
        timeout = self.__wait_timeout_seconds if (value is None or value == '') else float(value)
        try:
            WebDriverWait(self.__web_driver, timeout).until(
                WaitCondition.alert_is_present())
            alert: Alert = self.__web_driver.switch_to().alert()
            if how == 'accept':
                alert.accept()
            elif how == 'dismiss':
                alert.dismiss()
            else:
                return ActionResult(action, False, f"Unsupported: {action}")
        except TimeoutException:
            logger.debug(f"Timed out waiting for alert. {action}")

        return ActionResult(action, True)

    def __execute_script(self, action: Action) -> ActionResult:
        def execute(script: str):
            return self.__web_driver.execute_script(script)

        return execute_for_result(execute, ' '.join(action.get_args()), action)

    def __execute_script_on(self, action: Action) -> ActionResult:

        args: list = action.get_args()

        def execute_on(target: WebElement):
            return self.__web_driver.execute_script(args[0], target)

        return execute_for_result(execute_on, args[1], action)

    def __refresh(self, action: Action) -> ActionResult:
        self.__web_driver.refresh()
        return ActionResult(action, True)
