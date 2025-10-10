import unittest

from aideas.app.action.element_action_handler import ElementActionHandler
from aideas.app.agent.agent_name import AgentName
from aideas.app.config import STAGES_KEY, STAGE_ITEMS_KEY
from aideas.app.web.element_selector import ElementSelector

from test.app.action.action_handler_helper import ActionHandlerHelper
from test.app.test_functions import create_webdriver, get_agent_resource, get_run_context, \
    load_agent_config


class ElementActionHandlerTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = ActionHandlerHelper()

    def test_actions_should_be_non_empty_list(self):
        stage_actions: dict[str, list[str]] = self.helper.collect_agent_actions(AgentName.PICTORY)
        for actions in stage_actions.values():
            self.assertIsInstance(actions, list)
            self.assertNotEqual(0, len(actions))

    def test_pictory_branding_actions(self):
        agent_name = 'pictory'
        stage_name = 'branding'
        config = load_agent_config(agent_name, False)
        webdriver = create_webdriver(agent_name, config)
        webdriver.get(get_agent_resource(agent_name, 'storyboard_page.html'))
        stage_config = config[STAGES_KEY][stage_name]
        targets = stage_config[STAGE_ITEMS_KEY].keys()
        run_context = get_run_context([agent_name])

        element_selector = ElementSelector.of(webdriver, agent_name, 10)
        action_handler = ElementActionHandler(element_selector, 10)

        for target in targets:
            self.helper.execute_actions(action_handler, run_context, agent_name, stage_name, stage_config, target)


if __name__ == '__main__':
    unittest.main()
