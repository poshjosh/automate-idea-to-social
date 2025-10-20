from aideas.app.action.action import Action
from aideas.app.action.action_handler import ActionHandler
from aideas.app.action.action_signatures import element_action_signatures
from aideas.app.config import AgentConfig, STAGES_KEY, STAGE_ITEMS_KEY
from aideas.app.run_context import RunContext

from test.app.test_functions import load_agent_config


class ActionHandlerHelper:
    @staticmethod
    def execute_actions(action_handler: ActionHandler, run_context: RunContext,
                         agent_name: str, stage_name: str,
                         stage_config: dict, target: str, action_prefix: str = None):
        stage_actions: dict[str, list[str]] = ActionHandlerHelper.collect_stage_actions(stage_name, stage_config)
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
                    action_handler.execute_on(run_context, action)
                except Exception:
                    print('Failed')
                    # print(f'{ex}')
                    # raise ex

    @staticmethod
    def collect_agent_actions(agent: str) -> dict[str, list[str]]:
        stages_config = load_agent_config(agent, False)[STAGES_KEY]
        stage_actions: dict[str, list[str]] = {}
        for stage_name in stages_config.keys():
            stage_config: dict[str, any] = stages_config[stage_name]
            stage_actions.update(ActionHandlerHelper.collect_stage_actions(stage_name, stage_config))
        return stage_actions

    @staticmethod
    def collect_stage_actions(stage_name: str, stage_config: dict) -> dict[str, list[str]]:
        collect_into: dict[str, list[str]] = {}
        if not stage_config:
            return collect_into
        stage_items_config: dict[str, any] = stage_config.get(STAGE_ITEMS_KEY, {})
        for key in stage_items_config.keys():
            if AgentConfig.is_default_actions_key(key):
                continue
            actions = element_action_signatures(stage_items_config, key)
            # print(f'element: {key}, actions: {actions}')
            collect_into[f'{stage_name}.{key}'] = actions
        return collect_into