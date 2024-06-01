import logging
from typing import Union

from .agent import Agent, INTERVAL_KEY
from ..web.browser_automator import BrowserAutomator

logger = logging.getLogger(__name__)


class BrowserAgent(Agent):
    @classmethod
    def of_config(cls,
                  agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any],
                  dependencies: Union[dict[str, Agent], None] = None) -> 'BrowserAgent':
        browser_automator = BrowserAutomator.of(app_config, agent_name, agent_config)
        interval_seconds: int = agent_config.get(INTERVAL_KEY, 0)
        return cls(agent_name, agent_config, dependencies, browser_automator, interval_seconds)
