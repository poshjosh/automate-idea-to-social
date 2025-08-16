import logging.config

from app.app import App
from app.task import AgentTask

if __name__ == '__main__':

    config_loader = App.init()

    logging.config.dictConfig(config_loader.load_logging_config())

    AgentTask.of_defaults(config_loader).start()
