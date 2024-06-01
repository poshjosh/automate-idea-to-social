import unittest

from aideas.app.agent.event_handler import parse_agent_to_stages


class ActionSignaturesTest(unittest.TestCase):
    def test_parse_agent_to_stages_given_only_stages_specified(self):
        expected_action = "action"
        calling_agent = "agent"
        calling_stage = "stage_0"
        action, agent_to_stages = parse_agent_to_stages(
            f"{expected_action} stage_1 stage_2",
            calling_agent, calling_stage)
        self.assertEqual(expected_action, action)
        result = agent_to_stages.get(calling_agent)
        self.assertEqual("stage_1", result[0].value)
        self.assertEqual(calling_stage, result[0].id)
        self.assertEqual("stage_2", result[1].value)
        self.assertEqual(calling_stage, result[1].id)

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
        self.assertEqual(called_stage, result[0].value)
        self.assertEqual(calling_stage, result[0].id)

        result = agent_to_stages.get(calling_agent)
        self.assertEqual("stage-a_1", result[0].value)
        self.assertEqual(calling_stage, result[0].id)


if __name__ == '__main__':
    unittest.main()
