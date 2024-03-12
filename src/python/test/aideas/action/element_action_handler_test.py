import unittest

from ....main.aideas.action.action import Action
from ....main.aideas.action.action_signatures import element_action_signatures
from ....main.aideas.action.element_action_handler import ElementActionHandler
from ....main.aideas.config import AgentConfig, STAGES_KEY, STAGE_ITEMS_KEY

from ..test_functions import create_webdriver, get_agent_resource, get_config_loader


class ElementActionHandlerTest(unittest.TestCase):
    def test_get_should_return_non_empty_list(self):
        stage_actions: dict[str, list[str]] = _collect_agent_actions('pictory')
        for actions in stage_actions.values():
            self.assertIsInstance(actions, list)
            self.assertNotEqual(0, len(actions))

    def test_pictory_branding_actions(self):
        agent_name = 'pictory'
        stage_name = 'branding'
        webdriver = create_webdriver()
        webdriver.get(get_agent_resource(agent_name, 'storyboard_page.html'))
        config = get_config_loader().load_agent_config(agent_name)
        stage_config = config[STAGES_KEY][stage_name]
        targets = stage_config[STAGE_ITEMS_KEY].keys()
        for target in targets:
            _execute_actions(webdriver, agent_name, stage_name, stage_config, target, None)


def _execute_actions(webdriver, agent_name: str, stage_name: str, stage_config: dict, target: str, action_prefix: str):
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
                ElementActionHandler(webdriver, 10).execute(action)
            except Exception as ex:
                print('Failed')
                # print(f'{ex}')
                # raise ex


def _collect_agent_actions(agent: str) -> dict[str, list[str]]:
    stages_config = get_config_loader().load_agent_config(agent)[STAGES_KEY]
    stage_actions: dict[str, list[str]] = {}
    for stage_name in stages_config.keys():
        stage_config: dict[str, any] = stages_config[stage_name]
        stage_actions.update(_collect_stage_actions(stage_name, stage_config))
    return stage_actions


def _collect_stage_actions(
        stage_name: str,
        stage_config: dict) -> dict[str, list[str]]:
    collect_into: dict[str, list[str]] = {}
    ui_config: dict[str, any] = stage_config[STAGE_ITEMS_KEY]
    for key in ui_config.keys():
        if AgentConfig.is_default_actions_key(key):
            continue
        actions = element_action_signatures(ui_config, key)
        print(f'element: {key}, actions: {actions}')
        collect_into[f'{stage_name}.{key}'] = actions
    return collect_into


if __name__ == '__main__':
    unittest.main()
