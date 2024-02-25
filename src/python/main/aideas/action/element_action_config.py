from typing import TypeVar, Union

STR_OR_DICT = TypeVar("STR_OR_DICT", bound=Union[str, dict])
STR_OR_LIST = TypeVar("STR_OR_LIST", bound=Union[str, list[str]])


class ElementActionConfig:
    DEFAULT_ACTIONS_KEY: str = 'default-actions'
    DEFAULT_ACTIONS: list[str] = ['click']

    @staticmethod
    def get(config: dict[str, any], element_name: str) -> list[str]:
        if element_name == ElementActionConfig.DEFAULT_ACTIONS_KEY:
            raise ValueError(f'The provided key (i.e {element_name}) is a reserved word.')
        default_actions: list[str] = ElementActionConfig.__get(
            config, ElementActionConfig.DEFAULT_ACTIONS_KEY, ElementActionConfig.DEFAULT_ACTIONS)
        element_config: STR_OR_DICT = config[element_name]
        if type(element_config) is str:
            return default_actions if len(default_actions) > 0 else ElementActionConfig.DEFAULT_ACTIONS
        elif type(element_config) is dict:
            return ElementActionConfig.__get(element_config, 'actions', default_actions)
        else:
            raise ValueError(f'Unexpected element config type: {type(element_config)}')

    @staticmethod
    def __get(config: dict[str, any], name: str, result_if_none: list[str]) -> list[str]:
        default_actions: STR_OR_LIST = config.get(name, result_if_none)
        if type(default_actions) is str:
            return [default_actions]
        elif type(default_actions) is list:
            return default_actions
        else:
            raise ValueError(f'Unexpected default actions type: {type(default_actions)}')
    