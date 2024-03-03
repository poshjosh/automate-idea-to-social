import logging
from typing import Callable

from ..action.action import Action
from ..action.action_handler import ActionHandler
from ..action.action_signatures import event_action_signatures
from ..result.element_result_set import ElementResultSet
from ..result.stage_result_set import StageResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class EventHandler:
    @staticmethod
    def noop() -> 'EventHandler':
        return NOOP

    def __init__(self, action_handler: ActionHandler):
        self.__action_handler: ActionHandler = action_handler

    def handle_terminal_event(self,
                              agent_name: str,
                              stage_id: str,
                              exception: Exception,
                              result: ElementResultSet,
                              config: dict[str, any],
                              key: str,
                              retry: Callable[[int], ElementResultSet],
                              run_stages: Callable[[RunContext, list[str], list[str]], StageResultSet],
                              run_context: RunContext,
                              trials: int = 1) -> ElementResultSet:
        event_config = config[key]
        if type(event_config) is not dict:
            event_config = {}

        if exception is not None or result is None or not result.is_successful():
            event_name = 'onerror'
            logger.debug(f'For: {key}, handling event: {event_name} with config: {event_config}')
        else:
            event_name = 'onsuccess'

        return self.__handle_event(
            agent_name, stage_id, event_name, exception, result, key,
            event_config, retry, run_stages, run_context, trials)

    def __handle_event(self,
                       agent_name: str,
                       stage_id: str,
                       event_name: str,
                       exception: Exception,
                       result: ElementResultSet,
                       key: str,
                       config: dict[str, any],
                       retry: Callable[[int], ElementResultSet],
                       run_stages: Callable[[RunContext, list[str], list[str]], StageResultSet],
                       run_context: RunContext,
                       trials: int = 1) -> ElementResultSet:
        action_signature_list = event_action_signatures(config, event_name)

        index: int = -1
        for action_signature in action_signature_list:
            index += 1
            if action_signature == 'continue':
                self.__log(exception)
                if event_name == 'onerror':
                    logger.warning(f'For {key}, will continue despite error!')
                return result
            elif action_signature == 'fail':
                self.__raise_error(exception, result)
            elif action_signature.startswith('retry'):
                if trials < self.__max_trials(action_signature):
                    self.__log(exception)
                    logger.debug(f'Retrying: {key} after {event_name}, tried {trials} already')
                    return retry(trials + 1)
                else:
                    self.__raise_error(exception, result)
            elif action_signature.startswith('run_stages'):
                self.__log(exception)
                stage_names = action_signature.split(' ')[1:]
                stage_ids: [str] = [stage_id] * len(stage_names)
                run_stages(run_context, stage_names, stage_ids)
                return run_context.get_element_results(agent_name, stage_id)
            else:
                self.__log(exception)
                action = self.__create_action(
                    agent_name, stage_id, key, index, event_name, action_signature, run_context)
                action_result = self.__action_handler.execute(action)
                run_context.add_action_result(agent_name, stage_id, action_result)
                return run_context.get_element_results(agent_name, stage_id)

    def __compose(self,
                  stage_result_set: StageResultSet,
                  result: ElementResultSet) -> ElementResultSet:
        for stage_name in stage_result_set.keys():
            to_add: ElementResultSet = stage_result_set.get(stage_name)
            result.set_all(to_add)
        return result

    def __raise_error(self, exception: Exception, result_set: ElementResultSet):
        own_ex = ValueError(f'{result_set}')
        if exception is None:
            raise own_ex
        else:
            raise own_ex from exception

    def __create_action(self,
                        agent_name: str,
                        stage_id: str,
                        target_id: str,
                        index: int,
                        event_name: str,
                        action_signature: str,
                        run_context: RunContext) -> Action:
        return Action.of(agent_name, stage_id,f"{target_id}[{index}]-{event_name}",
                         action_signature, run_context)

    def __max_trials(self, action: str) -> int:
        max_retries: int = int(action.split(' ')[1])
        return max_retries + 1

    def __log(self, ex: Exception):
        if ex is not None:
            logger.warning(f'{ex}')


class NoopEventHandler(EventHandler):
    def __init__(self):
        super().__init__(ActionHandler.noop())

    def handle_terminal_event(self,
                              agent_name: str,
                              stage_id: str,
                              exception: Exception,
                              result: ElementResultSet,
                              config: dict[str, any],
                              key: str,
                              retry: Callable[[int], ElementResultSet],
                              run_stages: Callable[[RunContext, list[str], list[str]], StageResultSet],
                              run_context: RunContext,
                              trials: int = 1) -> ElementResultSet:
        return result


NOOP: EventHandler = NoopEventHandler()
