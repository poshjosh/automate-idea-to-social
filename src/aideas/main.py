import logging.config

from app.app import App
from app.config import RunArg
from app.task import Task

if __name__ == '__main__':

    config_loader = App.init()

    logging.config.dictConfig(config_loader.load_logging_config())

    run_config = config_loader.load_run_config()

    run_config.update(RunArg.of_sys_argv())

    Task.of_defaults(config_loader, run_config).start()


