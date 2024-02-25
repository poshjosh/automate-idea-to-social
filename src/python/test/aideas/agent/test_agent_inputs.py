import os
from typing import AnyStr

from ....main.aideas.agent.agent_inputs import AgentInputs
from ....main.aideas.agent.agent_names import AgentNames
from ....main.aideas.env_names import PictoryEnvNames, TranslationEnvNames


class TestAgentInputs(AgentInputs):
    def __init__(self):
        resources_dir = 'python/test/resources'
        pictory_resources_dir = resources_dir + '/' + AgentNames.PICTORY
        os.environ[PictoryEnvNames.USER_NAME] = 'test-user-name'
        os.environ[PictoryEnvNames.USER_PASS] = 'test-user-pass'
        os.environ[PictoryEnvNames.INPUT_FILE] = 'test-input-file'
        os.environ[PictoryEnvNames.OUTPUT_DIR] = pictory_resources_dir
        os.environ[TranslationEnvNames.INPUT_DIR] = pictory_resources_dir
        os.environ[TranslationEnvNames.OUTPUT_LANGUAGES] = "ar,de,zh"

    def read_file(self, file_path: str) -> AnyStr:
        return """
            This is some test file content.
            The content is spread over multiple lines.
            This is the third line.
        """
