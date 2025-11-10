from unittest import mock

import unittest

from content_publisher.app.app import App
from content_publisher.app.content_publisher import Content, PostResult

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

    def test_publish_content(self):
        agent_name = AgentName.REDDIT_API
        post_url = "https://test.post.url.com"
        post_result = { "success": PostResult(success=True, post_url=post_url) }
        action_handler = ActionHandler()
        with mock.patch.object(App, 'publish_content') as mock_publish_content:
            with mock.patch.object(Content, 'of_dir'):
                mock_publish_content.return_value = post_result
                run_context: RunContext = get_run_context([agent_name])
                action = Action(agent_name,
                                "main",
                                "publish-content-social-media",
                                ActionId.PUBLISH_CONTENT.value,
                                '-p youtube -o portrait -t fake-title -d /fake/dir'.split(' '))
                result = action_handler.execute(run_context, action)
                self.assertEqual(result.get_result(), [post_url])

    def test_context_given_list_format_string(self):
        agent_name = "test-agent"
        key = "subtitles-files"
        value = "['/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.ar.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.bn.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.de.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.es.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.fr.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.hi.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.it.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.ja.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.ko.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.ru.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.tr.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.uk.vtt', '/Users/chinomso/.aideas/content/subtitles/subtitles_b4b0b5ab-e30b-4533-972d-c9f6078efcf6.zh.vtt']"
        action_signature = f"context {key}={value}"
        run_context = get_run_context([agent_name])
        action = Action.of(agent_name, "test-stage", "test-stage-item",
                           action_signature, run_context)
        ActionHandler.context(run_context, action)
        self.assertEqual(value, run_context.get(key))


if __name__ == '__main__':
    unittest.main()
