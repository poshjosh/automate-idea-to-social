from ..web.test_browser_automator import TestBrowserAutomator
from ....main.aideas.agent.browser_agent import BrowserAgent
from ....main.aideas.event.event_handler import EventHandler


class TestBrowserAgent(BrowserAgent):
    @staticmethod
    def of_config(agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any]) -> 'BrowserAgent':
        browser_automator = TestBrowserAutomator.of(app_config, agent_name, agent_config)
        interval_seconds: int = agent_config.get('interval-seconds', 0)
        return TestBrowserAgent(agent_name, agent_config, browser_automator, interval_seconds)

    def without_events(self) -> 'BrowserAgent':
        browser_automator = self.get_browser_automator().with_event_handler(EventHandler.noop())
        return TestBrowserAgent(
            self.get_name(), self.get_config(), browser_automator, self.get_interval_seconds())
