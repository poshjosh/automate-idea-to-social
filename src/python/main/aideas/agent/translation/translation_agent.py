import glob
import logging
import os.path
import shutil

import webvtt

from .subtitles import grouping_subtitle, subtitle_read, subtitle_save, mix_subtitles
from .translator import Translator
from ..agent import Agent
from ...agent.agent_name import AgentName
from ...action.action import Action
from ...action.action_result import ActionResult
from ...config import Name
from ...result.result_set import ElementResultSet
from ...env import Env
from ...run_context import RunContext


logger = logging.getLogger(__name__)


class TranslationAgent(Agent):
    __verbose = False

    @staticmethod
    def of_config(agent_config: dict[str, any]) -> 'TranslationAgent':
        return TranslationAgent(agent_config, Translator.of_config(agent_config))

    def __init__(self, agent_config: dict[str, any], translator: Translator):
        super().__init__(AgentName.TRANSLATION, agent_config)
        self.__from_lang = "en"
        self.__translator = translator

    def run_stage(self,
                  run_context: RunContext,
                  stage: Name) -> ElementResultSet:
        file_type = run_context.get_env(Env.TRANSLATION_FILE_EXTENSION)
        pictory_output_dir: str = self.get_output_dir(AgentName.PICTORY)
        src_files = [f for f in glob.glob(f'{pictory_output_dir}/*.{file_type}')]

        target_languages_str: str = run_context.get_env(Env.TRANSLATION_OUTPUT_LANGUAGES)
        target_language_codes: [str] = target_languages_str.split(',')
        logger.debug(f'Output languages: {target_language_codes}, '
                     f'files: {len(src_files)}, dir: {pictory_output_dir}')

        results_dir: str = self.get_results_dir()
        for src_file in src_files:
            tgt_file = os.path.join(results_dir, os.path.basename(src_file))
            shutil.copy2(src_file, tgt_file)
            logger.debug(f"Copied to: {tgt_file} from: {src_file}")
            self.__translate_all(
                stage.get_id(), tgt_file, target_language_codes, run_context)

        return run_context.get_element_results(self.get_name(), stage.get_id())

    def __translate_all(self,
                        stage_id: str,
                        filename_in: str,
                        output_language_codes: [str],
                        run_context: RunContext) -> ElementResultSet:
        for output_language_code in output_language_codes:
            file_name_out = _compose_file_name(filename_in, output_language_code)
            result: ActionResult = self.__translate(
                stage_id, filename_in, file_name_out, output_language_code)
            run_context.add_action_result(AgentName.TRANSLATION, stage_id, result)
        return run_context.get_element_results(self.get_name(), stage_id)

    def __translate(self,
                    stage_id: str,
                    filename_in: str,
                    filename_out: str,
                    output_language_code: str) -> ActionResult:
        action = Action.of_generic(
            AgentName.TRANSLATION,
            stage_id,
            [filename_in, filename_out, output_language_code])
        try:
            self.__do_translate(filename_in, filename_out, output_language_code)
            return ActionResult(action, True, filename_out)
        except Exception as ex:
            logger.exception(ex)
            return ActionResult(action, False)

    def __do_translate(self,
                       filename_in: str,
                       filename_out: str,
                       to_lang: str):

        subtitles_list = subtitle_read(filename_in)
        grouped_list = grouping_subtitle(subtitles_list)

        self.__print_subtitles_if_verbose(grouped_list)

        q = (c.text for c in grouped_list)

        translated_result = self.__translator.translate(q, self.__from_lang, to_lang)

        for group_capt, translated_row in zip(grouped_list, translated_result):
            group_capt.text = translated_row

        self.__print_subtitles_if_verbose(grouped_list)

        subtitle_save(filename_out, grouped_list)

        logger.debug(f'{to_lang} translated to: {filename_out}, from: {filename_in}')

    def __mix_subtitles(self,
                        subtitles_list_1: list[webvtt.Caption],
                        subtitles_list_2: list[webvtt.Caption]) -> list[webvtt.Caption]:
        dual_lang_subtitles = mix_subtitles(subtitles_list_1, subtitles_list_2)
        self.__print_subtitles_if_verbose(dual_lang_subtitles)
        return dual_lang_subtitles

    def __print_subtitles_if_verbose(self, subtitles_list: list[webvtt.Caption], title: str = ""):
        if self.__verbose is not True:
            return
        print(title)
        for i in subtitles_list:
            print(i)


def _compose_file_name(filename: str, target_language_code: str):
    parts: [str] = filename.rsplit('.', 1)
    if len(parts) < 2:
        return filename + "." + target_language_code
    else:
        return parts[0] + "." + target_language_code + "." + parts[1]
