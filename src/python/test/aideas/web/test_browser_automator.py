from ..action.test_element_action_handler import TestElementActionHandler
from ..web.test_element_selector import TestElementSelector
from ....main.aideas.event.event_handler import EventHandler
from ....main.aideas.web.browser_automator import BrowserAutomator
from ....main.aideas.web.webdriver_creator import WebDriverCreator


class TestBrowserAutomator(BrowserAutomator):
    @staticmethod
    def of(config: dict[str, any],
           agent_name: str,
           agent_config: dict[str, any] = None) -> 'BrowserAutomator':
        web_driver = WebDriverCreator.create(config)
        wait_timeout_seconds = config['browser']['chrome']["wait-timeout-seconds"]
        action_handler = TestElementActionHandler(web_driver, wait_timeout_seconds)
        event_handler = EventHandler(action_handler)
        element_selector = TestElementSelector.of(web_driver, agent_name, wait_timeout_seconds)
        return TestBrowserAutomator(
            web_driver, wait_timeout_seconds, agent_name,
            event_handler, element_selector, action_handler)

    def with_event_handler(self, event_handler: EventHandler) -> 'BrowserAutomator':
        return TestBrowserAutomator(
            self.get_web_driver(), self.get_wait_timeout_seconds(), self.get_agent_name(),
            event_handler, self.get_element_selector(), self.get_action_handler())
