import logging
import os.path
from enum import unique
from typing import TypeVar, Union

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as WaitCondition
from selenium.webdriver.support.wait import WebDriverWait

from ..action.action import Action
from ..action.action_handler import ActionHandler, execute_for_result, BaseActionId
from ..action.action_result import ActionResult
from ..env import get_cookies_file_path

logger = logging.getLogger(__name__)

WEB_DRIVER = TypeVar("WEB_DRIVER", bound=Union[webdriver.Chrome, webdriver.Remote])
ALERT_ACTION = TypeVar("ALERT_ACTION", bound=Union['accept', 'dismiss'])


@unique
class BrowserActionId(BaseActionId):
    ACCEPT_ALERT = ('accept_alert', False)
    DELETE_COOKIES = ('delete_cookies', False)
    DISMISS_ALERT = ('dismiss_alert', False)
    EXECUTE_SCRIPT = 'execute_script'
    REFRESH = ('refresh', False)


class BrowserActionHandler(ActionHandler):
    @staticmethod
    def to_action_id(action: str) -> BaseActionId:
        try:
            return ActionHandler.to_action_id(action)
        except ValueError:
            return BrowserActionId(action)

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
        if key.endswith('alert'):  # accept_alert|dismiss_alert
            result = self.__handle_alert(action)
        elif key == BrowserActionId.DELETE_COOKIES.value:
            result = self.__delete_cookies(action)
        elif key == BrowserActionId.EXECUTE_SCRIPT.value:
            result = self.__execute_script(action)
        elif key == BrowserActionId.REFRESH.value:
            result = self.__refresh(action)
        else:
            return super()._execute(key, action)
        logger.debug(f'{result}')
        return result

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
                raise ValueError(f"Unsupported: {action}")
        except TimeoutException:
            logger.debug(f"Timed out waiting for alert. {action}")

        return ActionResult(action, True)

    def __delete_cookies(self, action: Action) -> ActionResult:
        def delete_all_cookies(file):
            self.__web_driver.delete_all_cookies()
            if os.path.exists(file):
                os.remove(file)
                logger.debug(f"Deleted cookies file: {file}")
        cookies_file = get_cookies_file_path(action.get_agent_name())
        return execute_for_result(delete_all_cookies, cookies_file, action)

    def __execute_script(self, action: Action) -> ActionResult:
        def execute(script: str):
            return self.__web_driver.execute_script(script)

        return execute_for_result(execute, ' '.join(action.get_args()), action)

    def __refresh(self, action: Action) -> ActionResult:
        self.__web_driver.refresh()
        return ActionResult(action, True)

    def get_web_driver(self) -> WEB_DRIVER:
        return self.__web_driver

    def get_wait_timeout_seconds(self) -> float:
        return self.__wait_timeout_seconds
