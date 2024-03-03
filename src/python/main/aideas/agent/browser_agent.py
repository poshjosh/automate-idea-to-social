import logging
import time

from .agent import Agent
from ..config.name import Name
from ..event.event_handler import EventHandler
from ..result.element_result_set import ElementResultSet
from ..result.stage_result_set import StageResultSet
from ..run_context import RunContext
from ..web.browser_automator import BrowserAutomator

logger = logging.getLogger(__name__)


class BrowserAgent(Agent):
    @staticmethod
    def of_config(agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any]) -> 'BrowserAgent':
        return BrowserAgent.of_dynamic(agent_name, app_config, agent_config, BrowserAgent)

    """
    See example usage below:
    ..highlight:: python
    .. code-block:: python
        class BrowserAgentSubclass(BrowserAgent):
            pass
            
        BrowserAgent.of_dynamic(config, agent_config, BrowserAgentSubclass)
    """

    @staticmethod
    def of_dynamic(agent_name: str,
                   app_config: dict[str, any],
                   agent_config: dict[str, any], init) -> 'BrowserAgent':
        browser_automator = BrowserAutomator.of(app_config, agent_name, agent_config)
        interval_seconds: int = agent_config.get('interval-seconds', 0)
        return init(agent_name, agent_config, browser_automator, interval_seconds)

    def __init__(self,
                 name: str,
                 agent_config: dict[str, any],
                 browser_automator: BrowserAutomator,
                 interval_seconds: int = 0):
        super().__init__(name, agent_config)
        self.__browser_automator = browser_automator
        self.__event_handler = browser_automator.get_event_handler()
        self.__interval_seconds = interval_seconds

    def without_events(self) -> 'BrowserAgent':
        browser_automator = self.__browser_automator.with_event_handler(EventHandler.noop())
        return BrowserAgent(
            self.get_name(), self.get_config(), browser_automator, self.get_interval_seconds())

    def run(self, run_context: RunContext) -> StageResultSet:
        try:
            return super().run(run_context)
        finally:
            self.__browser_automator.quit()

    def run_stage(self,
                  stages_config: dict[str, any],
                  stage_name: Name,
                  run_context: RunContext) -> ElementResultSet:
        result = self.__run_stage(stages_config, stage_name, run_context, 1)
        self.__sleep()
        return result

    def __run_stage(self,
                    stages_config: dict[str, any],
                    stage_name: Name,
                    run_context: RunContext,
                    trials) -> ElementResultSet:
        logger.debug(f"Executing stage: {stage_name}")

        exception = None
        result = ElementResultSet.none()
        try:
            result: ElementResultSet = self.__browser_automator.act_on_elements(
                stages_config, stage_name, run_context)
        except Exception as ex:
            exception = ex

        def retry_action(_trials: int) -> ElementResultSet:
            return self.__run_stage(stages_config, stage_name, run_context, _trials)

        def run_stages_action(context: RunContext, names: [str], aliases: [str]) -> StageResultSet:
            logger.debug(f'Running stages: {names}, with ids: {aliases}')
            return self.without_events().run_stages(context, names, aliases)

        result = self.__event_handler.handle_terminal_event(
            self.get_name(), stage_name.alias, exception, result, stages_config,
            stage_name.alias, retry_action, run_stages_action, run_context, trials)

        return ElementResultSet.none() if result is None else result

    def __sleep(self):
        if self.__interval_seconds < 1:
            return
        time.sleep(self.__interval_seconds)

    def get_browser_automator(self) -> BrowserAutomator:
        return self.__browser_automator

    def get_interval_seconds(self) -> int:
        return self.__interval_seconds