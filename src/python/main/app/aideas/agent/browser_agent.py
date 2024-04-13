from collections import OrderedDict
import logging
import time
from typing import Union

from .agent import Agent, AgentError
from ..config import AgentConfig, ConfigPath, Name, ON_START
from ..action.action_handler import ActionError
from ..result.result_set import ElementResultSet
from ..run_context import RunContext
from ..web.browser_automator import BrowserAutomator
from ..web.element_selector import ElementNotFoundError

logger = logging.getLogger(__name__)


class BrowserAgent(Agent):
    @staticmethod
    def of_config(agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any],
                  dependencies: Union[dict[str, Agent], None] = None) -> 'BrowserAgent':
        return BrowserAgent.of_dynamic(
            agent_name, app_config, agent_config, dependencies, BrowserAgent)

    @staticmethod
    def of_dynamic(agent_name: str,
                   app_config: dict[str, any],
                   agent_config: dict[str, any],
                   dependencies: Union[dict[str, Agent], None],
                   init) -> 'BrowserAgent':
        """
        See example usage below:
        highlight:: python
        code-block:: python
            class BrowserAgentSubclass(BrowserAgent):
                pass

            BrowserAgent.of_dynamic(config, agent_config, BrowserAgentSubclass)
        """
        browser_automator = BrowserAutomator.of(app_config, agent_name, agent_config)
        interval_seconds: int = agent_config.get('interval-seconds', 0)
        return init(agent_name, agent_config, dependencies, browser_automator, interval_seconds)

    def __init__(self,
                 name: str,
                 agent_config: dict[str, any],
                 dependencies: Union[dict[str, Agent], None],
                 browser_automator: BrowserAutomator,
                 interval_seconds: int = 0):
        super().__init__(name, agent_config, dependencies)
        self.__browser_automator = (browser_automator
                                    .with_stage_runner(self._run_stages_without_events))
        self.__event_handler = browser_automator.get_event_handler()
        self.__interval_seconds = interval_seconds

    def close(self):
        self.__browser_automator.quit()

    def create_dependency(self, name: str, config: dict[str, any]) -> 'BrowserAgent':
        return BrowserAgent(
            name, config, None,
            self.__browser_automator, self.__interval_seconds)

    def without_events(self) -> 'BrowserAgent':
        return BrowserAgent(self.get_name(), self.get_config().root(), self._get_dependencies(),
                            self.__browser_automator.without_events(), self.get_interval_seconds())

    def with_automator(self, automator: BrowserAutomator) -> 'BrowserAgent':
        return BrowserAgent(self.get_name(), self.get_config().root(), self._get_dependencies(),
                            automator, self.get_interval_seconds())

    def run_stage(self,
                  run_context: RunContext,
                  stage: Name) -> ElementResultSet:
        result = self.__run_stage(run_context, stage, 1)
        self.__sleep()
        return result

    def __run_stage(self,
                    run_context: RunContext,
                    stage: Name,
                    trials) -> ElementResultSet:

        config: AgentConfig = self.get_config()
        config_path: ConfigPath = ConfigPath.of(stage)

        logger.debug(f"Executing stage {config_path}")

        if config.get_actions(config_path):
            raise ValueError(f"actions are not supported at stage level. "
                             f"Current stage: {config_path}")

        def do_retry(_trials: int) -> ElementResultSet:
            logger.debug(f"Retrying {config_path}")
            return self.__run_stage(run_context, stage, _trials)

        exception = None
        result = ElementResultSet.none()
        try:

            to_proceed = self.__browser_automator.stage_may_proceed(config, stage, run_context)

            if to_proceed is False:
                return result

            self.__event_handler.handle_event(
                self.get_name(), config, config_path,
                ON_START, run_context, self._run_stages_without_events)

            result: ElementResultSet = self.__browser_automator.act_on_elements(
                config, stage, run_context)

        except (ElementNotFoundError, ActionError, AgentError) as ex:
            logger.debug(f"Error acting on {config_path}\n{str(ex)}")
            exception = ex

        result = self.__event_handler.handle_result_event(
            self.get_name(), config, config_path, run_context,
            self._run_stages_without_events, do_retry, exception, result, trials)

        return ElementResultSet.none() if result is None else result

    def _run_stages_without_events(
            self, context: RunContext, agent_to_stages: OrderedDict[str, [Name]]):
        logger.debug(f"Running stages {agent_to_stages}")
        # We don't want an infinite loop, so we run this event without events.
        self.without_events()._run_agent_stages(context, agent_to_stages)

    def __sleep(self):
        if self.__interval_seconds <= 0:
            return
        time.sleep(self.__interval_seconds)

    def get_browser_automator(self) -> BrowserAutomator:
        return self.__browser_automator

    def get_interval_seconds(self) -> int:
        return self.__interval_seconds
