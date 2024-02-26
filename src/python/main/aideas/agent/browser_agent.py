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
                 agent_config: dict[str, any],
                 interval_seconds: int = 0):
        super().__init__(agent_config)
        self.__browser_automator = browser_automator
        self.__event_handler = browser_automator.get_event_handler()
        self.__interval_seconds = interval_seconds

    def run(self, run_config: dict[str, any]) -> ActionResultSet:
        try:
            return super().run(run_config)
        finally:
            self.__browser_automator.quit()

    def run_stage(self,
                  stages_config: dict[str, any],
                  stage_name: str,
                  run_config: dict[str, any]) -> ActionResultSet:
        result = self.__run_stage(stages_config, stage_name, run_config, 1)
        self.__sleep()
        return result

    def __run_stage(self,
                    stages_config: dict[str, any],
                    stage_name: str,
                    run_config: dict[str, any],
                    trials) -> ActionResultSet:
        logger.debug(f"Executing stage: {stage_name}")

        result_set = ActionResultSet.none()
        exception = None
        try:
            result_set: ActionResultSet = self.__browser_automator.act_on_elements(
                stages_config, stage_name, run_config)
        except Exception as ex:
            exception = ex

        def retry_action(_trials: int) -> ActionResultSet:
            return self.__run_stage(stages_config, stage_name, run_config, _trials)

        def run_stages_action(stage_names: [str]) -> ActionResultSet:
            return self.run_stages(run_config, stage_names)

        event_name = 'onsuccess' if result_set.is_successful() else 'onerror'

        # This will return an onerror based result set
        return self.__event_handler.handle_event(
            event_name, exception, result_set, stages_config,
            stage_name, retry_action, run_stages_action, trials)

    def __sleep(self):
        if self.__interval_seconds < 1:
            return
        time.sleep(self.__interval_seconds)
