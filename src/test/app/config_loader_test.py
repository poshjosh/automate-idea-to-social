import unittest

from test.app.test_functions import get_main_config_loader


class ConfigLoaderTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_agent_variables(self):
        config_loader = get_main_config_loader()
        agent_names: [str] = config_loader.get_all_agent_names()
        self.assertGreater(len(agent_names), 0)


if __name__ == '__main__':
    unittest.main()
