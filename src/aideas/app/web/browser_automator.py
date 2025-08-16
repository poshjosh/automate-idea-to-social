from collections import OrderedDict
import logging
from enum import unique

from typing import Callable, Union

from selenium.webdriver.remote.webelement import WebElement

from .element_selector import ElementSelector
from .webdriver_creator import WEB_DRIVER, WebDriverCreator
from ..action.action import Action
from ..action.action_handler import ActionHandler
from ..action.browser_action_handler import BrowserActionId, BrowserActionHandler
from ..action.element_action_handler import ElementActionHandler
from ..action.variable_parser import get_run_arg_replacement
from ..agent.automator import Automator, AutomationListener, AutomationEvent
from ..agent.event_handler import EventHandler
from ..config import AgentConfig, ConfigPath, Name, SearchConfigs, BrowserConfig, RunArg
from ..result.result_set import ElementResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)


@unique
class BrowserAutomationEvent(AutomationEvent):
    PAGE_LOADED = ("PAGE_LOADED", False)

# always|never|onerror|onfailure|onsuccess
# always and never are exclusive. The rest may be combined with each other.
_SAVE_SCREENS_ALWAYS = "always"
_SAVE_SCREENS_NEVER = "never"
_SAVE_SCREENS_ON_ERROR = "onerror"
_SAVE_SCREENS_ON_FAILURE = "onfailure"
_SAVE_SCREENS_ON_SUCCESS = "onsuccess"
_SAVE_SCREENS_ON_START = "onstart"

def _save_screens_arg(run_context: RunContext) -> str:
    def err_msg(opt: str) -> str:
        return f"Invalid {RunArg.SAVE_SCREENS.value} option. Option: `{opt}` cannot be combined with other options."
    arg = run_context.get_arg(RunArg.SAVE_SCREENS, _SAVE_SCREENS_NEVER)
    # We do this because, always and never are exclusive. The rest may be combined with each other.
    if _SAVE_SCREENS_ALWAYS != arg and _SAVE_SCREENS_ALWAYS in arg:
        raise ValueError(err_msg(_SAVE_SCREENS_ALWAYS))
    if _SAVE_SCREENS_NEVER != arg and _SAVE_SCREENS_NEVER in arg:
        raise ValueError(err_msg(_SAVE_SCREENS_NEVER))
    return arg

def _is_save_screens(run_context: RunContext, value: str) -> bool:
    return _save_screens_arg(run_context) == _SAVE_SCREENS_ALWAYS or value in _save_screens_arg(run_context)

class BrowserAutomationListener(AutomationListener):
    def __init__(self, agent_name: str, action_handler: BrowserActionHandler):
        self.__agent_name: str = agent_name
        self.__action_handler: BrowserActionHandler = action_handler

    def on_error(self, event: AutomationEvent, config_path: ConfigPath,
                 run_context: RunContext, exception: Exception):
        if _is_save_screens(run_context, _SAVE_SCREENS_ON_ERROR):
            self._on_event(event, config_path, run_context)

    def on_event(self, event: AutomationEvent, config_path: ConfigPath, run_context: RunContext):
        if _save_screens_arg(run_context) == _SAVE_SCREENS_ALWAYS:
            self._on_event(event, config_path, run_context)

    def on_start(self, event: AutomationEvent, config_path: ConfigPath, run_context: RunContext):
        if _is_save_screens(run_context, _SAVE_SCREENS_ON_START):
            self._on_event(event, config_path, run_context)

    def on_success(self, event: AutomationEvent, config_path: ConfigPath, run_context: RunContext,
                  result_set: ElementResultSet):
        if _is_save_screens(run_context, _SAVE_SCREENS_ON_SUCCESS):
            self._on_event(event, config_path, run_context)

    def on_failure(self, event: AutomationEvent, config_path: ConfigPath, run_context: RunContext,
                   result_set: ElementResultSet):
        if _is_save_screens(run_context, _SAVE_SCREENS_ON_FAILURE):
            self._on_event(event, config_path, run_context)

    def _on_event(self, event: AutomationEvent, config_path: ConfigPath, run_context: RunContext):
        self.__save_view(config_path, run_context, BrowserActionId.SAVE_SCREENSHOT, event)
        self.__save_view(config_path, run_context, BrowserActionId.SAVE_WEBPAGE, event)

    def __save_view(self,
                    config_path: ConfigPath,
                    run_context: RunContext,
                    action_id: BrowserActionId,
                    key: Union[AutomationEvent, str]):
        try:
            key: str = key.description if isinstance(key, AutomationEvent) else key
            stage_item: str = config_path.stage_item().id if config_path.is_stage_item() \
                else ""
            stage_item: str = f"{stage_item}-{key}" if stage_item else key
            action = Action.of(self.__agent_name, config_path.stage().id,
                               stage_item, action_id.value)
            self.__action_handler.execute(run_context, action)
        except Exception as ex:
            logger.warning(f"Failed execute action: {action_id.value}. Reason: {ex}")


class BrowserAutomator(Automator):
    @classmethod
    def of(cls,
           app_config: dict[str, any],
           agent_name: str,
           agent_config: dict[str, any] = None,
           run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None] = None) \
            -> 'BrowserAutomator':
        web_driver = WebDriverCreator.create(agent_name, BrowserConfig(agent_config.get('browser', {})))
        timeout_seconds = BrowserAutomator.get_agent_timeout(app_config, agent_config)
        element_selector = ElementSelector.of(web_driver, agent_name, timeout_seconds)
        action_handler = ElementActionHandler(element_selector, timeout_seconds)
        event_handler = EventHandler(action_handler)
        listener = BrowserAutomationListener(agent_name, action_handler)
        return cls(web_driver, timeout_seconds, agent_name, element_selector,
                   action_handler, event_handler, listener, run_stages)

    def __init__(self,
                 web_driver: WEB_DRIVER,
                 timeout_seconds: float,
                 agent_name: str,
                 element_selector: ElementSelector,
                 action_handler: ActionHandler,
                 event_handler: EventHandler,
                 listener: AutomationListener,
                 run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None] = None):
        super().__init__(
            timeout_seconds, agent_name, action_handler, event_handler, listener, run_stages)
        self.__webdriver = web_driver
        self.__element_selector = element_selector

    def quit(self):
        super().quit()
        self.__webdriver.quit()

    def with_element_selector(self, element_selector: ElementSelector) -> 'BrowserAutomator':
        clone: BrowserAutomator = self.clone()
        clone.__element_selector = element_selector
        return clone

    def clone(self) -> 'BrowserAutomator':
        return self.__class__(
            self.__webdriver, self.get_timeout_seconds(), self.get_agent_name(),
            self.__element_selector, self.get_action_handler(), self.get_event_handler(),
            self.get_listener(), self.get_run_stages())

    def act_on_elements(self,
                        config: AgentConfig,
                        stage: Name,
                        run_context: RunContext) -> ElementResultSet:
        self.__load_page(config, stage, run_context)

        return super().act_on_elements(config, stage, run_context)

    def stage_may_proceed(self,
                          config: AgentConfig,
                          stage: Name,
                          run_context: RunContext) -> bool:
        self.__load_page(config, stage, run_context)
        return super().stage_may_proceed(config, stage, run_context)

    def __load_page(self,
                    config: AgentConfig,
                    stage: Name,
                    run_context: RunContext):
        link: str = config.get_url(stage, self.__webdriver.current_url)

        page_loaded: bool = self.__element_selector.load_page(link)
        if page_loaded:
            self.get_listener().on_event(
                BrowserAutomationEvent.PAGE_LOADED, ConfigPath.of(stage), run_context)

        run_context.set_current_url(link)

    def _select_target(self,
                       target_config: dict[str, any],
                       config_path: ConfigPath,
                       run_context: RunContext,
                       timeout: float = None) -> WebElement:
        if not timeout:
            timeout = self._get_timeout(target_config)

        path: list[str] = config_path.agent_str_path_simplified(self.get_agent_name())

        def transform(text: str) -> str:
            return text if not path else str(get_run_arg_replacement(path, text, run_context))

        search_configs: SearchConfigs = SearchConfigs.of(target_config).transform_queries(transform)

        return None if not search_configs or not search_configs.search_for() \
            else self.__element_selector.with_timeout(timeout).select_element(search_configs)

    def get_element_selector(self) -> ElementSelector:
        return self.__element_selector
