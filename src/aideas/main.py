import logging.config
import os.path

from app.app import App
from app.config import RunArg
from app.config_loader import ConfigLoader
from app.env import Env

if __name__ == '__main__':

    Env.set_defaults()

    config_loader = ConfigLoader(os.path.join(os.getcwd(), 'resources', 'config'))

    logging.config.dictConfig(config_loader.load_logging_config())

    run_config = config_loader.load_run_config()

    run_config.update(RunArg.collect())

    App.of_defaults(config_loader).run(run_config)


