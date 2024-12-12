import logging
import os
import signal
import sys

from .config_loader import ConfigLoader, SimpleConfigLoader
from .env import Env
from .task import shutdown as shutdown_tasks

logger = logging.getLogger(__name__)


class App:
    __shutdown = False

    @staticmethod
    def init() -> ConfigLoader:
        print("Initializing app...") # logging not yet configured, so we use print
        signal.signal(signal.SIGINT, App.shutdown)
        signal.signal(signal.SIGTERM, App.shutdown)
        Env.set_defaults()
        return SimpleConfigLoader(os.path.join(os.getcwd(), 'resources', 'config'))

    @staticmethod
    def shutdown(signum, _):
        logger.info(f"Received signal {signum} -> Shutting down...")
        shutdown_tasks()
        App.__shutdown = True
        logger.info("Done shutting down.")
        # TODO - Find out why shutdown is not achieved without this. On the other hand,
        #  when we remove this, we OFTEN receive the following warning:
        #  UserWarning: resource_tracker: There appear to be 2 leaked semaphore objects to clean up at shutdown
        sys.exit(1)

    @staticmethod
    def is_shutdown() -> bool:
        return App.__shutdown
