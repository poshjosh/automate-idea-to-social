import os

from ..env import Env, get_video_file, require_path


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

        if not result.get(Env.VIDEO_INPUT_TEXT.value):
            result[Env.VIDEO_INPUT_TEXT.value] = self.read_file(require_path(Env.VIDEO_INPUT_FILE))

        video_content_file = get_video_file()
        result[Env.VIDEO_CONTENT_FILE.value] = video_content_file

        if not result.get(Env.VIDEO_TILE.value):
            result[Env.VIDEO_TILE.value] = os.path.basename(video_content_file).split('.')[0]

        if not result.get(Env.VIDEO_DESCRIPTION.value):
            result[Env.VIDEO_DESCRIPTION.value] = self.read_file(video_content_file)

        if not result.get(Env.VIDEO_COVER_IMAGE_SQUARE.value):
            result[Env.VIDEO_COVER_IMAGE_SQUARE.value] = result.get(Env.VIDEO_COVER_IMAGE.value)

        return result

    @staticmethod
    def read_file(file_path: str):
        with open(file_path) as file:
            return file.read()

