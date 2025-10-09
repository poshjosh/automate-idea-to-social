import logging
from typing import Union

from .agent import INTERVAL_KEY
from .automator_agent import AutomatorAgent
from ..web.browser_automator import BrowserAutomator

logger = logging.getLogger(__name__)


class BrowserAutomatorAgent(AutomatorAgent):
    @classmethod
    def of_config(cls,
                  agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any],
                  dependencies: Union[dict[str, AutomatorAgent], None] = None) -> 'BrowserAutomatorAgent':
        browser_automator = BrowserAutomator.of(app_config, agent_name, agent_config)
        interval_seconds: int = agent_config.get(INTERVAL_KEY, 0)
        return cls(agent_name, agent_config, dependencies, browser_automator, interval_seconds)
