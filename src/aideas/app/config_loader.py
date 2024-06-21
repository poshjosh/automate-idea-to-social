import logging
import os

from .action.variable_parser import replace_all_variables

from pyu.io.yaml_loader import YamlLoader

logger = logging.getLogger(__name__)


class ConfigLoader(YamlLoader):
    def __init__(self, config_path: str):
        super().__init__(config_path, transform=replace_all_variables, suffix='.config')

    def load_agent_config(self, agent_name: str) -> dict[str, any]:
        return self.load_from_path(self.get_agent_config_path(agent_name))

    def get_agent_config_path(self, agent_name: str) -> str:
        return self.get_path(os.path.join('agent', agent_name))
