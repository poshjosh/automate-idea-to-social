import logging
from collections import OrderedDict
from typing import List, Union

from selenium.webdriver.remote.webelement import WebElement

from .element_selector import ElementNotFoundError, ElementSelector
from .webdriver_creator import WEB_DRIVER, WebDriverCreator
from ..action.action import Action
from ..action.action_result import ActionResult
from ..action.action_signatures import element_action_signatures
from ..action.element_action_handler import ElementActionHandler
from ..agent.agent_name import AgentName
from ..config import AgentConfig, Name, SearchConfig, WHEN_KEY
from ..result.result_set import ElementResultSet
from ..event.event_handler import EventHandler, ON_START
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class BrowserAutomator:
    @staticmethod
    def of(app_config: dict[str, any],
           agent_name: str,
           agent_config: dict[str, any] = None) -> 'BrowserAutomator':
        web_driver = WebDriverCreator.create(app_config, AgentName.YOUTUBE == agent_name)
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
                        config: AgentConfig,
                        stage: Name,
                        run_context: RunContext) -> ElementResultSet:

        body_elements: List[WebElement] = self.__load_page_bodies(config, stage, run_context)

        for stage_item in config.stage_item_names(stage):

            path = config.path(stage.id, stage_item)

            to_proceed = self.__may_proceed(config, path, body_elements[0], run_context)

            if not to_proceed:
                continue

            self.__act_on_element(config, path, body_elements[0], run_context)

        return run_context.get_element_results(self.__agent_name, stage.id)

    def stage_may_proceed(self,
                          config: AgentConfig,
                          stage: Name,
                          run_context: RunContext) -> bool:
        page_bodies: List[WebElement] = self.__load_page_bodies(config, stage, run_context)
        return self.__may_proceed(
            config, config.path(stage.id), page_bodies[0], run_context)

    def __load_page_bodies(self,
                           config: AgentConfig,
                           stage: Name,
                           run_context: RunContext) -> List[WebElement]:
        link: str = config.get_url(stage, self.__webdriver.current_url)
        body_elements: List[WebElement] = self.__element_selector.load_page_bodies(link)
        run_context.set_current_url(link)
        return body_elements

    def __may_proceed(self,
                      config: AgentConfig,
                      path: [str],
                      body_element: WebElement,
                      run_context: RunContext) -> bool:

        path = [e for e in path]  # Use a copy
        path.append(WHEN_KEY)

        condition = config.get(path)

        if not condition:
            return True

        path_str = f'@{".".join(path)}'

        try:
            success = self.__act_on_element(
                config, path, body_element, run_context).is_successful()
        except Exception as ex:
            logger.debug(f'Error checking condition for: {path_str}, \nCause: {ex}')
            success = False

        logger.debug(f'May proceed: {success}, {path_str}, due to condition: {condition}')
        return success

    def __act_on_element(self,
                         config: AgentConfig,
                         path: [str],
                         body_element: WebElement,
                         run_context: RunContext,
                         trials: int = 1) -> ElementResultSet:

        stage_id = path[1]
        key = path[-1]

        element_config: dict[str, any] = config.get(path)

        parent_config = config.get(path[:-1])
        element_actions: list[str] = [] if not parent_config \
            else element_action_signatures(parent_config, key)

        result = ElementResultSet.none()

        if not element_config and not element_actions:
            return result

        def retry_event(_trials: int) -> ElementResultSet:
            return self.__act_on_element(config, path, body_element, run_context, _trials)

        def run_stages_event(context: RunContext,
                             agent_to_stages: OrderedDict[str, [Name]]):
            raise ValueError(f'Event: run_stages is not supported for: {".".join(path)}')

        search_config = SearchConfig.of(element_config)

        exception = None
        try:

            self.__event_handler.handle_event(
                path, ON_START, config, run_stages_event, run_context)

            timeout = self.__wait_timeout_seconds if type(element_config) is not dict \
                else element_config.get('wait-timeout-seconds', self.__wait_timeout_seconds)

            selector = self.__element_selector.with_timeout(timeout)
            element: WebElement = None if search_config is None else selector.select_element(
                body_element, key, search_config)
            
            if search_config is not None and search_config.search_for_needs_reordering():
                search_for = search_config.reorder_search_for()
                logger.debug(f"For @{'.'.join(path)} search-for re-ordered to:\n{search_for}")

            if element_actions:
                result: ElementResultSet = self.__execute_all_actions(
                    stage_id, element, timeout, key, element_actions, run_context)
        except ElementNotFoundError as ex:
            exception = ex

        result = self.__event_handler.handle_result_event(
            path, exception, result, config, retry_event, run_stages_event, run_context, trials)

        return ElementResultSet.none() if result is None else result

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
