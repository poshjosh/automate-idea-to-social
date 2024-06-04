import glob
import logging
import os.path
import shutil

import webvtt

from .subtitles import grouping_subtitle, subtitle_read, subtitle_save
from .translator import Translator
from ..agent import Agent, Automator
from ...agent.agent_name import AgentName
from ...action.action import Action
from ...action.action_result import ActionResult
from ...config import Name
from ...env import Env, get_content_file_path, get_app_language
from ...result.result_set import ElementResultSet
from ...run_context import RunContext

logger = logging.getLogger(__name__)

DEFAULT_STAGE = Name.of("translate-subtitles")


class TranslationAgent(Agent):
    __verbose = False

    @staticmethod
    def create_translator(agent_config: dict[str, any]) -> Translator:
        return Translator.of_config(agent_config)

    def __init__(self,
                 name: str,
                 agent_config: dict[str, any],
                 dependencies: dict[str, 'Agent'] = None,
                 automator: Automator = None,
                 interval_seconds: int = 0):
        super().__init__(name, agent_config, dependencies, automator, interval_seconds)
        self.__translator = self.__class__.create_translator(agent_config)
        self.__from_lang = get_app_language(False)

    def run_stage(self, run_context: RunContext, stage: Name) -> ElementResultSet:
        if stage == DEFAULT_STAGE:
            return self.__translate_subtitles(run_context)
        else:
            return super().run_stage(run_context, stage)

    def __translate_subtitles(self, run_context: RunContext) -> ElementResultSet:
        stage = DEFAULT_STAGE
        file_type = run_context.get_env(Env.TRANSLATION_FILE_EXTENSION)
        pictory_output_dir: str = self.get_output_dir(AgentName.PICTORY)
        src_files = [f for f in glob.glob(f'{pictory_output_dir}/*.{file_type}')]

        if len(src_files) == 0:
            logger.warning(f'No translation files found in: {pictory_output_dir}')
            return run_context.get_element_results(self.get_name(), stage.id)

        target_languages_str: str = run_context.get_env(Env.TRANSLATION_OUTPUT_LANGUAGES)
        target_language_codes: [str] = target_languages_str.split(',')
        logger.debug(f'Output languages: {target_language_codes}, '
                     f'files: {len(src_files)}, dir: {pictory_output_dir}')

        results_dir: str = self.get_results_dir()
        for src_file in src_files:
            tgt_file = os.path.join(results_dir, os.path.basename(src_file))
            shutil.copy2(src_file, tgt_file)
            logger.debug(f"Copied to: {tgt_file} from: {src_file}")
            self.__translate_all(stage.id, tgt_file, target_language_codes, run_context)

        return run_context.get_element_results(self.get_name(), stage.id)

    def __translate_all(self,
                        stage_id: str,
                        filename_in: str,
                        output_language_codes: [str],
                        run_context: RunContext) -> ElementResultSet:

        self.__copy_to_content_dir(filename_in)

        for output_language_code in output_language_codes:
            filename_out = _compose_file_name(filename_in, output_language_code)
            result: ActionResult = self.__translate(
                stage_id, filename_in, filename_out, output_language_code)

            self.__copy_to_content_dir(filename_out)

            run_context.add_action_result(AgentName.TRANSLATION, stage_id, result)

        return run_context.get_element_results(self.get_name(), stage_id)

    @staticmethod
    def __copy_to_content_dir(src: str):
        dir_path = get_content_file_path("subtitles")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.debug(f'Created dir: {dir_path}')
        shutil.copy2(src, os.path.join(dir_path, os.path.basename(src)))

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

    def __print_subtitles_if_verbose(self, subtitles_list: list[webvtt.Caption], title: str = ""):
        if self.__verbose is not True:
            return
        output: str = title
        for i in subtitles_list:
            output += f'\n{i}'
        logger.debug(output)


def _compose_file_name(filename: str, target_language_code: str):
    parts: [str] = filename.rsplit('.', 1)
    if len(parts) < 2:
        return filename + "." + target_language_code
    else:
        return parts[0] + "." + target_language_code + "." + parts[1]
