import logging
import os.path
import shutil

import webvtt

from .subtitles import grouping_subtitle, subtitle_read, subtitle_save
from .translator import Translator
from ..automator_agent import AutomatorAgent, Automator
from ...action.action import Action
from ...action.action_result import ActionResult
from ...config import Name, RunArg
from ...result.result_set import ElementResultSet
from ...run_context import RunContext

logger = logging.getLogger(__name__)

DIR_NAME = "subtitles"
DEFAULT_STAGE = Name.of("translate-subtitles")
DEFAULT_STAGE_ITEM = DEFAULT_STAGE
DEFAULT_ACTION = "translate_subtitles"


class SubtitlesTranslationAutomatorAgent(AutomatorAgent):
    __verbose = False

    @staticmethod
    def create_translator(agent_config: dict[str, any]) -> Translator:
        return Translator.of_config(agent_config)

    def __init__(self,
                 name: str,
                 agent_config: dict[str, any],
                 dependencies: dict[str, 'AutomatorAgent'] = None,
                 automator: Automator = None,
                 interval_seconds: int = 0):
        super().__init__(name, agent_config, dependencies, automator, interval_seconds)
        self.__translator = self.__class__.create_translator(agent_config)

    def run_stage(self, run_context: RunContext, stage: Name) -> ElementResultSet:
        if stage == DEFAULT_STAGE:
            return self.__translate_subtitles(run_context)
        else:
            return super().run_stage(run_context, stage)

    def __translate_subtitles(self, run_context: RunContext) -> ElementResultSet:
        stage_id = DEFAULT_STAGE.id
        stage_item_id = DEFAULT_STAGE_ITEM.id

        src_file = run_context.get_arg(RunArg.SUBTITLES_FILE)
        if not src_file:
            logger.warning(f'File not found: {src_file}')
            return run_context.get_element_results(self.get_name(), stage_id)

        logger.debug(f'Source file: {src_file}')

        from_lang: str = run_context.get_app_language()
        to_langs_str = run_context.get_language_codes_str()
        logger.debug(f'Translate from: {from_lang}, to: {to_langs_str}')

        action = Action.of(
            self.get_name(), stage_id, stage_item_id,
            f"{DEFAULT_ACTION} \"{src_file}\" {from_lang} {to_langs_str}",
            run_context)

        self.__do_translate_subtitles(run_context, action)

        return run_context.get_element_results(self.get_name(), stage_id)

    def __do_translate_subtitles(self, run_context: RunContext, action: Action) -> ElementResultSet:

        args = action.get_args_as_str_list()

        filepath_in: str = args[0]
        from_lang: str =  args[1]
        output_language_codes: [str] = args[2].split(',')

        for target_dir in action.get_output_dirs(DIR_NAME):
            self.__copy_to_dir(filepath_in, target_dir)

        for to_lang in output_language_codes:

            result: ActionResult = self.__translate_subtitle(action, from_lang, to_lang)

            run_context.add_action_result(result)

        return run_context.get_element_results(self.get_name(), action.get_stage_id())

    @staticmethod
    def __copy_to_dir(src: str, tgt_dir):
        if not os.path.exists(tgt_dir):
            os.makedirs(tgt_dir)
            logger.debug(f'Created dir: {tgt_dir}')
        tgt = os.path.join(tgt_dir, os.path.basename(src))
        logger.debug(f"Copied to: {tgt} from: {src}")
        shutil.copy2(src, tgt)

    def __translate_subtitle(self,
                             action: Action,
                             input_language_code: str,
                             output_language_code: str) -> ActionResult:

        try:
            filepath_in = action.get_first_arg()
            filepath_out = _add_language_code_to_path(filepath_in, output_language_code)
            filename = os.path.basename(filepath_out)

            filepaths_out = [os.path.join(e, filename) for e in action.get_output_dirs(DIR_NAME)]

            self.__do_translate_subtitle(filepath_in, filepaths_out, input_language_code, output_language_code)

            return ActionResult(action, True, filepaths_out)

        except Exception as ex:
            logger.exception(ex)
            return ActionResult(action, False)

    def __do_translate_subtitle(self,
                                filepath_in: str,
                                filepaths_out: [str],
                                input_language_code: str,
                                output_language_code: str):

        subtitles_list = subtitle_read(filepath_in)
        grouped_list = grouping_subtitle(subtitles_list)

        self.__print_subtitles_if_verbose(grouped_list)

        q = (c.text for c in grouped_list)

        translated_result = self.__translator.translate(q, input_language_code, output_language_code)

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
