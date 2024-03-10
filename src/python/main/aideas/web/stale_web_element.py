from typing import Callable

from selenium.webdriver.remote.webelement import WebElement


class StaleWebElement(WebElement):
    def __init__(self,
                 delegate: WebElement,
                 reload: Callable[[int], WebElement],
                 timeout: float) -> None:
        super().__init__(delegate.parent, delegate.id)
        self.__reload = reload
        self.__timeout = timeout

    def reload(self) -> WebElement:
        return StaleWebElement.__run_till_success(self.__reload, self.__timeout)

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
