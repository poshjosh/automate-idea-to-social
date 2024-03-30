import logging.config
import unittest

from .test_functions import get_config_loader, init_logging
from .agent.test_agent_factory import TestAgentFactory
from ....main.app.aideas.app import App

init_logging(logging.config)


class AppIT(unittest.TestCase):
    def test_run(self):
        result = given_app().run()
        print(f'{result.pretty_str()}')
        self.assertTrue(result.is_successful())


def given_app() -> App:
    # This will result to the live app, which we don't want
    #return App.of_defaults(get_main_path('config'))
    agent_factory = TestAgentFactory(get_config_loader())
    return App(agent_factory, get_config_loader().load_app_config())


if __name__ == '__main__':
    unittest.main()
