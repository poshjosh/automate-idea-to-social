from collections.abc import Iterable

from typing import Union

import logging
import os
import signal
import sys

from .config_loader import ConfigLoader
from .env import Env, is_production, get_env_value, get_output_dir, get_content_dir
from .task import shutdown as shutdown_tasks, init_tasks_cleanup

logger = logging.getLogger(__name__)


class App:
    __shutting_down = False
    __shutdown = False

    @staticmethod
    def init(config_path: Union[str, Iterable, None] = None) -> ConfigLoader:
        print(f"Initializing app, profiles: {get_env_value(Env.APP_PROFILES)}"
              f", working dir: {os.getcwd()}") # logging not yet configured, so we use print
        signal.signal(signal.SIGINT, App.shutdown)
        signal.signal(signal.SIGTERM, App.shutdown)
        Env.set_defaults()
        if is_production():
            init_tasks_cleanup(lambda: App.__shutting_down, 600)

        logs_output_dir = get_output_dir('logs')
        if not os.path.exists(logs_output_dir):
            os.makedirs(logs_output_dir)
            logger.info(f"Created logs output directory: {logs_output_dir}")

        content_dir = get_content_dir()
        if not os.path.exists(content_dir):
            os.makedirs(content_dir)
            logger.info(f"Created content directory: {content_dir}")

        return ConfigLoader(config_path)

    @staticmethod
    def shutdown(signum, _):
        try:
            logger.warning(f"Received signal {signum}")
            if App.__shutting_down:
                msg = "Already shutting down..." if App.__shutdown is False else "Already shut down"
                logger.warning(msg)
                return
            App.__shutting_down = True
            logger.info("Shutting down...")
            shutdown_tasks()
            App.__shutdown = True
        finally:
            # TODO - Find out why shutdown is not achieved without this. On the other hand,
            #  when we remove this, we OFTEN receive the following warning:
            #  UserWarning: resource_tracker: There appear to be 2 leaked semaphore objects to clean up at shutdown
            logger.info("Exiting")
            sys.exit(1)

    @staticmethod
    def is_shutdown() -> bool:
        return App.__shutdown

    @staticmethod
    def is_shutting_down() -> bool:
        return App.__shutting_down
