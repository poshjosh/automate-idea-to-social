import logging
from typing import Callable

from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class ReloadableWebElement(WebElement):
    def __init__(self,
                 delegate: WebElement,
                 reload: Callable[[int], WebElement],
                 timeout: float) -> None:
        super().__init__(delegate.parent, delegate.id)
        self.__delegate = delegate
        self.__reload = reload
        self.__timeout = timeout

    def load(self) -> WebElement:
        return self.__delegate if self.__delegate is not None else self.reload()

    def get_delegate(self) -> WebElement:
        return self.__delegate

    def reload(self) -> WebElement:
        logger.warning('Reloading element')
        return ReloadableWebElement.__run_till_success(self.__reload, self.__timeout)

    @staticmethod
    def __run_till_success(func: Callable[[int], WebElement], timeout: float = 60) -> WebElement:
        from datetime import datetime, timedelta
        start = datetime.now()
        max_time = timedelta(seconds=timeout)
        trials = -1
        while True:
            try:
                trials += 1
                return func(trials)
            except Exception as ex:
                if datetime.now() - start > max_time:
                    raise ex
