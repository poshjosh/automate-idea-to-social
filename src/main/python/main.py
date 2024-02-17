import logging

from aideas.setup.setup import init_app
from aideas.web.browser import Browser
from aideas.pictory.pictory_agent import PictoryAgent

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    config = init_app()

    option_args = config['browser']['chrome']['options']['args']
    remote_dvr = config['selenium.webdriver.url'] if 'selenium.webdriver.url' in config else None
    browser = Browser(option_args, remote_dvr)

    try:
        success: bool = PictoryAgent(browser).run(config["agents"]["pictory"]["ui"])
        logger.info(f'Pictory Agent success: {success}')
    except Exception as ex:
        logger.error(f'Error: {ex}')
    finally:
        if success is not True:
            browser.quit()
