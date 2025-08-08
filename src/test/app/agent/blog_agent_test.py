import logging.config
import unittest

from test.app.agent.test_blog_agent import TestBlogAgent
from test.app.test_functions import init_logging, load_agent_config, get_run_context
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

        result = agent.run(run_context)

        print(f'Completed. Result:\n{result.pretty_str()}')

        self.assertTrue(result.is_successful())


if __name__ == '__main__':
    unittest.main()
