import logging.config
import os.path

from aideas.app import App, ARG_AGENTS, get_list_arg
from aideas.config_loader import ConfigLoader


if __name__ == "__main__":

    config_path = os.path.join('aideas', 'config')
    config_loader = ConfigLoader(config_path)
    logging.config.dictConfig(config_loader.load_logging_config())

    agents: [str] = get_list_arg(ARG_AGENTS)
    App.of_defaults(config_loader).run(agents)

