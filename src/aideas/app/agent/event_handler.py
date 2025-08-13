from collections import OrderedDict
import logging
from typing import Callable

from ..action.action import Action
from ..action.action_handler import ActionHandler, ActionError
from ..action.action_result import ActionResult
from ..action.action_signatures import parse_agent_to_stages
from ..config import AgentConfig, ConfigPath, Name, ON_ERROR, ON_SUCCESS
from ..result.result_set import ElementResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class EventHandler:
    @staticmethod
    def noop() -> 'EventHandler':
        return NOOP

    def __init__(self, action_handler: ActionHandler):
        self.__action_handler: ActionHandler = action_handler

    @staticmethod
    def is_path_successful(
            result_set: ElementResultSet, config: AgentConfig, config_path: ConfigPath) -> bool:
        """
        Determine if the result set has a failure, excluding stages and stage items
        which ignore errors.

        For stage items, it is sufficient to simply check if the result set is successful.
        On the other hand, for stages, we need to exclude stage items which ignore errors.
        These are stage items, which have `onerror: continue`.

        If a stage-item fails:

        - succeeding stage-items will not be executed, unless
        `onerror` is set to `continue` for the stage-item.

        - the stage will fail, unless `onerror` is set to
        `continue` for the stage.

        :param result_set: The result set to check
        :param config: The agent configuration
        :param config_path: The path to the aspect of the configuration which we are handling
        :return: true if the result set has a failure, false otherwise
        """

        if config_path.is_stage_item():
            return result_set.is_successful()
        elif config_path.is_stage():
            return not EventHandler.__has_failure_excluding_ignored(result_set, config, config_path)
        else:
            raise ValueError(f'Expected path to stage or stage item, got: {config_path}')

    @staticmethod
    def __has_failure_excluding_ignored(
            result_set: ElementResultSet, config: AgentConfig, config_path: ConfigPath) -> bool:
        for target_id, result_list in result_set.items():
            target_cfg_path = config_path.join(target_id)
            if config.is_continue_on_event(target_cfg_path, ON_ERROR):
                continue
            if result_set.is_result_successful(result_list) is False:
                return True
        return False

    def handle_event(self,
                     agent_name: str,
                     config: AgentConfig,
                     config_path: ConfigPath,
                     event_name: str,
                     run_context: RunContext,
                     run_stages: Callable[[RunContext, OrderedDict[str, list[Name]]], None]) \
            -> ElementResultSet:
        return self.__handle_event(
            agent_name, config, config_path, event_name, run_context, run_stages, trials=1)

    def handle_result_event(self,
                            agent_name: str,
                            config: AgentConfig,
                            config_path: ConfigPath,
                            run_context: RunContext,
                            run_stages: Callable[[RunContext, OrderedDict[str, list[Name]]], None],
                            retry: Callable[[int], ElementResultSet] = None,
                            exception: Exception = None,
                            result: ElementResultSet = None,
                            trials: int = 1) -> ElementResultSet:

        event_name = self.__determine_result_event_name(config, config_path, exception, result)

        return self.__handle_event(
            agent_name, config, config_path, event_name, run_context,
            run_stages, retry, exception, result, trials)

    def __handle_event(self,
                       agent_name: str,
                       config: AgentConfig,
                       config_path: ConfigPath,
                       event_name: str,
                       run_context: RunContext,
                       run_stages: Callable[[RunContext, OrderedDict[str, list[Name]]], None],
                       retry: Callable[[int], ElementResultSet] = None,
                       exception: Exception = None,
                       result: ElementResultSet = None,
                       trials: int = 1) -> ElementResultSet:

        if event_name == ON_ERROR:
            logger.debug(f'Handling {event_name} event for {config_path}')

        action_signature_list = config.get_event_actions(config_path, event_name)

        stage_id = config_path.stage().id
        target_id = config_path.name().id

        def create_action():
            return self.__create_action(
                agent_name, stage_id, target_id, index,
                event_name, action_signature, run_context)

        index: int = -1
        for action_signature in action_signature_list:
            index += 1
            if action_signature == 'continue':
                if event_name == ON_ERROR:
                    logger.warning(
                        f'For {config_path}, will continue despite error: {type(exception)}!')
                    logger.exception(exception)
            elif action_signature == 'fail':
                error_msg: str = f'Error {config_path}, result: {result}'
                run_context.add_action_result(ActionResult.failure(create_action(), error_msg))
                raise ActionError(error_msg) from exception
            elif action_signature.startswith('retry'):
                max_trials: int = self.__max_trials(action_signature)
                logger.debug(f'Attempted: {trials} of {max_trials} '
                             f'for "{action_signature}" of {config_path}')
                if trials < max_trials:
                    retry(trials + 1)
                else:
                    error_msg: str = f'Max retries exceeded {config_path}, result: {result}'
                    run_context.add_action_result(ActionResult.failure(create_action(), error_msg))
                    raise ActionError(error_msg) from exception
            elif action_signature.startswith('run_stages'):
                _, agent_to_stages = parse_agent_to_stages(
                    action_signature, agent_name, config_path.stage())
                run_stages(run_context, agent_to_stages)
            else:
                action = create_action()
                logger.debug(f"Executing event action: {action}")
                try:
                    action_result = self.__action_handler.execute(run_context, action)
                    run_context.add_action_result(action_result)
                except ActionError as ex:
                    run_context.add_action_result(ActionResult.failure(action))
                    raise ex

        return run_context.get_element_results(agent_name, stage_id)

    @staticmethod
    def __determine_result_event_name(config: AgentConfig,
                                      config_path: ConfigPath,
                                      exception: Exception,
                                      result_set: ElementResultSet) -> str:
        """
        Determine the event name to use based on the result set and the exception.
        :param config: The agent configuration
        :param config_path: The path to the aspect of the configuration which we are handling
        :param exception: The exception which was thrown during process, or None
        :param result_set: The result of the process, or None
        :return: The event name to use
        """
        if exception is not None or EventHandler.__has_failure(config, config_path, result_set):
            return ON_ERROR
        else:
            return ON_SUCCESS

    @staticmethod
    def __has_failure(config: AgentConfig,
                      config_path: ConfigPath,
                      result_set: ElementResultSet) -> bool:
        # if not result_set:
        if result_set.is_empty():
            # This happens if a condition to proceed with processing is not met
            # It does not indicate a failure, just that the condition for processing was not met.
            return False
        return EventHandler.is_path_successful(result_set, config, config_path) is False

    @staticmethod
    def __create_action(agent_name: str,
                        stage_id: str,
                        target_id: str,
                        index: int,
                        event_name: str,
                        action_signature: str,
                        run_context: RunContext) -> Action:
        return Action.of(agent_name, stage_id, f"{target_id}[{index}]-{event_name}",
                         action_signature, run_context)

    @staticmethod
    def __max_trials(action_signature: str) -> int:
        max_retries: int = int(action_signature.split(' ')[1])
        return max_retries + 1


class NoopEventHandler(EventHandler):
    def __init__(self):
        super().__init__(ActionHandler.noop())

    def handle_event(self,
                     agent_name: str,
                     config: AgentConfig,
                     config_path: ConfigPath,
                     event_name: str,
                     run_context: RunContext,
                     run_stages: Callable[[RunContext, OrderedDict[str, list[Name]]], None]) \
            -> ElementResultSet:
        return ElementResultSet.none()

    def handle_result_event(self,
                            agent_name: str,
                            config: AgentConfig,
                            config_path: ConfigPath,
                            run_context: RunContext,
                            run_stages: Callable[[RunContext, OrderedDict[str, list[Name]]], None],
                            retry: Callable[[int], ElementResultSet] = None,
                            exception: Exception = None,
                            result: ElementResultSet = None,
                            trials: int = 1) -> ElementResultSet:
        return result


NOOP: EventHandler = NoopEventHandler()
