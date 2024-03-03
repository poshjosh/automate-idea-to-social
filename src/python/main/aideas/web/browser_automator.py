import logging
from typing import List, Union

from selenium.webdriver.remote.webelement import WebElement

from .element_search_config import ElementSearchConfig
from .element_selector import ElementSelector
from .webdriver_creator import WEB_DRIVER, WebDriverCreator
from ..action.action import Action
from ..action.action_result import ActionResult
from ..action.action_signatures import DEFAULT_ACTIONS_KEY, element_action_signatures
from ..action.element_action_handler import ElementActionHandler
from ..config.name import Name
from ..result.element_result_set import ElementResultSet
from ..result.stage_result_set import StageResultSet
from ..event.event_handler import EventHandler
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class BrowserAutomator:
    @staticmethod
    def of(app_config: dict[str, any],
           agent_name: str,
           agent_config: dict[str, any] = None) -> 'BrowserAutomator':
        web_driver = WebDriverCreator.create(app_config, agent_config)
        wait_timeout_seconds = app_config['browser']['chrome']["wait-timeout-seconds"]
        action_handler = ElementActionHandler(web_driver, wait_timeout_seconds)
        event_handler = EventHandler(action_handler)
        element_selector = ElementSelector.of(web_driver, agent_name, wait_timeout_seconds)
        return BrowserAutomator(
            web_driver, wait_timeout_seconds, agent_name,
            event_handler, element_selector, action_handler)

    def __init__(self,
                 web_driver: WEB_DRIVER,
                 wait_timeout_seconds: float,
                 agent_name: str,
                 event_handler: EventHandler,
                 element_selector: ElementSelector,
                 action_handler: ElementActionHandler):
        self.__webdriver = web_driver
        self.__wait_timeout_seconds = 0 if wait_timeout_seconds is None else wait_timeout_seconds
        self.__agent_name = agent_name
        self.__event_handler = event_handler
        self.__element_selector = element_selector
        self.__action_handler = action_handler

    def with_event_handler(self, event_handler: EventHandler) -> 'BrowserAutomator':
        return BrowserAutomator(
            self.__webdriver, self.__wait_timeout_seconds, self.__agent_name,
            event_handler, self.__element_selector, self.__action_handler)

    def act_on_elements(self,
                        stages_config: dict[str, any],
                        stage_name: Name,
                        run_context: RunContext) -> ElementResultSet:
        stage_config: dict[str, any] = stages_config[stage_name.value]
        link: str = stage_config.get('url', self.__webdriver.current_url)

        body_elements: List[WebElement] = self.__element_selector.load_page_bodies(link)

        elem_parent_cfg: dict[str, any] = stage_config['ui']

        for key in elem_parent_cfg.keys():
            if key == DEFAULT_ACTIONS_KEY:
                continue

            to_proceed = self.__may_proceed(
                stage_name.alias, body_elements[0], elem_parent_cfg, key, run_context)

            if not to_proceed:
                logger.debug(f"Skipping actions for: "
                             f"{self.__path(stage_name.alias, key)} due to specified condition")
                continue

            self.__act_on_element(
                stage_name.alias, body_elements[0], elem_parent_cfg, key, run_context)

        return run_context.get_element_results(self.__agent_name, stage_name.alias)

    def __may_proceed(self,
                      stage_id: str,
                      body_element: WebElement,
                      elem_parent_cfg: dict[str, any], element_name: str,
                      run_context: RunContext) -> bool:
        # This key does not have to be unique, since it is not included in the result set
        when_key = 'when'
        when_config = None if type(elem_parent_cfg[element_name]) is str \
            else elem_parent_cfg[element_name].get(when_key)
        return True if when_config is None else self.__act_on_element(
            stage_id, body_element, elem_parent_cfg[element_name],
            when_key, run_context).is_successful()

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
    def __act_on_element(self,
                         stage_id: str,
                         body_element: WebElement,
                         elem_parent_cfg: dict[str, any],
                         element_name: str,
                         run_context: RunContext,
                         trials: int = 1) -> ElementResultSet:
        element_actions: list[str] = element_action_signatures(elem_parent_cfg, element_name)
        element_config: dict[str, any] = elem_parent_cfg[element_name]
        search_config = ElementSearchConfig.of(element_config)

        exception = None
        result = ElementResultSet.none()
        try:
            timeout = self.__wait_timeout_seconds if type(element_config) is not dict \
                else element_config.get('wait-timeout-seconds', self.__wait_timeout_seconds)

            selector = self.__element_selector.with_timeout(timeout)
            element: WebElement = None if search_config is None else selector.select_element(
                body_element, element_name, search_config)

            result: ElementResultSet = self.__execute_all_actions(
                stage_id, element, timeout, element_name, element_actions, run_context)
        except Exception as ex:
            exception = ex

        def retry_action(_trials: int) -> ElementResultSet:
            return self.__act_on_element(
                stage_id, body_element, elem_parent_cfg, element_name, run_context, _trials)

        def run_stages_action(context: RunContext, names: [str], aliases: [str]) -> StageResultSet:
            raise ValueError(f'Event: run_stages is not supported for: '
                             f'{self.__path(stage_id, element_name)}')

        result = self.__event_handler.handle_terminal_event(
            self.__agent_name, stage_id, exception, result, elem_parent_cfg,
            element_name, retry_action, run_stages_action, run_context, trials)

        return ElementResultSet.none() if result is None else result

    def __path(self, stage_id: str, element_name: str) -> str:
        return f'{self.__agent_name}.{stage_id}.{element_name}'

    def __execute_all_actions(self,
                              stage_id: str,
                              element: Union[WebElement, None],
                              wait_timeout_secs: float,
                              target_id: str,
                              action_signatures: list[str],
                              run_context: RunContext) -> ElementResultSet:
        action_handler = self.__action_handler.with_timeout(wait_timeout_secs)
        for action_signature in action_signatures:
            action = Action.of(
                self.__agent_name, stage_id, target_id, action_signature, run_context)
            result: ActionResult = action_handler.execute_on(action, element)
            run_context.add_action_result(self.__agent_name, stage_id, result)
        # Don't close yet
        return run_context.get_element_results(self.__agent_name, stage_id)

    def quit(self):
        self.__webdriver.quit()

    def get_web_driver(self) -> WEB_DRIVER:
        return self.__webdriver

    def get_wait_timeout_seconds(self) -> float:
        return self.__wait_timeout_seconds

    def get_agent_name(self) -> str:
        return self.__agent_name

    def get_event_handler(self) -> EventHandler:
        return self.__event_handler

    def get_element_selector(self) -> ElementSelector:
        return self.__element_selector

    def get_action_handler(self) -> ElementActionHandler:
        return self.__action_handler
