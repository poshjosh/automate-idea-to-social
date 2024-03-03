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
                  stages_config: dict[str, any],
                  stage_name: Name,
                  run_context: RunContext) -> ElementResultSet:
        result_set = super().run_stage(stages_config, stage_name, run_context)
        delete_saved_files(result_set)
        return result_set
