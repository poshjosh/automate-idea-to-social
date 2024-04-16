from collections import OrderedDict
import copy
import logging

from typing import Union, Callable

from selenium.webdriver.remote.webelement import WebElement

from .element_selector import ElementSelector, ElementNotFoundError
from .webdriver_creator import WEB_DRIVER, WebDriverCreator
from ..action.action import Action
from ..action.action_result import ActionResult
from ..action.action_signatures import element_action_signatures
from ..action.action_handler import ActionError
from ..action.element_action_handler import ElementActionHandler
from ..config import (AgentConfig, ConfigPath, Name, SearchConfigs,
                      TIMEOUT_KEY, WHEN_KEY, ON_START, merge_configs)
from ..result.result_set import ElementResultSet
from ..event.event_handler import EventHandler
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class BrowserAutomator:
    @classmethod
    def of(cls,
           app_config: dict[str, any],
           agent_name: str,
           agent_config: dict[str, any] = None,
           run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None] = None) \
            -> 'BrowserAutomator':
        # app_config['browser'].update(agent_config.get('browser', {}))
        app_config = copy.deepcopy(app_config)  # Don't update the original
        app_config['browser'] = merge_configs(
            agent_config.get('browser', {}), app_config['browser'], False)
        web_driver = WebDriverCreator.create(app_config)
        wait_timeout_seconds = app_config['browser']['chrome'].get(TIMEOUT_KEY, 20)
        element_selector = ElementSelector.of(web_driver, agent_name, wait_timeout_seconds)
        action_handler = ElementActionHandler(element_selector, wait_timeout_seconds)
        event_handler = EventHandler(action_handler)
        return cls(
            web_driver, wait_timeout_seconds, agent_name,
            element_selector, action_handler, event_handler,
            run_stages)

    def __init__(self,
                 web_driver: WEB_DRIVER,
                 wait_timeout_seconds: float,
                 agent_name: str,
                 element_selector: ElementSelector,
                 action_handler: ElementActionHandler,
                 event_handler: EventHandler,
                 run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None] = None):
        self.__webdriver = web_driver
        self.__wait_timeout_seconds = 0 if wait_timeout_seconds is None else wait_timeout_seconds
        self.__agent_name = agent_name
        self.__element_selector = element_selector
        self.__action_handler = action_handler
        self.__event_handler = event_handler
        self.__run_stages = run_stages
        self.__populate_result_set = True

    def without_results_update(self) -> 'BrowserAutomator':
        clone: BrowserAutomator = self.clone()
        clone.__populate_result_set = False
        return clone

    def without_events(self) -> 'BrowserAutomator':
        return self.with_event_handler(EventHandler.noop())

    def with_action_handler(self, action_handler: ElementActionHandler) -> 'BrowserAutomator':
        clone: BrowserAutomator = self.clone()
        clone.__action_handler = action_handler
        return clone

    def with_element_selector(self, element_selector: ElementSelector) -> 'BrowserAutomator':
        clone: BrowserAutomator = self.clone()
        clone.__element_selector = element_selector
        return clone

    def with_event_handler(self, event_handler: EventHandler) -> 'BrowserAutomator':
        clone: BrowserAutomator = self.clone()
        clone.__event_handler = event_handler
        return clone

    def with_stage_runner(
            self, run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None]) \
            -> 'BrowserAutomator':
        clone: BrowserAutomator = self.clone()
        clone.__run_stages = run_stages
        return clone

    def clone(self) -> 'BrowserAutomator':
        return self.__class__(
            self.__webdriver, self.__wait_timeout_seconds, self.__agent_name,
            self.__element_selector, self.__action_handler, self.__event_handler, self.__run_stages)

    def act_on_elements(self,
                        config: AgentConfig,
                        stage: Name,
                        run_context: RunContext) -> ElementResultSet:

        self.__load_page(config, stage, run_context)

        for stage_item in config.stage_item_names(stage):

            config_path: ConfigPath = ConfigPath.of(stage, stage_item)

            to_proceed = self.__may_proceed(config, config_path, run_context)

            if to_proceed is False:
                continue

            self.__act_on_element(config, config_path, run_context)

        return run_context.get_element_results(self.__agent_name, stage.get_id())

    def stage_may_proceed(self,
                          config: AgentConfig,
                          stage: Name,
                          run_context: RunContext) -> bool:
        self.__load_page(config, stage, run_context)
        return self.__may_proceed(config, ConfigPath.of(stage), run_context)

    def __load_page(self,
                    config: AgentConfig,
                    stage: Name,
                    run_context: RunContext):
        link: str = config.get_url(stage, self.__webdriver.current_url)
        self.__element_selector.load_page(link)
        run_context.set_current_url(link)

    def __may_proceed(self,
                      config: AgentConfig,
                      config_path: ConfigPath,
                      run_context: RunContext) -> bool:

        config_path = config_path.join(WHEN_KEY)

        condition = config.get(config_path)

        if not condition:
            return True

        try:
            success = self.without_events().without_results_update().__act_on_element(
                config, config_path, run_context).is_successful()
        except (ElementNotFoundError, ActionError) as ex:
            logger.debug(f'Error checking condition for {config_path}, \nCause: {ex}')
            success = False

        logger.debug(f'May proceed: {success}, {config_path}, due to condition: {condition}')
        return success

    def __act_on_element(self,
                         config: AgentConfig,
                         config_path: ConfigPath,
                         run_context: RunContext,
                         trials: int = 1) -> ElementResultSet:

        target_config: dict[str, any] = config.get(config_path)
        logger.debug(f"Acting on {config_path}")

        element_actions: list[str] = self.__get_actions(config, config_path)

        result = ElementResultSet.none()

        if not target_config and not element_actions:
            return result

        def do_retry(_trials: int) -> ElementResultSet:
            logger.debug(f"Retrying {config_path}")
            return self.__act_on_element(config, config_path, run_context, _trials)

        def do_run_stages(context: RunContext, agent_to_stages: OrderedDict[str, [Name]]):
            if not self.__run_stages:
                raise ValueError(f'Event: run_stages is not supported for {config_path}')
            self.__run_stages(context, agent_to_stages)

        exception = None
        try:

            self.__event_handler.handle_event(
                self.get_agent_name(), config, config_path,
                ON_START, run_context, do_run_stages)

            timeout: float = self.__get_timeout(target_config)

            element: WebElement = self.__select_element(target_config)

            run_context.set_current_element(element)

            if element_actions:
                result: ElementResultSet = self.__execute_all_actions(
                    config_path, element, timeout, element_actions, run_context)

                # Handle expectations if present
                self.__check_expectations(config, config_path, run_context, element, timeout)

        except (ElementNotFoundError, ActionError) as ex:
            # Error should be logged with more details at the stage level by browser agent.
            logger.debug(f"Error acting on {config_path} {type(ex)}")
            exception = ex

        result = self.__event_handler.handle_result_event(
            self.get_agent_name(), config, config_path, run_context,
            do_run_stages, do_retry, exception, result, trials)

        return ElementResultSet.none() if result is None else result

    @staticmethod
    def __get_actions(config: AgentConfig, config_path: ConfigPath) -> list[str]:
        target_parent_config = config.get(config_path[:-1])
        return [] if not target_parent_config \
            else element_action_signatures(target_parent_config, config_path.name().get_value())

    def __check_expectations(self,
                             config: AgentConfig,
                             config_path: ConfigPath,
                             run_context: RunContext,
                             element: WebElement,
                             timeout: float):
        expected = config.expected(config_path)
        if not expected:
            return

        selected = self.__select_element(expected, timeout)
        element = element if not selected else selected

        expectation_actions: list[str] = config.get_expectation_actions(config_path)
        logger.debug(f"Checking expectations: {expectation_actions}")
        if expectation_actions:
            # Since we use the same config_path as above, the
            # results of the expectation will be added to the
            # above results. This means if there is a failure
            # of expectation, the result set will also contain
            # the failure.
            self.__execute_all_actions(
                config_path, element, timeout, expectation_actions, run_context)

    def __select_element(self,
                         target_config: dict[str, any],
                         timeout: float = None) -> WebElement:
        if not timeout:
            timeout = self.__get_timeout(target_config)

        search_configs: SearchConfigs = SearchConfigs.of(target_config)

        return None if not search_configs or not search_configs.search_for() \
            else self.__element_selector.with_timeout(timeout).select_element(search_configs)

    def __get_timeout(self, target_config: dict[str, any]) -> float:
        return self.__wait_timeout_seconds if not isinstance(target_config, dict) \
            else target_config.get(TIMEOUT_KEY, self.__wait_timeout_seconds)

    def __execute_all_actions(self,
                              config_path: ConfigPath,
                              element: Union[WebElement, None],
                              wait_timeout_secs: float,
                              action_signatures: list[str],
                              run_context: RunContext) -> ElementResultSet:
        stage_id: str = config_path.stage().get_id()
        target_id: str = config_path.name().get_id()
        action_handler = self.__action_handler.with_timeout(wait_timeout_secs)

        result_set: ElementResultSet = ElementResultSet()
        for action_signature in action_signatures:
            action = Action.of(
                self.__agent_name, stage_id, target_id, action_signature, run_context)

            result: ActionResult = action_handler.execute_on(action, element)

            if self.__populate_result_set is True:
                run_context.add_action_result(self.__agent_name, stage_id, result)
            else:
                result_set.add(result)

        if self.__populate_result_set is True:
            return run_context.get_element_results(self.__agent_name, stage_id)
        else:
            return result_set

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
