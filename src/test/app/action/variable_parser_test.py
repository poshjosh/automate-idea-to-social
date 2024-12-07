
import os
import unittest

from aideas.app.action.action import Action
from aideas.app.action.action_result import ActionResult
from aideas.app.action.variable_parser import get_run_arg_replacement, replace_all_variables, \
    to_results_variable
from aideas.app.agent.agent_name import AgentName
from aideas.app.run_context import RunContext
from test.app.test_functions import load_app_config, load_agent_config, get_run_context

agent_name: str = AgentName.PICTORY
stage_name: str = "test-stage"
element_name: str = "test-success-0"
curr_path = [agent_name, stage_name, element_name]


def create_action_result(result: any) -> ActionResult:
    return ActionResult(
        Action.of(agent_name, stage_name, element_name, 'test-action'),
        True, result)


class VariableParserTest(unittest.TestCase):
    def test_get_run_arg_replacement_without_index(self):
        expected = ['test-result-0']
        run_context = self.__given_run_context_with_results(expected)
        result = get_run_arg_replacement(curr_path, to_results_variable(curr_path), run_context)
        self.assertListEqual(expected, result)

    def test_get_run_arg_replacement_with_me_reference_and_without_index(self):
        expected = ['test-result-0']
        run_context = self.__given_run_context_with_results(expected)
        result = get_run_arg_replacement(curr_path, to_results_variable(['me']), run_context)
        self.assertListEqual(expected, result)

    def test_get_run_arg_replacement_with_index(self):
        expected = 'test-result-1'
        run_context = self.__given_run_context_with_results(['test-result-0', expected])
        result = get_run_arg_replacement(
            curr_path, f'{to_results_variable(curr_path)}[1]', run_context)
        self.assertEqual(expected, result)

    def test_get_run_arg_replacement_with_me_reference_and_index(self):
        expected = 'test-result-1'
        run_context = self.__given_run_context_with_results(['test-result-0', expected])
        result = get_run_arg_replacement(
            curr_path, f'{to_results_variable(["me"])}[1]', run_context)
        self.assertEqual(expected, result)

    def __given_run_context_with_results(self, results: [str]) -> RunContext:
        run_context: RunContext = get_run_context([agent_name])
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

    def test_replace_all_variables(self):
        agents: [str] = load_app_config().get("agents")
        for agent in agents:
            self.replace_all_variables(load_agent_config(agent))

    @staticmethod
    def replace_all_variables(agent_config: dict[str, any]):
        replace_all_variables(agent_config, dict(os.environ))


if __name__ == '__main__':
    unittest.main()
