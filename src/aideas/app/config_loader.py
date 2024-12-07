import logging
import os

from pyu.io.file import load_yaml, read_content
from pyu.io.yaml_loader import YamlLoader
from .action.variable_parser import replace_all_variables
from .config import RunArg
from .env import Env
from .paths import Paths

logger = logging.getLogger(__name__)


class ConfigLoader(YamlLoader):
    def __init__(self, config_path: str, run_config: dict[str, any] = None):
        super().__init__(config_path, suffix='.config')
        self.__variable_source = {}
        Env.collect(self.__variable_source)  # Environment variables
        RunArg.collect(self.__variable_source)  # Run args from sys.argv
        self.__variable_source.update(
            run_config if run_config is not None else self.load_run_config())  # Run config

    def load_run_config(self) -> dict[str, any]:
        result = self.load_config("run")

        video_content_path = Paths.require_path(result[RunArg.VIDEO_CONTENT_FILE.value])
        result[RunArg.VIDEO_CONTENT_FILE.value] = video_content_path
        video_content = read_content(video_content_path)

        if not result.get(RunArg.VIDEO_TITLE.value):
            result[RunArg.VIDEO_TITLE.value] = os.path.basename(video_content_path).split('.')[0]

        if not result.get(RunArg.VIDEO_DESCRIPTION.value):
            result[RunArg.VIDEO_DESCRIPTION.value] = video_content

        video_input_file = result.get(RunArg.VIDEO_INPUT_FILE.value)
        if video_input_file:
            result[RunArg.VIDEO_INPUT_FILE.value] = Paths.require_path(video_input_file)
        else:
            result[RunArg.VIDEO_INPUT_FILE.value] = video_content_path

        if not result.get(RunArg.VIDEO_INPUT_TEXT.value):
            result[RunArg.VIDEO_INPUT_TEXT.value] = (
                read_content(result[RunArg.VIDEO_INPUT_FILE.value]))

        video_cover_image_path = Paths.require_path(result[RunArg.VIDEO_COVER_IMAGE.value])
        result[RunArg.VIDEO_COVER_IMAGE.value] = video_cover_image_path

        if result.get(RunArg.VIDEO_COVER_IMAGE_SQUARE.value):
            result[RunArg.VIDEO_COVER_IMAGE_SQUARE.value] = Paths.require_path(
                result[RunArg.VIDEO_COVER_IMAGE_SQUARE.value])
        else:
            result[RunArg.VIDEO_COVER_IMAGE_SQUARE.value] = video_cover_image_path

        return result

    def load_from_path(self, path: str) -> dict[str, any]:
        try:
            return replace_all_variables(load_yaml(path), self.__variable_source)
        except FileNotFoundError:
            logger.warning(f'Could not find config file for: {path}')
            return {}

    def load_agent_config(self, agent_name: str) -> dict[str, any]:
        return self.load_from_path(self.get_agent_config_path(agent_name))

    def get_agent_config_path(self, agent_name: str) -> str:
        return self.get_path(os.path.join('agent', agent_name))
