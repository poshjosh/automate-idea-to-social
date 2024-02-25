import os
from typing import AnyStr

from .agent_names import AgentNames
from ..env_names import PictoryEnvNames, TranslationEnvNames


class AgentInputs:
    __DEFAULT_OUTPUT_LANGUAGES = ["ar", "bn", "de", "es", "fr", "hi", "it", "ja", "ko", "ru", "zh", "zh-TW"]

    def get(self, agent_name: str):
        if agent_name == AgentNames.PICTORY:
            return self.for_pictory()
        elif agent_name == AgentNames.TRANSLATION:
            return self.for_translation()
        else:
            raise ValueError(f"Unsupported agent: {agent_name}")

    def for_pictory(self) -> dict[str, any]:
        file_path = os.environ[PictoryEnvNames.INPUT_FILE]
        file_content = self.read_file(file_path)
        # TODO - ACTION_VALUES - Find a standard format
        enter_text: dict[str, str] = {
            'title': os.path.basename(file_path).split('.')[0],
            'text': file_content,
            'username': os.environ[PictoryEnvNames.USER_NAME],
            'password': os.environ[PictoryEnvNames.USER_PASS]
        }
        # TODO - Actions which have argument(s) will not work. So find a better logic
        return {'enter_text': enter_text}

    def for_translation(self) -> dict[str, any]:
        result = {TranslationEnvNames.OUTPUT_LANGUAGES: AgentInputs.__DEFAULT_OUTPUT_LANGUAGES}
        return self.from_os_environ(AgentNames.TRANSLATION, result)

    def from_os_environ(self, agent_name: str, result: dict[str, any] = None) -> dict[str, any]:
        if result is None:
            result = {}
        for k, v in os.environ.items():
            if k.startswith(agent_name):
                result[k] = v
        return result

    def read_file(self, file_path: str) -> AnyStr:
        with open(file_path) as file:
            return file.read()

