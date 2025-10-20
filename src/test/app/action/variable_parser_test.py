
import os
import unittest

from pyu.io.variable_parser import SELF_KEY

from aideas.app.action.action import Action
from aideas.app.action.action_result import ActionResult
from aideas.app.action.variable_parser import get_run_arg_replacement, replace_all_variables, \
    to_results_variable, get_variables
from aideas.app.agent.agent_name import AgentName
from aideas.app.run_context import RunContext
from test.app.test_functions import load_agent_config, get_run_context, get_main_config_loader

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

    def test_get_variables_given_empty_data(self):
        config = {}
        variables: [str] = get_variables(config, True)
        self.assertEqual(len(variables), 0)

    def test_get_variables_given_no_variables(self):
        config = {
            'a': {
                'b': {
                    'bool': False, 'list': [0, 1], 'dict': {'k0': 'v0', 'k1': 'v1'}
                }
            },
            'name': 'Jane'
        }
        variables: [str] = get_variables(config, True)
        self.assertEqual(len(variables), 0)

    def test_get_variables(self):
        config = {
            'a': {
                'b': {
                    'bool': False, 'list': [0, 1], 'dict': {'k0': 'v0', 'k1': 'v1'}
                }
            },
            'scoped': '$' + SELF_KEY + '.user_name',
            'unscoped': '$USER_NAME'
        }

        variables: [str] = get_variables(config, True)
        self.assertEqual(len(variables), 2)

    def test_get_unscoped_variables(self):
        config = {
            'a': {
                'b': {
                    'bool': False, 'list': [0, 1], 'dict': {'k0': 'v0', 'k1': 'v1'}
                }
            },
            'scoped': '$' + SELF_KEY + '.user_name',
            'unscoped': '$USER_NAME'
        }

        variables: [str] = get_variables(config, False)
        self.assertEqual(len(variables), 1)

    def __given_run_context_with_results(self, results: [str]) -> RunContext:
        run_context: RunContext = get_run_context([agent_name])
        self.__given_action_results(results, run_context)
        return run_context

    @staticmethod
    def __given_action_results(results: [str], run_context: RunContext) -> list[ActionResult]:
        output: list[ActionResult] = []
        for r in results:
            action_result = create_action_result(r)
            run_context.add_action_result(action_result)
            output.append(action_result)
        return output

    def test_replace_all_variables(self):
        agents: list[str] = get_main_config_loader().get_agent_names()
        for agent in agents:
            # TODO: Remove this exclusion and fix the test for the named agent
            if AgentName.SOCIAL_MEDIA_POSTER == agent:
                continue
            agent_config = load_agent_config(agent, False)
            variable_source = get_run_context([agent]).get_run_config().to_dict()
            replace_all_variables(agent_config, variable_source)


if __name__ == '__main__':
    unittest.main()
