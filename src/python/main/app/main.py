import logging.config
import os.path

from aideas.app import App, AppArg, get_list_arg_value
from aideas.config_loader import ConfigLoader


if __name__ == "__main__":

    config_loader = ConfigLoader(os.path.join('resources', 'config'))

    logging.config.dictConfig(config_loader.load_logging_config())

    App.of_defaults(config_loader).run(get_list_arg_value(AppArg.AGENTS))

