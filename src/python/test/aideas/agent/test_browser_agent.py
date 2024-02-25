from ..web.test_browser_automator import TestBrowserAutomator
from ....main.aideas.agent.browser_agent import BrowserAgent


class TestBrowserAgent(BrowserAgent):
    @staticmethod
    def of_config(config: dict[str, any], agent_config: dict[str, any]) -> 'BrowserAgent':
        browser_automator = TestBrowserAutomator.of(config, agent_config)
        interval_seconds: int = agent_config.get('interval-seconds', 0)
        return TestBrowserAgent(browser_automator, agent_config, interval_seconds)
