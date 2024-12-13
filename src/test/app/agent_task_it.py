import logging.config
import unittest

from aideas.app.task import AgentTask
from test_functions import get_main_config_loader, init_logging, get_run_context
from agent.test_agent_factory import TestAgentFactory

init_logging(logging.config)


class AgentTaskIT(unittest.TestCase):
    def test_run(self):
        result = given_task().start()
        print(f'{result.pretty_str()}')
        self.assertTrue(result.is_successful())


def given_task() -> AgentTask:
    # This will result to a live task, which we don't want
    #return AgentTask.of_defaults(get_main_config_loader(), load_run_config())
    agent_factory = TestAgentFactory(get_main_config_loader())
    return AgentTask(agent_factory, get_run_context())


if __name__ == '__main__':
    unittest.main()
