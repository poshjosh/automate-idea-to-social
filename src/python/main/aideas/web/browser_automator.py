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

        elem_parent_cfg: dict[str, any] = stage_config['ui']

        result_set: ActionResultSet = ActionResultSet()

        for key in elem_parent_cfg.keys():
            if key == ElementActionConfig.DEFAULT_ACTIONS_KEY:
                continue

            may_proceed = self.may_proceed(body_elements[0], elem_parent_cfg, key, action_values)

            if may_proceed is False:
                logger.debug(f"Skipping actions for: {key} due to specified condition")
                continue

            result_set.add_all(self.act_on_element(
                body_elements[0], elem_parent_cfg, key, action_values))

        return result_set.close()

    def may_proceed(self,
                    body_element: WebElement,
                    elem_parent_cfg: dict[str, any], element_name: str,
                    action_values: dict[str, any]) -> bool:
        # This key does not have to be unique, since it is not included in the result set
        when_key = 'when'
        when_config = None if type(elem_parent_cfg[element_name]) is str \
            else elem_parent_cfg[element_name].get(when_key)
        return True if when_config is None else self.act_on_element(
            body_element, elem_parent_cfg[element_name],
            when_key, action_values).is_successful()

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
                       elem_parent_cfg: dict[str, any],
                       element_name: str,
                       action_values: dict[str, any],
                       trials: int = 1) -> ActionResultSet:
        element_actions: list[str] = ElementActionConfig.get(elem_parent_cfg, element_name)
        element_config: dict[str, any] = elem_parent_cfg[element_name]
        search_config = ElementSearchConfig.of(element_config)

        result_set = ActionResultSet.none()
        exception = None
        try:
            timeout = self.__wait_timeout_seconds if type(element_config) is not dict \
                else element_config.get('wait-timeout-seconds', self.__wait_timeout_seconds)

            selector = self.__element_selector.with_timeout(timeout)
            element: WebElement = selector.select_element(
                body_element, element_name, search_config)

            result_set: ActionResultSet = self.execute_all_actions(
                element, timeout, element_name, element_actions, action_values)
        except Exception as ex:
            exception = ex

        def retry_action(_trials: int) -> ActionResultSet:
            return (self.act_on_element
                    (body_element, elem_parent_cfg, element_name, action_values, _trials))

        def run_stages_action(stage_names: [str]) -> ActionResultSet:
            raise ValueError(f"Event: run_stages is not supported for: {element_name}")

        event_name = 'onsuccess' if result_set.is_successful() else 'onerror'

        # This will return an onerror based result set
        return self.__event_handler.handle_event(
            event_name, exception, result_set, elem_parent_cfg,
            element_name, retry_action, run_stages_action, trials)

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
