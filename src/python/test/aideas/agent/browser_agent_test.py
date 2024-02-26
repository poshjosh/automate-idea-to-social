import logging.config
import unittest

from .test_browser_agent import TestBrowserAgent
from .test_agent_inputs import TestAgentInputs
from ..test_functions import get_logging_config, load_app_config, load_agent_config
from ....main.aideas.agent.agent_names import AgentNames

logging.config.dictConfig(get_logging_config())


class BrowserAgentTest(unittest.TestCase):
    def test_run(self):
        agent_name: str = AgentNames.PICTORY
        config = load_app_config()
        print(f'Loaded app config: {config}')
        agent_config = load_agent_config(agent_name)
        agent = TestBrowserAgent.of_config(config, agent_config)
        inputs = TestAgentInputs().get(agent_name)
        print(f'Will run agent with inputs: {inputs}')
        result = agent.run(inputs)
        print(f'Completed.\nResult: {result.pretty_str()}')
        self.assertTrue(result.is_successful())


if __name__ == '__main__':
    unittest.main()
