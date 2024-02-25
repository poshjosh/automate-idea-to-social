from typing import TypeVar, Union

T = TypeVar("T", bound=Union[str, dict])


class ElementSearchConfig:
    @staticmethod
    def of(config: T):
        if type(config) is str:
            search_from = None
            search_for = str(config)
        elif type(config) is dict:
            xpath_config = config['xpath']
            if type(xpath_config) is str:
                search_from = None
                search_for = xpath_config
            elif type(xpath_config) is dict:
                search_from = dict(xpath_config)['search-from']
                search_for = dict(xpath_config)['search-for']
            else:
                raise ValueError(f'Invalid search config: {config}')
        else:
            raise ValueError(f'Invalid search config: {config}')
        return ElementSearchConfig(search_from, search_for)

    def __init__(self, search_from: str, search_for: str):
        self.__search_from = search_from
        self.__search_for = search_for

    def get_search_from(self) -> str:
        return self.__search_from

    def get_search_for(self) -> str:
        return self.__search_for
