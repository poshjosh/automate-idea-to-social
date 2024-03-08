import logging.config
import unittest

from .test_blog_updater_agent import TestBlogUpdaterAgent
from ..test_functions import init_logging, get_config_loader
from ....main.aideas.agent.agent_name import AgentName
from ....main.aideas.run_context import RunContext

init_logging(logging.config)


class BlogUpdaterAgentIT(unittest.TestCase):
    def test_run(self):
        app_config = get_config_loader().load_app_config()
        agent_name = AgentName.BLOG_UPDATER
        run_context: RunContext = RunContext.of_config(app_config, agent_name)
        agent_config = get_config_loader().load_agent_config(agent_name)
        agent = TestBlogUpdaterAgent.of_config(agent_config)

        result = agent.run(run_context)

        print(f'Completed. Result:\n{result.pretty_str()}')

        self.assertTrue(result.is_successful())


if __name__ == '__main__':
    unittest.main()
