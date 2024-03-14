import logging.config
import os.path

from aideas.app import App, ARG_AGENTS, get_list_arg
from aideas.config_loader import ConfigLoader


if __name__ == "__main__":

    config_loader = ConfigLoader(os.path.join('aideas', 'config'))

    logging.config.dictConfig(config_loader.load_logging_config())

    App.of_defaults(config_loader).run(get_list_arg(ARG_AGENTS))

