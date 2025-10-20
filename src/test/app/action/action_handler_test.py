from unittest import mock

import unittest

from content_publisher.app.app import App
from content_publisher.app.content_publisher import Content

from aideas.app.action.action import Action
from aideas.app.action.action_handler import ActionHandler, ActionId
from aideas.app.agent.agent_name import AgentName
from aideas.app.run_context import RunContext

from test.app.action.action_handler_helper import ActionHandlerHelper
from test.app.test_functions import get_run_context, get_main_config_loader


class ActionHandlerTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = ActionHandlerHelper()

    def test_actions_should_be_non_empty_list(self):
        agent_names: list[str] = get_main_config_loader().get_agent_names()
        for agent_name in agent_names:
            stage_actions: dict[str, list[str]] = self.helper.collect_agent_actions(agent_name)
            for actions in stage_actions.values():
                self.assertIsInstance(actions, list)
                self.assertNotEqual(0, len(actions))
        pass

    def test_publish_content(self):
        agent_name = AgentName.SOCIAL_MEDIA_POSTER
        expected_result = { "success": True }
        action_handler = ActionHandler()
        with mock.patch.object(App, 'publish_content') as mock_publish_content:
            with mock.patch.object(Content, 'of_dir'):
                mock_publish_content.return_value = expected_result
                run_context: RunContext = get_run_context([agent_name])
                action = Action(agent_name,
                                "main",
                                "publish-content-social-media",
                                ActionId.PUBLISH_CONTENT.value,
                                '-p youtube -o portrait -t fake-title -d /fake/dir'.split(' '))
                result = action_handler.execute(run_context, action)
                self.assertEqual(result.get_result(), expected_result)


if __name__ == '__main__':
    unittest.main()
