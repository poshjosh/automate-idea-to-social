from typing import TypeVar, Union

from ..config import AgentConfig, DEFAULT_ACTIONS_KEY

STR_OR_DICT = TypeVar("STR_OR_DICT", bound=Union[str, dict])
STR_OR_LIST = TypeVar("STR_OR_LIST", bound=Union[str, list[str]])


DEFAULT_ACTIONS: list[str] = ['click']


def element_action_signatures(config: dict[str, any], element_name: str) -> list[str]:
    if AgentConfig.is_default_actions_key(element_name):
        raise ValueError(f'The provided key (i.e {element_name}) is a reserved word.')
    default_actions: list[str] = __element_action_signatures(
        config, DEFAULT_ACTIONS_KEY, DEFAULT_ACTIONS)
    element_config: STR_OR_DICT = config[element_name]
    if isinstance(element_config, str):
        return default_actions if len(default_actions) > 0 else DEFAULT_ACTIONS
    elif isinstance(element_config, dict):
        return __element_action_signatures(element_config, 'actions', default_actions)
    else:
        raise ValueError(f'Unexpected element config type: {type(element_config)}')


def __element_action_signatures(config: dict[str, any],
                                name: str,
                                result_if_none: list[str]) -> list[str]:
    default_actions: STR_OR_LIST = result_if_none if not config \
        else config.get(name, result_if_none)
    if isinstance(default_actions, str):
        return [default_actions]
    elif isinstance(default_actions, list):
        return default_actions
    else:
        raise ValueError(f'Unexpected default actions type: {type(default_actions)}')


def event_action_signatures(config: dict[str, any], event_name: str) -> list[str]:
    event_config = __get_event_config(config, event_name)
    return __make_list(event_config)


def __get_event_config(config: dict[str, any], event_name: str) -> Union[str, list]:
    default_action: str = 'fail' if event_name == 'onerror' else 'continue'
    events_config = None if not config else config.get('events')
    return default_action if events_config is None \
        else events_config.get(event_name, default_action)


def __make_list(event_config) -> list[str]:
    if isinstance(event_config, str):
        return [event_config]
    elif isinstance(event_config, list):
        return event_config
    else:
        raise ValueError(f'Invalid type for events: {event_config}, expected list | str')
