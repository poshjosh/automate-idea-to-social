import logging
import time

from .agent import Agent
from ..web.browser_automator import BrowserAutomator
from ..action.action_result_set import ActionResultSet

logger = logging.getLogger(__name__)


class BrowserAgent(Agent):
    @staticmethod
    def of_config(config: dict[str, any], agent_config: dict[str, any]) -> 'BrowserAgent':
        return BrowserAgent.of_dynamic(config, agent_config, BrowserAgent)

    """
    See example usage below:
    ..highlight:: python
    .. code-block:: python
        class BrowserAgentSubclass(BrowserAgent):
            pass
            
        BrowserAgent.of_dynamic(config, agent_config, BrowserAgentSubclass)
    """
    @staticmethod
    def of_dynamic(config: dict[str, any], agent_config: dict[str, any], init) -> 'BrowserAgent':
        browser_automator = BrowserAutomator.of(config, agent_config)
        interval_seconds: int = agent_config.get('interval-seconds', 0)
        return init(browser_automator, agent_config, interval_seconds)

    def __init__(self,
                 browser_automator: BrowserAutomator,
                 config: dict[str, any],
                 interval_seconds: int = 0):
        self.__browser_automator = browser_automator
        self.__event_handler = browser_automator.get_event_handler()
        self.__config = config
        self.__interval_seconds = interval_seconds

    def run(self, run_config: dict[str, any]) -> ActionResultSet:
        stages_config: dict = self.__config['stages']
        result_set: ActionResultSet = ActionResultSet()
        for stage_name in stages_config.keys():
            result = self.run_stage(stages_config, stage_name, run_config)
            logger.debug(f"Stage: {stage_name}, result: {result_set}")
            result_set.add_all(result)
            # We raise an exception if we want to stop the process
            # so no need to do this.
            # if result_set.is_successful() is False:
            #     break

            self.__sleep()

        return result_set.close()

    def run_stage(self,
                  stages_config: dict[str, any],
                  stage_name: str,
                  run_config: dict[str, any],
                  trials: int = 1) -> ActionResultSet:
        logger.debug(f"Executing stage: {stage_name}")

        result_set = ActionResultSet.none()
        exception = None
        try:
            result_set: ActionResultSet = self.__browser_automator.act_on_elements(
                stages_config, stage_name, run_config)
        except Exception as ex:
            exception = ex

        if result_set.is_successful():
            return result_set

        def on_retry(_trials: int) -> ActionResultSet:
            return self.run_stage(stages_config, stage_name, run_config, _trials)

        # This will return an onerror based result set
        return self.__event_handler.on_execution_error(
            exception, result_set, stages_config, stage_name, on_retry, trials)

    def __sleep(self):
        if self.__interval_seconds < 1:
            return
        time.sleep(self.__interval_seconds)
