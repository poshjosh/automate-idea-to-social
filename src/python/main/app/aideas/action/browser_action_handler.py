import logging
import os.path
from enum import unique
from typing import TypeVar, Union

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
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
    DISABLE_CURSOR = ('disable_cursor', False)
    DISMISS_ALERT = ('dismiss_alert', False)
    ENABLE_CURSOR = ('enable_cursor', False)
    EXECUTE_SCRIPT = 'execute_script'
    MOVE_BY_OFFSET = ('move_by_offset', False)
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
        elif key == BrowserActionId.DISABLE_CURSOR.value:
            result = self.__disable_cursor(action)
        elif key == BrowserActionId.ENABLE_CURSOR.value:
            result = self.__enable_cursor(action)
        elif key == BrowserActionId.EXECUTE_SCRIPT.value:
            result = self.__execute_script(action)
        elif key == BrowserActionId.MOVE_BY_OFFSET.value:
            result = self.__move_by_offset(action)
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

    def __disable_cursor(self, action: Action) -> ActionResult:
        # This is a hack.
        disable_cursor = """
                function disableCursor() {
                  var seleniumFollowerImg = document.getElementById('selenium_mouse_follower')
                  if (seleniumFollowerImg) {
                    document.body.removeChild(seleniumFollowerImg);
                  }
                };
        
                disableCursor();
        """

        def execute(script: str):
            self.get_web_driver().execute_script(script)

        return execute_for_result(execute, disable_cursor, action)

    def __enable_cursor(self, action: Action) -> ActionResult:
        # This is a hack.
        # See https://stackoverflow.com/questions/53900972/how-can-i-see-the-mouse-pointer-as-it-performs-actions-in-selenium
        enable_cursor = """
                function enableCursor() {
                  var seleniumFollowerImg = document.createElement("img");
                  seleniumFollowerImg.setAttribute('src', 'data:image/png;base64,'
                    + 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAeCAQAAACGG/bgAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAA'
                    + 'HsYAAB7GAZEt8iwAAAAHdElNRQfgAwgMIwdxU/i7AAABZklEQVQ4y43TsU4UURSH8W+XmYwkS2I0'
                    + '9CRKpKGhsvIJjG9giQmliHFZlkUIGnEF7KTiCagpsYHWhoTQaiUUxLixYZb5KAAZZhbunu7O/PKf'
                    + 'e+fcA+/pqwb4DuximEqXhT4iI8dMpBWEsWsuGYdpZFttiLSSgTvhZ1W/SvfO1CvYdV1kPghV68a3'
                    + '0zzUWZH5pBqEui7dnqlFmLoq0gxC1XfGZdoLal2kea8ahLoqKXNAJQBT2yJzwUTVt0bS6ANqy1ga'
                    + 'VCEq/oVTtjji4hQVhhnlYBH4WIJV9vlkXLm+10R8oJb79Jl1j9UdazJRGpkrmNkSF9SOz2T71s7M'
                    + 'SIfD2lmmfjGSRz3hK8l4w1P+bah/HJLN0sys2JSMZQB+jKo6KSc8vLlLn5ikzF4268Wg2+pPOWW6'
                    + 'ONcpr3PrXy9VfS473M/D7H+TLmrqsXtOGctvxvMv2oVNP+Av0uHbzbxyJaywyUjx8TlnPY2YxqkD'
                    + 'dAAAAABJRU5ErkJggg==');
                  seleniumFollowerImg.setAttribute('id', 'selenium_mouse_follower');
                  seleniumFollowerImg.setAttribute('style', 'position: absolute; z-index: 99999999999; pointer-events: none; left:0; top:0');
                  document.body.appendChild(seleniumFollowerImg);
                  document.addEventListener('mousemove', function (e) {
                    document.getElementById("selenium_mouse_follower").style.left = e.pageX + 'px';
                    document.getElementById("selenium_mouse_follower").style.top = e.pageY + 'px';
                  });  
                };
        
                enableCursor();
        """

        def execute(script: str):
            self.get_web_driver().execute_script(script)

        return execute_for_result(execute, enable_cursor, action)

    def __execute_script(self, action: Action) -> ActionResult:
        def execute(script: str):
            return self.__web_driver.execute_script(script)

        return execute_for_result(execute, action.get_arg_str(), action)

    def __move_by_offset(self, action: Action) -> ActionResult:
        def move_by_offset(offset: tuple[int, int]):
            ActionChains(self.__web_driver).move_by_offset(offset[0], offset[1]).perform()
        args = action.get_args()
        x: int = 0 if len(args) == 0 else int(args[0])
        y: int = 0 if len(args) < 2 else int(args[1])
        return execute_for_result(move_by_offset, (x, y), action)

    def __refresh(self, action: Action) -> ActionResult:
        self.__web_driver.refresh()
        return ActionResult(action, True)

    def get_web_driver(self) -> WEB_DRIVER:
        return self.__web_driver

    def get_wait_timeout_seconds(self) -> float:
        return self.__wait_timeout_seconds
