import logging.config
import unittest

from test.app.agent.test_blog_agent import TestBlogAgent
from test.app.test_functions import init_logging, get_config_loader
from aideas.app.agent.agent_name import AgentName
from aideas.app.run_context import RunContext

init_logging(logging.config)


class BlogAgentTest(unittest.TestCase):
    def test_run(self):
        app_config = get_config_loader().load_app_config()
        agent_name = AgentName.BLOG
        run_context: RunContext = RunContext.of_config(app_config, agent_name)
        agent_config = get_config_loader().load_agent_config(agent_name)
        agent = TestBlogAgent.of_config(agent_name, app_config, agent_config)

        result = agent.run(run_context)

        print(f'Completed. Result:\n{result.pretty_str()}')

        self.assertTrue(result.is_successful())


if __name__ == '__main__':
    unittest.main()
