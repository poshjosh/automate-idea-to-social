from ...test_functions import delete_saved_files
from .test_translator import TestTranslator
from .....main.aideas.agent.translation.translation_agent import TranslationAgent
from .....main.aideas.config.name import Name
from .....main.aideas.result.element_result_set import ElementResultSet
from .....main.aideas.run_context import RunContext


class TestTranslationAgent(TranslationAgent):
    @staticmethod
    def of_config(agent_config: dict[str, any]) -> TranslationAgent:
        return TestTranslationAgent(agent_config, TestTranslator.of_config(agent_config))

    def run_stage(self,
                  run_context: RunContext,
                  stage_name: Name) -> ElementResultSet:
        result_set: ElementResultSet = ElementResultSet.none()
        try:
            result_set = super().run_stage(run_context, stage_name)
        finally:
            delete_saved_files(result_set)
        return result_set
