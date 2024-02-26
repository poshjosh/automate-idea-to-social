import logging.config
import os
import unittest

from ...agent.test_agent_inputs import TestAgentInputs
from ...test_functions import get_logging_config, load_agent_config
from .....main.aideas.action.action_result_set import ActionResultSet
from .....main.aideas.agent.agent_names import AgentNames
from .....main.aideas.agent.translation.translation_agent import TranslationAgent

logging.config.dictConfig(get_logging_config())


class TranslationAgentIT(unittest.TestCase):
    # def test_translate_all(self):
    #     filename_in = "resources/subtitles.vtt"
    #     target_langs = ["ar", "de", "zh", "zh-TW"]
    #     TranslationAgent().translate_all(filename_in, target_langs)

    def test_run(self):
        agent_name: str = AgentNames.TRANSLATION
        config = load_agent_config(agent_name)
        print(f'Loaded app config: {config}')
        agent = TranslationAgent.of_config(config)
        inputs = TestAgentInputs().get(agent_name)
        print(f'Will run agent with inputs: {inputs}')
        result_set: ActionResultSet = agent.run(inputs)
        print(f'Completed. Results:\n{result_set.pretty_str()}')

        # Delete all saved translated files
        _delete_saved_files(result_set)


def _delete_saved_files(result_set: ActionResultSet):
    # Delete all saved translated files
    for target_d in result_set.keys():
        result_list = result_set.get(target_d)
        for result in result_list:
            file = result.get_result()
            if file is None:
                continue
            try:
                os.remove(file)
                print(f'Successfully removed file: {file}')
            except Exception as ex:
                print(f'Failed to remove file: {file}. {str(ex)}')


if __name__ == '__main__':
    unittest.main()
