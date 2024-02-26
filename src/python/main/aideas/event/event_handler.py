import logging
from typing import Callable

from ..action.action import Action
from ..action.action_result_set import ActionResultSet
from ..action.action_handler import ActionHandler

logger = logging.getLogger(__name__)


class EventHandler:
    def __init__(self, action_handler: ActionHandler):
        self.__action_handler: ActionHandler = action_handler

    def handle_event(self,
                     event_name: str,
                     exception: Exception,
                     result_set: ActionResultSet,
                     config: dict[str, any],
                     key: str,
                     retry: Callable[[int], ActionResultSet],
                     run_stages: Callable[[list[str]], ActionResultSet],
                     trials: int = 1) -> ActionResultSet:
        event_config = config[key]
        if type(event_config) is not dict:
            event_config = {}
        if event_name == 'onerror':
            logger.debug(f"For: {key}, handling event: {event_name} with config: {event_config}")
        return self.__handle_event(
            event_name, exception, result_set, key,
            event_config, retry, run_stages, trials)

    def __handle_event(self,
                       event_name: str,
                       exception: Exception,
                       result_set: ActionResultSet,
                       key: str,
                       config: dict[str, any],
                       retry: Callable[[int], ActionResultSet],
                       run_stages: Callable[[list[str]], ActionResultSet],
                       trials: int = 1) -> ActionResultSet:
        default_action: str = 'fail' if event_name == 'onerror' else 'continue'
        event_config: str | list = config.get('events', {}).get(event_name, default_action)
        action_signature_list = self.__make_list(event_config)

        index: int = -1
        for action_signature in action_signature_list:
            index += 1
            if action_signature == 'continue':
                self.__log(exception)
                if event_name == 'onerror':
                    logger.warning(f"For {key}, will continue despite error!")
                return result_set
            elif action_signature == 'fail':
                self.__raise_error(exception, result_set)
            elif action_signature.startswith('retry'):
                if trials < self.__max_trials(action_signature):
                    self.__log(exception)
                    logger.debug(f"Retrying: {key} after {event_name}, tried {trials} already")
                    return retry(trials + 1)
                else:
                    self.__raise_error(exception, result_set)
            elif action_signature.startswith('run_stages'):
                self.__log(exception)
                stage_names = action_signature.split(' ')[1:]
                next_result_set = run_stages(stage_names)
                return ActionResultSet().add_all(result_set).add_all(next_result_set).close()
            else:
                self.__log(exception)
                result = self.__action_handler.execute(
                    self.__create_action(key, index, event_name, action_signature))
                return ActionResultSet().add_all(result_set).add(result).close()

    def __make_list(self, event_config) -> list[str]:
        if type(event_config) is str:
            return [event_config]
        elif type(event_config) is list:
            return event_config
        else:
            raise ValueError(f'Invalid type for events: {event_config}, expected list | str')

    def __raise_error(self, exception: Exception, result_set: ActionResultSet):
        own_ex = ValueError(f"{result_set}")
        if exception is None:
            raise own_ex
        else:
            raise own_ex from exception

    def __create_action(self,
                        target_id: str,
                        index: int,
                        event_name: str,
                        action_signature: str) -> Action:
        return Action(f"{target_id}[{index}]-{event_name}", action_signature, [])

    def __max_trials(self, action: str) -> int:
        max_retries: int = int(action.split(' ')[1])
        return max_retries + 1

    def __log(self, exception: Exception):
        if exception is not None:
            logger.warning(f"{str(exception)}")
