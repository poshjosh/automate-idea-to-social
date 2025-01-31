from test.app.test_functions import delete_saved_files
from test.app.agent.translation.test_translator import TestTranslator
from aideas.app.agent.translation.subtitles_translation_agent import SubtitlesTranslationAgent
from aideas.app.config import Name
from aideas.app.result.result_set import ElementResultSet
from aideas.app.run_context import RunContext


class TestSubtitlesTranslationAgent(SubtitlesTranslationAgent):
    @staticmethod
    def create_translator(agent_config: dict[str, any]) -> TestTranslator:
        return TestTranslator.of_config(agent_config)

    def run_stage(self,
                  run_context: RunContext,
                  stage_name: Name) -> ElementResultSet:
        result_set: ElementResultSet = ElementResultSet.none()
        try:
            result_set = super().run_stage(run_context, stage_name)
        finally:
            delete_saved_files(result_set)
        return result_set
