import unittest

from ....main.aideas.web.element_selector import ElementSelector
from ....main.aideas.web.element_search_config import ElementSearchConfig

from ..test_functions import create_webdriver, get_agent_resource
from .noop_cookie_store import NoopCookieStore


class ElementSelectorTest(unittest.TestCase):
    def test_select_login(self):
        element_selector = get_element_selector()
        link = get_agent_resource("pictory", "login_page.html")
        element_name = 'username'
        search_from = ''
        search_for = '//*[@id="mui-1"]'
        search_config: ElementSearchConfig = ElementSearchConfig(search_from, search_for)
        body_element = element_selector.load_page_bodies(link)[0]
        result = element_selector.select_element(body_element, element_name, search_config)
        self.assertIsNotNone(result)

    # A few seconds after loading the page, the page was emptied of most
    # visual elements and simply displayed the message: Page Not Found.
    # This made the test to fail as we could not click the button.
    #
    # def test_select_brand(self):
    #     element_selector = get_element_selector()
    #     link = get_agent_resource("pictory", "storyboard_page.html")
    #     element_name = 'select-brand'
    #     search_from = ''
    #     search_for = '//*[@id="menu-"]/div[3]/ul/li[contains(text(), "LiveAbove3D")]'
    #     search_config: ElementSearchConfig = ElementSearchConfig(search_from, search_for)
    #     result: WebElement = element_selector.select_element(link, element_name, search_config)
    #     self.assertIsNotNone(result)

    # def test_enter_textinput(self):
    #     element_selector = _get_element_selector()
    #     link = get_agent_resource("pictory", "textinput_page.html")
    #     element_name = 'select-brand'
    #     search_from = ''
    #     search_for = '//*[@id="menu-"]/div[3]/ul/li[contains(text(), "LiveAbove3D")]'
    #     search_config: ElementSearchConfig = ElementSearchConfig(search_from, search_for)
    #     result: WebElement = element_selector.select_element(link, element_name, search_config)
    #     self.assertIsNotNone(result)


def get_element_selector() -> ElementSelector:
    webdriver = create_webdriver()
    return ElementSelector(webdriver, 10,
                           NoopCookieStore(webdriver, "test-domain"))


if __name__ == '__main__':
    unittest.main()

