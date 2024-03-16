import os

from ..env import Env


class AgentArgs:
    __DEFAULT_OUTPUT_LANGUAGES = [
        "ar", "bn", "de", "es", "fr", "hi", "it", "ja", "ko", "ru", "zh", "zh-TW"]

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

        video_input_file = Env.require_path(Env.VIDEO_INPUT_FILE)
        if not result.get(Env.VIDEO_TILE.value):
            result[Env.VIDEO_TILE.value] = os.path.basename(video_input_file).split('.')[0]
        if not result.get(Env.VIDEO_DESCRIPTION.value):
            file_content = self.read_file(video_input_file)
            result[Env.VIDEO_DESCRIPTION.value] = file_content

        return result

    @staticmethod
    def read_file(file_path: str):
        with open(file_path) as file:
            return file.read()

