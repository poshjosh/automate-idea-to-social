from unittest import mock

import unittest

from aideas.app.config import RunArg
from aideas.app.config_loader import ConfigLoader
from test.app.test_functions import get_main_config_loader, get_run_context, get_test_config_loader


class ConfigLoaderTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_agent_config_order(self):
        agent = "test-parent-agent"
        variables = get_run_context([agent]).get_run_config().to_dict()
        agent_config = get_test_config_loader(variables).load_agent_config(agent)
        stages = agent_config.get("stages").keys()
        # print("Stages: ", stages)
        self.assertListEqual(list(stages), ['one', 'two', 'three'])
        stage_items = agent_config.get("stages").get("three").get("stage-items").keys()
        # print("Stage['three'] items: ", stage_items)
        self.assertListEqual(list(stage_items), ['stage-item-a', 'stage-item-b', 'stage-item-c'])

    def test_child_config_overrides_parent(self):
        child_name = "test-child-agent"
        variables = get_run_context([child_name]).get_run_config().to_dict()
        child_config = get_test_config_loader(variables).load_agent_config(child_name)
        print("Child config: ", child_config)
        stages = child_config.get("stages").keys()
        # print("Stages: ", stages)
        self.assertListEqual(list(stages), ['one', 'two', 'three'])
        result = child_config.get("stages").get("two")
        self.assertEqual(result, "overridden")

    def test_agent_variables(self):
        config_loader = get_main_config_loader()
        agent_names: list[str] = config_loader.get_agent_names()
        self.assertGreater(len(agent_names), 0)

    def test_external_config_loads(self):
        config_1 = get_main_config_loader().load_run_config()
        config_1_val = config_1[RunArg.SHARE_COVER_IMAGE.value]
        with mock.patch.object(ConfigLoader, "_load_from_external_path") as _load_from_external_path:
            _load_from_external_path.return_value = { RunArg.SHARE_COVER_IMAGE.value: not config_1_val }
            config_2 = get_main_config_loader().load_run_config()
            config_2_val = config_2[RunArg.SHARE_COVER_IMAGE.value]
            self.assertNotEquals(config_1_val, config_2_val)

if __name__ == '__main__':
    unittest.main()
