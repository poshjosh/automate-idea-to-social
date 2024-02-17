from aideas.setup.setup import init_app
from aideas.web.browser import Browser
from aideas.pictory.pictory_agent import PictoryAgent

# TODO - Try to make logging work for the package of this script

if __name__ == "__main__":

    config = init_app()

    browser: Browser = Browser.create(config)

    success: bool = False
    try:
        success = PictoryAgent(browser).run(config["agents"]["pictory"]["ui"])
    except Exception as ex:
        print(f'Error: {ex}')
    finally:
        if success is not True:
            browser.quit()
