import logging

from .agent import Agent, INTERVAL_KEY
from .event_handler import EventHandler
from ..config import Name, AgentConfig
from ..result.result_set import ElementResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)

class YoutubeApiAgent(Agent):
    @classmethod
    def of_config(cls,
                  agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any],
                  dependencies: dict[str, 'Agent'] = None) -> 'Agent':
        interval_seconds: int = agent_config.get(INTERVAL_KEY, 0)
        return cls(agent_name, agent_config, dependencies, EventHandler(), interval_seconds)

    def __init__(self,
                 name: str,
                 agent_config: dict[str, any],
                 dependencies: dict[str, 'Agent'] = None,
                 event_handler: EventHandler = EventHandler(),
                 interval_seconds: int = 0):
        super().__init__(name, agent_config, dependencies, event_handler, interval_seconds)

    def _execute(self,
                 config: AgentConfig,
                 stage: Name,
                 run_context: RunContext) -> ElementResultSet:
        """ Execute the YoutubeApiAgent logic. """
        pass
