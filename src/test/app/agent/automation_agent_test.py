from typing import Any
from unittest import mock

import unittest

from aideas.app.agent.agent_name import AgentName
from aideas.app.agent.automator_agent import AutomatorAgent
from aideas.app.agent.translation.translator import Translator
from aideas.app.run_context import RunContext
from test.app.test_functions import get_run_context, run_agent


class AutomationAgentTest(unittest.TestCase):
    def test_translate(self):
        agent_name = AgentName.TRANSLATION
        action_name = 'translate'
        run_context: RunContext = get_run_context([agent_name])

        with mock.patch.object(Translator, "translate") as translate:
            translate.return_value = "test-translation-result"
            agent_config = AutomationAgentTest._translation_config(
                action_name,
                '/Users/chinomso/dev_ai/automate-idea-to-social/src/test/resources/test-content/video.txt')

            agent = AutomatorAgent.of_config(
                agent_name, run_context.get_app_config().to_dict(), agent_config)

            result = run_agent(agent, run_context)
            self.assertTrue(result.is_successful())
            result = result.get_element_results('stage-0').get_action_result('stage-item-0', action_name).get_result()
            self.assertGreater(len(result), 0)


    def test_translate_subtitles(self):
        agent_name: str = AgentName.SUBTITLES_TRANSLATION
        action_name = 'translate_subtitles'
        run_context: RunContext = get_run_context([agent_name])

        with mock.patch.object(Translator, "translate") as translate:
            translate.return_value = "test-subtitles-translation-result"
            agent_config = AutomationAgentTest._translation_config(
                action_name,
                '/Users/chinomso/dev_ai/automate-idea-to-social/src/test/resources/test-content/subtitles.vtt')

            agent = AutomatorAgent.of_config(
                agent_name, run_context.get_app_config().to_dict(), agent_config)

            result = run_agent(agent, run_context)
            self.assertTrue(result.is_successful())
            result = result.get_element_results('stage-0').get_action_result('stage-item-0', action_name).get_result()
            self.assertGreater(len(result), 0)


    @staticmethod
    def _translation_config(action_name: str, file_path: str) -> dict[str, Any]:
        return {
            'stages': {
                'stage-0': {
                    'stage-items': {
                        'stage-item-0': {
                            'actions': [
                                "context verbose=true",
                                "context service-url=https://translate.googleapis.com/translate_a/single",
                                f"{action_name} {file_path} en de,es,fr"
                            ]
                        }
                    }
                }
            }
        }


if __name__ == '__main__':
    unittest.main()
