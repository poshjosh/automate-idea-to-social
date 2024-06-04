import logging
import os
from typing import TypeVar, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

from ..config import BrowserConfig
from ..env import Env, get_value

logger = logging.getLogger(__name__)

WEB_DRIVER = TypeVar("WEB_DRIVER", bound=Union[webdriver.Chrome, uc.Chrome])


class WebDriverCreator:
    @staticmethod
    def create(config: dict[str, any]) -> WEB_DRIVER:

        browser_config: BrowserConfig = BrowserConfig(config)

        WebDriverCreator.__create_dirs_if_need([browser_config.get_download_dir()])

        options: Options = WebDriverCreator.__collect_options(
            browser_config.get_options(),
            {} if browser_config.is_undetected() is True else browser_config.prefs())

        if "headless" not in options.arguments and get_value(Env.SETUP_DISPLAY, False) is False:
            logger.warning("DISPLAY is not set up. Webdriver may crash.")

        if browser_config.is_undetected():
            logger.debug("Undetected ChromeDriver will be used")
            # See https://github.com/ultrafunkamsterdam/undetected-chromedriver
            # TODO - Find out why this takes about 10 minutes to complete
            # It took about 10 minutes for this next line to complete, at least on local machine
            driver = uc.Chrome(options=options, use_subprocess=False)
            download_dir: str = browser_config.get_download_dir()
            if not download_dir:
                return driver
            # Defines autodownload and download PATH
            # See https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/260
            params = {
                "behavior": "allow",
                "downloadPath": browser_config.get_download_dir()
            }
            driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
            return driver

        logger.debug("ChromeDriver will be used")
        if not browser_config.get_executable_path():
            return webdriver.Chrome(options=options)

        service = webdriver.ChromeService(executable_path=browser_config.get_executable_path())
        return webdriver.Chrome(options=options, service=service)

    @staticmethod
    def __create_dirs_if_need(dirs: list[str]):
        for to_create in dirs:
            if not to_create:
                return
            if os.path.exists(to_create):
                return
            os.makedirs(to_create)
            logger.debug(f"Created dirs: {to_create}")

    @staticmethod
    def __collect_options(option_args: list[str], prefs: dict[str, str]) -> Options:
        logger.debug(f'Will create browser with\nprefs: {prefs}\noptions: {option_args}')
        options = Options()
        if option_args:
            for arg in option_args:
                if not arg:
                    continue
                options.add_argument("--" + arg)

        if not prefs:
            return options

        options.add_experimental_option("prefs", prefs)
        return options
