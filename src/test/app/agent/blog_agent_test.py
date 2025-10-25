import os
from unittest import mock

import logging.config
import unittest

from aideas.app.agent.translation.translator import Translator
from test.app.agent.test_blog_agent import TestBlogAgent
from test.app.test_functions import init_logging, load_agent_config, get_run_context, run_agent
from aideas.app.agent.agent_name import AgentName
from aideas.app.run_context import RunContext

init_logging(logging.config)


class BlogAgentTest(unittest.TestCase):
    def test_run(self):
        agent_name = AgentName.BLOG
        run_context: RunContext = get_run_context([agent_name])
        agent = TestBlogAgent.of_config(
            agent_name,
            run_context.get_app_config().to_dict(),
            load_agent_config(agent_name, False))

        with mock.patch.object(Translator, 'translate_file_path') as translate_file_path:
            with mock.patch.object(Translator, 'translate') as translate:

                translate.side_effect = lambda text, from_lang_code, to_lang_code: text

                files_to_delete = []

                def mock_translate_file_path(file_path, _, to_lang_code):
                    name, ext = os.path.splitext(os.path.basename(file_path))
                    translated_file_path = os.path.join(os.path.dirname(file_path), f"{name}.{to_lang_code}{ext}")
                    files_to_delete.append(translated_file_path)
                    return translated_file_path

                translate_file_path.side_effect = mock_translate_file_path

                try:
                    result = run_agent(agent, run_context)
                    self.assertTrue(result.is_successful())
                finally:
                    [os.remove(f) for f in files_to_delete if os.path.exists(f)]


if __name__ == '__main__':
    unittest.main()
