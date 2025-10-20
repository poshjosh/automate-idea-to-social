import logging

from .agent import Agent, ExecutionError, INTERVAL_KEY
from .automator import Automator, AutomationError
from ..agent.event_handler import EventHandler
from ..config import AgentConfig, Name
from ..result.result_set import ElementResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class AutomatorAgent(Agent):
    @classmethod
    def of_config(cls,
                  agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any],
                  dependencies: dict[str, 'Agent'] = None) -> 'AutomatorAgent':
        automator = Automator.of(app_config, agent_name, agent_config)
        interval_seconds: int = agent_config.get(INTERVAL_KEY, 0)
        return cls(agent_name, agent_config, dependencies, automator, interval_seconds)

    def __init__(self,
                 name: str,
                 agent_config: dict[str, any],
                 dependencies: dict[str, 'Agent'] = None,
                 automator: Automator = None,
                 interval_seconds: int = 0):
        super().__init__(name, agent_config, dependencies,
                         EventHandler.noop() if automator is None \
                             else automator.get_event_handler(), interval_seconds)
        self.__automator = None if automator is None \
            else automator.with_stage_runner(self._run_stages_without_events)

    def close(self):
        self.__automator.quit()

    def without_events(self) -> 'AutomatorAgent':
        clone: AutomatorAgent = self.clone()
        clone.__automator = self.__automator.without_events()
        return clone

    def with_automator(self, automator: Automator) -> 'AutomatorAgent':
        clone: AutomatorAgent = self.clone()
        clone.__automator = automator
        return clone

    def clone(self) -> 'AutomatorAgent':
        return self.__class__(self.get_name(), self.get_config().to_dict(),
                              self._get_dependencies(), self.__automator, self.get_interval_seconds())

    def create_dependency(self, name: str, config: dict[str, any]) -> 'AutomatorAgent':
        return self.__class__(name, config, None, self.__automator, self.get_interval_seconds())

    def _execute(self,
                 config: AgentConfig,
                 stage: Name,
                 run_context: RunContext) -> ElementResultSet:
        try:
            return self.__automator.act_on_elements(config, stage, run_context)
        except AutomationError as ex:
            raise ExecutionError() from ex

    def get_automator(self) -> Automator:
        return self.__automator

    def get_event_handler(self) -> EventHandler:
        return self.__automator.get_event_handler()
