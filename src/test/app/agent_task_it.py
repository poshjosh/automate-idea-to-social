import logging.config
import unittest

from aideas.app.config import RunArg
from aideas.app.task import AgentTask
from test_functions import get_main_config_loader, init_logging

init_logging(logging.config)


class AgentTaskIT(unittest.TestCase):
    def test_run(self):
        result = given_task(["test-agent"]).start()
        # print(f'{result.pretty_str()}')
        self.assertTrue(result.is_successful())


def given_task(agent_names: list[str] = None) -> AgentTask:
    config_loader = get_main_config_loader()
    run_config = config_loader.load_run_config()
    if agent_names:
        run_config[str(RunArg.AGENTS.value)] = agent_names
    return AgentTask.of_defaults(config_loader, run_config)


if __name__ == '__main__':
    unittest.main()
