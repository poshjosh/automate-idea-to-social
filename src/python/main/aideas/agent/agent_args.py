import os
from typing import AnyStr

from ..env import Env


class AgentArgs:
    __DEFAULT_OUTPUT_LANGUAGES = ["ar", "bn", "de", "es", "fr", "hi", "it", "ja", "ko", "ru", "zh", "zh-TW"]

    @staticmethod
    def from_config(config: dict[str, any]) -> 'AgentArgs':
        app_name = config['app']['name']
        return AgentArgs(app_name)

    def __init__(self, app_name: str = None):
        self.__app_name = app_name

    def load(self) -> dict[str, any]:
        result = {
            'app.name': self.__app_name,
            Env.TRANSLATION_OUTPUT_LANGUAGES.value: ','.join(self.__DEFAULT_OUTPUT_LANGUAGES),
        }
        result.update(Env.collect())

        self.__add_cwd(result, Env.VIDEO_COVER_IMAGE.value)
        self.__add_cwd(result, Env.VIDEO_COVER_IMAGE_SQUARE.value)

        file_path = result[Env.VIDEO_INPUT_FILE.value]
        if result.get(Env.VIDEO_TILE.value) is None:
            result[Env.VIDEO_TILE.value] = os.path.basename(file_path).split('.')[0]
        file_content = self.read_file(file_path)
        result[Env.VIDEO_DESCRIPTION.value] = file_content
        return result

    @staticmethod
    def __add_cwd(result: dict[str, any], key: str):
        value = result.get(key)
        if value is not None and value != '':
            result[key] = os.path.join(os.getcwd(), value)

    def read_file(self, file_path: str) -> AnyStr:
        with open(file_path) as file:
            return file.read()
