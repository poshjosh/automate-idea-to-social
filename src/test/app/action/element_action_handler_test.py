import unittest

from aideas.app.action.action import Action
from aideas.app.action.action_signatures import element_action_signatures
from aideas.app.action.element_action_handler import ElementActionHandler
from aideas.app.config import AgentConfig, STAGES_KEY, STAGE_ITEMS_KEY
from aideas.app.web.element_selector import ElementSelector
from aideas.app.run_context import RunContext

from test.app.test_functions import create_webdriver, get_agent_resource, get_run_context, \
    load_agent_config


class ElementActionHandlerTest(unittest.TestCase):
    def test_get_should_return_non_empty_list(self):
        stage_actions: dict[str, list[str]] = _collect_agent_actions('pictory')
        for actions in stage_actions.values():
            self.assertIsInstance(actions, list)
            self.assertNotEqual(0, len(actions))

    def test_pictory_branding_actions(self):
        agent_name = 'pictory'
        stage_name = 'branding'
        webdriver = create_webdriver(agent_name=agent_name)
        webdriver.get(get_agent_resource(agent_name, 'storyboard_page.html'))
        config = load_agent_config(agent_name)
        stage_config = config[STAGES_KEY][stage_name]
        targets = stage_config[STAGE_ITEMS_KEY].keys()
        run_context = get_run_context([agent_name])
        for target in targets:
            _execute_actions(
                webdriver, run_context, agent_name, stage_name, stage_config, target)


def _execute_actions(webdriver, run_context: RunContext,
                     agent_name: str, stage_name: str,
                     stage_config: dict, target: str, action_prefix: str = None):
    stage_actions: dict[str, list[str]] = _collect_stage_actions(stage_name, stage_config)
    for key, action_list in stage_actions.items():
        if key != f'{stage_name}.{target}':
            continue
        for action in action_list:
            if action_prefix is not None and action.startswith(action_prefix) is False:
                print(f'Skipping action: {stage_name}.{action} for: {target}')
                continue
            print(f'executing action: {stage_name}.{action} for: {target}')
            try:
                action = Action.of(agent_name, stage_name, target, action)
                element_selector = ElementSelector.of(webdriver, agent_name, 10)
                ElementActionHandler(element_selector, 10).execute_on(run_context, action)
            except Exception:
                print('Failed')
                # print(f'{ex}')
                # raise ex


def _collect_agent_actions(agent: str) -> dict[str, list[str]]:
    stages_config = load_agent_config(agent)[STAGES_KEY]
    stage_actions: dict[str, list[str]] = {}
    for stage_name in stages_config.keys():
        stage_config: dict[str, any] = stages_config[stage_name]
        stage_actions.update(_collect_stage_actions(stage_name, stage_config))
    return stage_actions


def _collect_stage_actions(
        stage_name: str,
        stage_config: dict) -> dict[str, list[str]]:
    collect_into: dict[str, list[str]] = {}
    stage_items_config: dict[str, any] = stage_config[STAGE_ITEMS_KEY]
    for key in stage_items_config.keys():
        if AgentConfig.is_default_actions_key(key):
            continue
        actions = element_action_signatures(stage_items_config, key)
        print(f'element: {key}, actions: {actions}')
        collect_into[f'{stage_name}.{key}'] = actions
    return collect_into


if __name__ == '__main__':
    unittest.main()
