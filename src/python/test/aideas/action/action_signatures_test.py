import unittest

from ....main.aideas.action.action_signatures import event_action_signatures, parse_agent_to_stages
from ....main.aideas.event.event_handler import ON_SUCCESS


class ActionSignaturesTest(unittest.TestCase):
    def test_event_action_signatures(self):
        actions: list[str] = ["test-action-a test-arg0 test-arg1", "test-action-b"]
        events = {ON_SUCCESS: actions}
        config = {'events': events}
        action_signatures = event_action_signatures(config, ON_SUCCESS)
        self.assertEqual(actions, action_signatures)

    def test_parse_agent_to_stages_given_only_stages_specified(self):
        expected_action = "action"
        calling_agent = "agent"
        calling_stage = "stage_0"
        action, agent_to_stages = parse_agent_to_stages(
            f"{expected_action} stage_1 stage_2",
            calling_agent, calling_stage)
        self.assertEqual(expected_action, action)
        result = agent_to_stages.get(calling_agent)
        self.assertEqual("stage_1", result[0].get_value())
        self.assertEqual(calling_stage, result[0].get_id())
        self.assertEqual("stage_2", result[1].get_value())
        self.assertEqual(calling_stage, result[1].get_id())

    def test_parse_agent_to_stages_given_called_agent_specified(self):
        expected_action = "action"
        calling_agent = "agent-a"
        calling_stage = "stage-a_0"
        called_agent = "agent-b"
        called_stage = "stage-b_0"
        action, agent_to_stages = parse_agent_to_stages(
            f"{expected_action} {called_agent}.{called_stage} stage-a_1",
            calling_agent, calling_stage)
        self.assertEqual(expected_action, action)

        result = agent_to_stages.get(called_agent)
        self.assertEqual(called_stage, result[0].get_value())
        self.assertEqual(calling_stage, result[0].get_id())

        result = agent_to_stages.get(calling_agent)
        self.assertEqual("stage-a_1", result[0].get_value())
        self.assertEqual(calling_stage, result[0].get_id())


if __name__ == '__main__':
    unittest.main()
