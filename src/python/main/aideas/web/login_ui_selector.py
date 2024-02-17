import logging

from .login_ui_selector_xpath import LoginUiSelectorXpath
from .login_ui_selector_brute import LoginUiSelectorBrute

logger = logging.getLogger(__name__)


class LoginUiSelector:

    def select(self, webdriver, link: str, xpath_config: dict[str, str]) -> list[dict]:
        if xpath_config is None:
            return LoginUiSelectorBrute().select(webdriver, link)
        return LoginUiSelectorXpath().select(webdriver, link, xpath_config)
