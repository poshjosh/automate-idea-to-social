import logging
from typing import Callable

from ..action.action import Action
from ..action.action_result_set import ActionResultSet
from ..action.action_handler import ActionHandler

logger = logging.getLogger(__name__)


class EventHandler:
    def __init__(self, action_handler: ActionHandler):
        self.__browser_action_handler: ActionHandler = action_handler

    def on_execution_error(self,
                           exception: Exception,
                           result_set: ActionResultSet,
                           config: dict[str, any],
                           key: str,
                           on_retry: Callable[[int], ActionResultSet],
                           trials: int = 1) -> ActionResultSet:
        error_config = config[key]
        if type(error_config) is not dict:
            error_config = {}
        failure = exception if exception is not None else result_set
        logger.debug(f"For: {key}, handling failure with "
                     f"config: {error_config}, failure:\n{failure}")
        return self.__onerror(exception, result_set, key, error_config, on_retry, trials)

    """
    Handle onerror related actions in the stages of the agents.
    """

    def __onerror(self,
                  exception: Exception,
                  result_set: ActionResultSet,
                  key: str,
                  config: dict[str, any],
                  on_retry: Callable[[int], ActionResultSet],
                  trials: int = 1) -> ActionResultSet:
        default_action: str = 'fail'
        events_config = config.get('events', {'onerror': default_action})
        onerror: str | list = events_config.get('onerror', default_action)
        if type(onerror) is str:
            action_signature_list = [onerror]
        elif type(onerror) is list:
            action_signature_list = onerror
        else:
            raise ValueError(f'Invalid type for onerror: {onerror}, expected list | str')

        for action_signature in action_signature_list:
            if action_signature == 'continue':
                logger.warning("Will continue despite error.")
                return result_set
            elif action_signature == 'fail':
                self.__raise_error(exception, result_set)
            elif action_signature.startswith('retry'):
                if trials < self.__max_trials(action_signature):
                    logger.debug(f"Retrying: {key} after error, tried {trials} already")
                    return on_retry(trials + 1)
                else:
                    self.__raise_error(exception, result_set)
            else:
                result = self.__browser_action_handler.execute(
                    self.__create_action(key, action_signature))
                return ActionResultSet().add_all(result_set).add(result).close()

    def __raise_error(self, exception: Exception, result_set: ActionResultSet):
        own_ex = ValueError(f"{result_set}")
        if exception is None:
            raise own_ex
        else:
            raise own_ex from exception

    def __create_action(self, target_id: str, action_signature: str) -> Action:
        return Action(f"{target_id}.onerror", action_signature, [])

    def __max_trials(self, action: str) -> int:
        max_retries: int = int(action.split(' ')[1])
        return max_retries + 1
