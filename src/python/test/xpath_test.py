import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as WaitCondition

# <form style="float:right;display:inline-block;margin:0;border:0;padding:0">
#   <label>
#     <input type="text" id="search-form_search-box" class="searchInput" value="" placeholder="Type to search...">
#   </label>
#   <input type="submit" class="emphasis-button" value="Search">
# </form>

timeout: float = 20


def _create_webdriver():
    options = Options()
    return webdriver.Chrome(options=options)


class MyTestCase(unittest.TestCase):

    def test_something(self):
        webdriver = _create_webdriver()
        webdriver.get('http://chinomsoikwuagwu.com/')

        # See expected html dom structure above

        search_box = WebDriverWait(webdriver, timeout).until(
            WaitCondition.presence_of_element_located(
                (By.XPATH, "//*[@id=\"search-form_search-box\"]")))
        print("Found search_box id: ", search_box.get_attribute("id"))

        parent = WebDriverWait(search_box, timeout).until(
            WaitCondition.presence_of_element_located(
                (By.XPATH, ".//..//..")))
        print("Found parent: ", parent.tag_name)
        self.assertEqual(parent.tag_name, "form")

        parent = WebDriverWait(search_box, timeout).until(
            WaitCondition.presence_of_element_located(
                (By.XPATH, "./parent::*/parent::*")))
        print("Found parent: ", parent.tag_name)
        self.assertEqual(parent.tag_name, "form")


if __name__ == '__main__':
    unittest.main()
