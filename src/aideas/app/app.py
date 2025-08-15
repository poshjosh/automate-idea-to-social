import logging
import os
import signal
import sys

from .config_loader import ConfigLoader
from .env import Env, is_production, get_env_value
from .task import shutdown as shutdown_tasks, init_tasks_cleanup

logger = logging.getLogger(__name__)


class App:
    __shutting_down = False
    __shutdown = False

    @staticmethod
    def init() -> ConfigLoader:
        print("Initializing app, profiles: ", get_env_value(Env.APP_PROFILES)) # logging not yet configured, so we use print
        signal.signal(signal.SIGINT, App.shutdown)
        signal.signal(signal.SIGTERM, App.shutdown)
        Env.set_defaults()
        if is_production():
            init_tasks_cleanup(lambda: App.__shutting_down, 600)
        return ConfigLoader(os.path.join(os.getcwd(), 'resources', 'config'))

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
