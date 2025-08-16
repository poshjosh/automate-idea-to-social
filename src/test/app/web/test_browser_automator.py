from collections import OrderedDict
from typing import Callable

from test.app.action.test_element_action_handler import TestElementActionHandler
from test.app.web.test_element_selector import TestElementSelector
from test.app.test_functions import create_webdriver
from aideas.app.agent.automator import AutomationListener
from aideas.app.agent.event_handler import EventHandler
from aideas.app.config import Name
from aideas.app.run_context import RunContext
from aideas.app.web.browser_automator import BrowserAutomator


class TestBrowserAutomator(BrowserAutomator):
    @classmethod
    def of(cls,
           app_config: dict[str, any],
           agent_name: str,
           agent_config: dict[str, any] = None,
           run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None] = None) \
            -> 'BrowserAutomator':
        web_driver = create_webdriver(agent_name, agent_config)
        timeout_seconds = BrowserAutomator.get_agent_timeout(app_config, agent_config)
        element_selector = TestElementSelector.of(web_driver, agent_name, timeout_seconds)
        action_handler = TestElementActionHandler(element_selector, timeout_seconds)
        event_handler = EventHandler(action_handler)
        listener = AutomationListener()
        return cls(web_driver, timeout_seconds, agent_name, element_selector,
                   action_handler, event_handler, listener, run_stages)
