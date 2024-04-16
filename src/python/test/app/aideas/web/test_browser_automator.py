from collections import OrderedDict
from typing import Callable

from ..action.test_element_action_handler import TestElementActionHandler
from ..web.test_element_selector import TestElementSelector
from ..test_functions import create_webdriver
from .....main.app.aideas.config import TIMEOUT_KEY, Name
from .....main.app.aideas.event.event_handler import EventHandler
from .....main.app.aideas.run_context import RunContext
from .....main.app.aideas.web.browser_automator import BrowserAutomator


class TestBrowserAutomator(BrowserAutomator):
    @classmethod
    def of(cls,
           app_config: dict[str, any],
           agent_name: str,
           agent_config: dict[str, any] = None,
           run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None] = None) \
            -> 'BrowserAutomator':
        web_driver = create_webdriver(app_config, agent_name)
        wait_timeout_seconds = app_config['browser']['chrome'][TIMEOUT_KEY]
        element_selector = TestElementSelector.of(web_driver, agent_name, wait_timeout_seconds)
        action_handler = TestElementActionHandler(element_selector, wait_timeout_seconds)
        event_handler = EventHandler(action_handler)
        return cls(
            web_driver, wait_timeout_seconds, agent_name,
            element_selector, action_handler, event_handler,
            run_stages)
