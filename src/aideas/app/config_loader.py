import logging
import os

from pyu.io.file import load_yaml, read_content
from pyu.io.yaml_loader import YamlLoader
from .action.variable_parser import replace_all_variables
from .config import RunArg
from .env import Env, is_production
from .paths import Paths

logger = logging.getLogger(__name__)


_SUFFIX = '.config'


class ConfigLoader(YamlLoader):
    def __init__(self, config_path: str, run_config: dict[str, any] = None):
        super().__init__(config_path, suffix=_SUFFIX)
        self.__variable_source = {}
        self.__variable_source.update(Env.collect())  # Environment variables
        self.__variable_source.update(RunArg.collect())  # Run args from sys.argv
        self.__variable_source.update(
            run_config if run_config is not None else self.load_run_config())  # Run config

    def load_app_config(self, path: str = None) -> dict[str, any]:
        app_config = super().load_app_config(path)
        # If not in production, use names of every agent in the 'agent' directory.
        # This may include, test, hidden or agents under development.
        if is_production() is False:
            agents = []
            agent_dir = os.path.join(os.path.dirname(self.get_path("app")), 'agent')
            for agent_filename in os.listdir(agent_dir):
                agents.append(agent_filename[0:agent_filename.index(_SUFFIX)])
            app_config['agents'] = agents
        return app_config

    def load_run_config(self) -> dict[str, any]:
        result = self.load_config("run")
        return RunArg.of_dict(result)

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
