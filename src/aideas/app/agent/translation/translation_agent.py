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
from ...config import Name, RunArg
from ...env import Env, get_app_language
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
        input_dir = run_context.get_arg(RunArg.INPUT_DIR)
        src_files = [f for f in glob.glob(f'{input_dir}/*.{file_type}')]

        if len(src_files) == 0:
            logger.warning(f'No translation files found in: {input_dir}')
            return run_context.get_element_results(self.get_name(), stage.id)

        target_languages_str: str = run_context.get_env(Env.TRANSLATION_OUTPUT_LANGUAGES)
        target_language_codes: [str] = target_languages_str.split(',')
        logger.debug(f'Output languages: {target_language_codes}, '
                     f'files: {len(src_files)}, dir: {input_dir}')

        for src_file in src_files:
            self.__do_translate_subtitles(stage.id, src_file, target_language_codes, run_context)

        return run_context.get_element_results(self.get_name(), stage.id)

    def __do_translate_subtitles(self,
                                 stage_id: str,
                                 filepath_in: str,
                                 output_language_codes: [str],
                                 run_context: RunContext) -> ElementResultSet:

        video_content_file = run_context.get_env(RunArg.VIDEO_CONTENT_FILE)
        src_dir = os.path.dirname(filepath_in)
        subtitles_dir_name = "subtitles"
        target_dirs = [
            os.path.join(src_dir, subtitles_dir_name),
            os.path.join(self.get_results_dir(), subtitles_dir_name),
            os.path.join(os.path.dirname(video_content_file), subtitles_dir_name)]

        for target_dir in target_dirs:
            self.__copy_to_dir(filepath_in, target_dir)

        for lang in output_language_codes:

            filepath_out = _add_language_code_to_path(filepath_in, lang)
            filename_out = os.path.basename(filepath_out)
            filepaths_out = [filepath_out]
            for target_dir in target_dirs:
                filepaths_out.append(os.path.join(target_dir, filename_out))

            result: ActionResult = self.__translate_subtitle(
                stage_id, filepath_in, filepaths_out, lang)

            run_context.add_action_result(AgentName.TRANSLATION, stage_id, result)

        return run_context.get_element_results(self.get_name(), stage_id)

    @staticmethod
    def __copy_to_dir(src: str, tgt_dir):
        if not os.path.exists(tgt_dir):
            os.makedirs(tgt_dir)
            logger.debug(f'Created dir: {tgt_dir}')
        shutil.copy2(src, os.path.join(tgt_dir, os.path.basename(src)))

    def __translate_subtitle(self,
                             stage_id: str,
                             filepath_in: str,
                             filepaths_out: [str],
                             output_language_code: str) -> ActionResult:
        args = [filepath_in]
        args.extend(filepaths_out)
        args.append(output_language_code)
        action = Action.of_generic(
            AgentName.TRANSLATION,
            stage_id,
            args)
        try:
            self.__do_translate_subtitle(filepath_in, filepaths_out, output_language_code)
            return ActionResult(action, True, filepaths_out)
        except Exception as ex:
            logger.exception(ex)
            return ActionResult(action, False)

    def __do_translate_subtitle(self,
                                filepath_in: str,
                                filepaths_out: [str],
                                output_language_code: str):

        subtitles_list = subtitle_read(filepath_in)
        grouped_list = grouping_subtitle(subtitles_list)

        self.__print_subtitles_if_verbose(grouped_list)

        q = (c.text for c in grouped_list)

        translated_result = self.__translator.translate(q, self.__from_lang, output_language_code)

        for group_capt, translated_row in zip(grouped_list, translated_result):
            group_capt.text = translated_row

        self.__print_subtitles_if_verbose(grouped_list)

        for filepath_out in filepaths_out:
            subtitle_save(filepath_out, grouped_list)
            logger.debug(f'{output_language_code} subtitles saved to: '
                         f'{filepath_out}, from: {filepath_in}')

    def __print_subtitles_if_verbose(self, subtitles_list: list[webvtt.Caption], title: str = ""):
        if self.__verbose is not True:
            return
        output: str = title
        for i in subtitles_list:
            output += f'\n{i}'
        logger.debug(output)


def _add_language_code_to_path(filename: str, target_language_code: str):
    parts: [str] = filename.rsplit('.', 1)
    if len(parts) < 2:
        return filename + "." + target_language_code
    else:
        return parts[0] + "." + target_language_code + "." + parts[1]
