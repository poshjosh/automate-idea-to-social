from typing import Union


class Name:
    @staticmethod
    def of_list(names: list[str], alias: Union[str, None] = None) -> ['Name']:
        aliases = [names] if alias is None else [alias for _ in names]
        return Name.of_lists(names, aliases)

    @staticmethod
    def of_lists(names: list[str], aliases: Union[list[str], None] = None) -> ['Name']:
        if aliases is not None and len(names) != len(aliases):
            raise ValueError("The number of names and aliases must be the same")
        if aliases is None:
            aliases: [str] = [name for name in names]
        return [Name(names[i], aliases[i]) for i in range(len(names))]

    @staticmethod
    def of(name: str, alias: Union[str, None] = None) -> 'Name':
        return Name(name, alias)

    def __init__(self, name: str, alias: Union[str, None] = None):
        if name is None:
            raise ValueError('name cannot be None')
        self.value = name
        self.alias = name if alias is None else alias

    def __eq__(self, other) -> bool:
        return self.value == other.value and self.alias == other.alias

    def __hash__(self) -> int:
        return hash(self.value) + hash(self.alias)

    def __str__(self) -> str:
        return self.value if self.value == self.alias else f'({self.value}|{self.alias})'
