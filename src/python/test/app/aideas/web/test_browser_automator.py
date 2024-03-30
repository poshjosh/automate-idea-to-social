from ..action.test_element_action_handler import TestElementActionHandler
from ..web.test_element_selector import TestElementSelector
from ..test_functions import create_webdriver
from .....main.app.aideas.action.element_action_handler import ElementActionHandler
from .....main.app.aideas.config import TIMEOUT_KEY
from .....main.app.aideas.event.event_handler import EventHandler
from .....main.app.aideas.web.browser_automator import BrowserAutomator
from .....main.app.aideas.web.element_selector import ElementSelector


class TestBrowserAutomator(BrowserAutomator):
    @staticmethod
    def of(app_config: dict[str, any],
           agent_name: str,
           agent_config: dict[str, any] = None) -> 'BrowserAutomator':
        # app_config['browser'].update(agent_config.get('browser', {}))
        app_config['browser'] = BrowserAutomator._update(agent_config.get('browser', {}), app_config['browser'])
        web_driver = create_webdriver(app_config, agent_name)
        wait_timeout_seconds = app_config['browser']['chrome'][TIMEOUT_KEY]
        action_handler = TestElementActionHandler(web_driver, wait_timeout_seconds)
        event_handler = EventHandler(action_handler)
        element_selector = TestElementSelector.of(web_driver, agent_name, wait_timeout_seconds)
        return TestBrowserAutomator(
            web_driver, wait_timeout_seconds, agent_name,
            event_handler, element_selector, action_handler)

    def with_action_handler(self, action_handler: ElementActionHandler) -> 'BrowserAutomator':
        return TestBrowserAutomator(
            self.get_web_driver(), self.get_wait_timeout_seconds(), self.get_agent_name(),
            self.get_event_handler(), self.get_element_selector(), action_handler)

    def with_element_selector(self, element_selector: ElementSelector) -> 'BrowserAutomator':
        return TestBrowserAutomator(
            self.get_web_driver(), self.get_wait_timeout_seconds(), self.get_agent_name(),
            self.get_event_handler(), element_selector, self.get_action_handler())

    def with_event_handler(self, event_handler: EventHandler) -> 'BrowserAutomator':
        return TestBrowserAutomator(
            self.get_web_driver(), self.get_wait_timeout_seconds(), self.get_agent_name(),
            event_handler, self.get_element_selector(), self.get_action_handler())
