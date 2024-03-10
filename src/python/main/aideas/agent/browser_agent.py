from collections import OrderedDict
import logging
import time
from typing import Union

from .agent import Agent, AgentError
from ..config.name import Name
from ..event.event_handler import EventHandler, ON_START
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
        self.__browser_automator = browser_automator
        self.__event_handler = browser_automator.get_event_handler()
        self.__interval_seconds = interval_seconds

    def close(self):
        self.__browser_automator.quit()

    def create_dependency(self, name: str, config: dict[str, any]) -> 'BrowserAgent':
        return BrowserAgent(
            name, config, None,
            self.__browser_automator, self.__interval_seconds)

    def without_events(self) -> 'BrowserAgent':
        browser_automator = self.__browser_automator.with_event_handler(EventHandler.noop())
        return BrowserAgent(self.get_name(), self.get_config(), self._get_dependencies(),
                            browser_automator, self.get_interval_seconds())

    def run_stage(self,
                  run_context: RunContext,
                  stage_name: Name) -> ElementResultSet:
        result = self.__run_stage(run_context, stage_name, 1)
        self.__sleep()
        return result

    def __run_stage(self,
                    run_context: RunContext,
                    stage_name: Name,
                    trials) -> ElementResultSet:
        logger.debug(f"Executing stage: {stage_name}")

        def retry_event(_trials: int) -> ElementResultSet:
            return self.__run_stage(run_context, stage_name, _trials)

        def run_stages_event(context: RunContext,
                             agent_to_stages: OrderedDict[str, [Name]]):
            # We don't want an infinite loop, so we run this event without events.
            self.without_events()._run_agent_stages(context, agent_to_stages)

        stage_id: str = stage_name.id
        stage_config = self.get_stage_config(stage_name.value)

        exception = None
        result = ElementResultSet.none()
        try:

            to_proceed = self.__browser_automator.stage_may_proceed(
                stage_config, stage_id, run_context)

            if not to_proceed:
                return result

            self.__event_handler.handle_event(
                self.get_name(), stage_id, ON_START, stage_id,
                stage_config, run_stages_event, run_context)

            result: ElementResultSet = self.__browser_automator.act_on_elements(
                self.get_stages_config(), stage_name, run_context)

        except ElementNotFoundError as ex:
            exception = ex
        except AgentError as ex:
            exception = ex

        result = self.__event_handler.handle_result_event(
            self.get_name(), stage_name.id, exception, result, stage_id,
            stage_config, retry_event, run_stages_event, run_context, trials)

        return ElementResultSet.none() if result is None else result

    def __sleep(self):
        if self.__interval_seconds < 1:
            return
        time.sleep(self.__interval_seconds)

    def get_browser_automator(self) -> BrowserAutomator:
        return self.__browser_automator

    def get_interval_seconds(self) -> int:
        return self.__interval_seconds
