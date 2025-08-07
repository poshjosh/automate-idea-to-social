import os
import unittest

from aideas.app.config import RunArg
from aideas.app.env import Env
from test.app.test_functions import get_main_config_loader


class ConfigLoaderTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_agent_variables(self):
        config_loader = get_main_config_loader()
        agent_names: [str] = config_loader.get_all_agent_names()
        self.assertGreater(len(agent_names), 0)

    def test_external_config_loads(self):
        config_1 = get_main_config_loader().load_run_config()
        # print(f"Run config 1: {config_1}")
        config_1_val = config_1[RunArg.SHARE_COVER_IMAGE.value]
        self.assertFalse(config_1_val)
        environ = Env.collect()
        environ['CONFIG_DIR'] = 'test/resources/config/external'
        config_2 = get_main_config_loader(environ).load_run_config()
        # print(f"Run config 2: {config_2}")
        config_2_val = config_2[RunArg.SHARE_COVER_IMAGE.value]
        self.assertNotEqual(config_1_val, config_2_val)

if __name__ == '__main__':
    unittest.main()
