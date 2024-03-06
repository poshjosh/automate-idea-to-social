import os
import unittest

from ....main.aideas.action.action import Action
from ....main.aideas.action.action_result import ActionResult
from ....main.aideas.action.variable_parser import (
    parse_run_arg, parse_variables, replace_all_variables, to_results_variable)
from ....main.aideas.agent.agent_name import AgentName
from ....main.aideas.run_context import RunContext
from ..test_functions import get_config_loader


agent_name: str = AgentName.PICTORY
stage_name: str = "test-stage"
element_name: str = "test-success-0"
curr_path = [agent_name, stage_name, element_name]


def create_action_result(result: any) -> ActionResult:
    return ActionResult(
        Action.of(agent_name, stage_name, element_name, 'test-action'),
        True, result)


class VariableParserTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_config = get_config_loader().load_app_config()

    def test_parse_run_arg_without_index(self):
        expected = 'test-result-0'
        run_context = self.__given_run_context_with_results([expected])
        result = parse_run_arg(curr_path, to_results_variable(curr_path), run_context)
        self.assertEqual(expected, result)

    def test_parse_run_arg_with_me_reference_and_without_index(self):
        expected = 'test-result-0'
        run_context = self.__given_run_context_with_results([expected])
        result = parse_run_arg(curr_path, to_results_variable(['me']), run_context)
        self.assertEqual(expected, result)

    def test_parse_run_arg_with_index(self):
        expected = 'test-result-1'
        run_context = self.__given_run_context_with_results(['test-result-0', expected])
        result = parse_run_arg(curr_path, f'{to_results_variable(curr_path)}[1]', run_context)
        self.assertEqual(expected, result)

    def test_parse_run_arg_with_me_reference_and_index(self):
        expected = 'test-result-1'
        run_context = self.__given_run_context_with_results(['test-result-0', expected])
        result = parse_run_arg(curr_path, f'{to_results_variable(["me"])}[1]', run_context)
        self.assertEqual(expected, result)

    def __given_run_context_with_results(self, results: [str]) -> RunContext:
        run_context: RunContext = RunContext.of_config(self.app_config, agent_name)
        self.__given_action_results(results, run_context)
        return run_context

    @staticmethod
    def __given_action_results(results: [str], run_context: RunContext) -> list[ActionResult]:
        output: list[ActionResult] = []
        for r in results:
            action_result = create_action_result(r)
            run_context.add_action_result(agent_name, stage_name, action_result)
            output.append(action_result)
        return output

    def test_parse_all_variables_given_single_variable(self):
        text = '$k'
        result = parse_variables(text, {'k': 'v'})
        self.assertEqual('v', result)

    def test_parse_all_variables_given_single_enclosed_variable(self):
        text = '${k}'
        result = parse_variables(text, {'k': 'v'})
        self.assertEqual('v', result)

    def test_parse_all_variables_given_multiple_variables_in_middle(self):
        text = 'before $k_0 $k_1 after'
        result = parse_variables(text, {'k_0': 'v_0', 'k_1': 'v_1'})
        self.assertEqual('before v_0 v_1 after', result)

    def test_parse_all_variables_given_multiple_enclosed_variables_in_middle(self):
        text = 'before ${k_0} ${k_1} after'
        result = parse_variables(text, {'k_0': 'v_0', 'k_1': 'v_1'})
        self.assertEqual('before v_0 v_1 after', result)

    def test_parse_all_variables_given_multiple_variables_at_start(self):
        text = '$k_0 $k_1 after'
        result = parse_variables(text, {'k_0': 'v_0', 'k_1': 'v_1'})
        self.assertEqual('v_0 v_1 after', result)

    def test_parse_all_variables_given_multiple_enclosed_variables_at_start(self):
        text = '${k_0} ${k_1} after'
        result = parse_variables(text, {'k_0': 'v_0', 'k_1': 'v_1'})
        self.assertEqual('v_0 v_1 after', result)

    def test_parse_all_variables_given_multiple_variables_at_end(self):
        text = 'before $k_0 $k_1'
        result = parse_variables(text, {'k_0': 'v_0', 'k_1': 'v_1'})
        self.assertEqual('before v_0 v_1', result)

    def test_parse_all_variables_given_multiple_enclosed_variables_at_end(self):
        text = 'before ${k_0} ${k_1}'
        result = parse_variables(text, {'k_0': 'v_0', 'k_1': 'v_1'})
        self.assertEqual('before v_0 v_1', result)

    def test_replace_all_variables(self):
        agents: [str] = get_config_loader().load_app_config().get("agents")
        for agent in agents:
            self.replace_all_variables(get_config_loader().load_agent_config(agent))

    @staticmethod
    def replace_all_variables(agent_config: dict[str, any]):
        replace_all_variables(agent_config, dict(os.environ))


if __name__ == '__main__':
    unittest.main()
