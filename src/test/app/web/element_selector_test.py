import unittest

from aideas.app.web.element_selector import ElementSelector
from aideas.app.config import SearchBy, SearchConfig, SearchConfigs
from aideas.app.env import get_cookies_file

from test.app.test_functions import create_webdriver, get_agent_resource
from test.app.web.noop_cookie_store import NoopCookieStore


class ElementSelectorTest(unittest.TestCase):
    def test_select_login(self):
        link = get_agent_resource("pictory", "login_page.html")
        search_for = '//*[@id="mui-1"]'
        self.__select_element_given_xpath_should_return_element(link, search_for)

    # A few seconds after loading the page, the page was emptied of most
    # visual elements and simply displayed the message: Page Not Found.
    # This made the test to fail as we could not click the button.
    #
    # def test_select_brand(self):
    #     link = get_agent_resource("pictory", "storyboard_page.html")
    #     search_for = '//*[@id="menu-"]/div[3]/ul/li[contains(text(), "LiveAbove3D")]'
    #     self.__select_element_given_xpath_should_return_element(link, search_for)
    #
    # def test_enter_textinput(self):
    #     link = get_agent_resource("pictory", "textinput_page.html")
    #     search_for = '//*[@id="menu-"]/div[3]/ul/li[contains(text(), "LiveAbove3D")]'
    #     self.__select_element_given_xpath_should_return_element(link, search_for)

    def __select_element_given_xpath_should_return_element(self, link: str, xpath: str):
        webdriver = create_webdriver()
        element_selector = get_element_selector(webdriver)
        webdriver.get(link)
        search_config: SearchConfig = SearchConfig(SearchBy.XPATH, xpath)
        result = element_selector.select_element(SearchConfigs(search_config))
        self.assertIsNotNone(result)


def get_element_selector(webdriver=None) -> ElementSelector:
    if webdriver is None:
        webdriver = create_webdriver()
    cookie_store = NoopCookieStore(webdriver, get_cookies_file("test-agent"))
    return ElementSelector(webdriver, 10, cookie_store)


if __name__ == '__main__':
    unittest.main()

