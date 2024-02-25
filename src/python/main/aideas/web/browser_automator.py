import logging
from typing import List, Union

from selenium.webdriver.remote.webelement import WebElement

from .element_search_config import ElementSearchConfig
from .element_selector import ElementSelector
from .webdriver_creator import WEB_DRIVER, WebDriverCreator
from ..action.action import Action
from ..action.action_result import ActionResult
from ..action.action_result_set import ActionResultSet
from ..action.element_action_config import ElementActionConfig
from ..action.element_action_handler import ElementActionHandler
from ..event.event_handler import EventHandler

logger = logging.getLogger(__name__)


class BrowserAutomator:
    @staticmethod
    def of(config: dict[str, any], agent_config: dict[str, any] = None) -> 'BrowserAutomator':
        web_driver = WebDriverCreator.create(config, agent_config)
        wait_timeout_seconds = config['browser']['chrome']["wait-timeout-seconds"]
        action_handler = ElementActionHandler(web_driver, wait_timeout_seconds)
        event_handler = EventHandler(action_handler)
        element_selector = ElementSelector.of(web_driver, wait_timeout_seconds)
        return BrowserAutomator(
            web_driver, wait_timeout_seconds, event_handler, element_selector, action_handler)

    def __init__(self,
                 web_driver: WEB_DRIVER,
                 wait_timeout_seconds: float,
                 event_handler: EventHandler,
                 element_selector: ElementSelector,
                 action_handler: ElementActionHandler):
        self.__webdriver = web_driver
        self.__wait_timeout_seconds = 0 if wait_timeout_seconds is None else wait_timeout_seconds
        self.__event_handler = event_handler
        self.__element_selector = element_selector
        self.__action_handler = action_handler

    def get_event_handler(self) -> EventHandler:
        return self.__event_handler

    def act_on_elements(self,
                        stages_config: dict[str, any],
                        stage_name: str,
                        action_values: dict[str, any]) -> ActionResultSet:
        stage_config: dict[str, any] = stages_config[stage_name]
        link: str = stage_config.get('url', self.__webdriver.current_url)

        body_elements: List[WebElement] = self.__element_selector.load_page_bodies(link)

        ui_config: dict[str, any] = stage_config['ui']

        result_set: ActionResultSet = ActionResultSet()

        for key in ui_config.keys():
            if key == ElementActionConfig.DEFAULT_ACTIONS_KEY:
                continue

            result_set.add_all(self.act_on_element(
                body_elements[0], ui_config, key, action_values))

        return result_set.close()

    """
        ########################
        #   UI config format   #
        ########################
        # default-actions: # optional
        #   - click
        #   - wait 2
        # element-0: //*[@id="element-0"]
        # element-1: //*[@id="element-1"] 
    """
    def act_on_element(self,
                       body_element: WebElement,
                       ui_config: dict[str, any],
                       element_name: str,
                       action_values: dict[str, any],
                       trials: int = 1) -> ActionResultSet:
        element_actions: list[str] = ElementActionConfig.get(ui_config, element_name)
        element_config: dict[str, any] = ui_config[element_name]
        search_config = ElementSearchConfig.of(element_config)

        result_set = ActionResultSet.none()
        exception = None
        try:
            timeout = self.__wait_timeout_seconds if type(element_config) is not dict \
                else element_config.get('wait-timeout-seconds', self.__wait_timeout_seconds)

            selector = self.__element_selector.with_timeout(timeout)
            found: WebElement = selector.select_element(
                body_element, element_name, search_config)

            result_set: ActionResultSet = self.execute_all_actions(
                found, timeout, element_name, element_actions, action_values)
        except Exception as ex:
            exception = ex

        if result_set.is_successful():
            return result_set

        def on_retry(_trials: int) -> ActionResultSet:
            return (self.act_on_element
                    (body_element, ui_config, element_name, action_values, _trials))

        # This will return an onerror based result set
        return self.__event_handler.on_execution_error(
            exception, result_set, ui_config, element_name, on_retry, trials)

    def execute_all_actions(self,
                            element: Union[WebElement, None],
                            wait_timeout_secs: float,
                            target_id: str,
                            action_signatures: list[str],
                            action_values: Union[dict[str, any], None]) -> ActionResultSet:
        result_set = ActionResultSet()
        action_handler = self.__action_handler.with_timeout(wait_timeout_secs)
        for action_signature in action_signatures:
            action = Action.of(target_id, action_signature, action_values)
            result: ActionResult = action_handler.execute_on(action, element)
            result_set.add(result)
        return result_set

    def quit(self):
        self.__webdriver.quit()
