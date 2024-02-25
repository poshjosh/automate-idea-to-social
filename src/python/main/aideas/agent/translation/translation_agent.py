import glob
import logging
import os

import webvtt

from .subtitles import grouping_subtitle, subtitle_read, subtitle_save, mix_subtitles
from .translator import translate_text
from ..agent import Agent
from ...action.action import Action
from ...action.action_result import ActionResult
from ...action.action_result_set import ActionResultSet
from ...env_names import TranslationEnvNames


logger = logging.getLogger(__name__)


class TranslationAgent(Agent):
    __debug = False

    @staticmethod
    def of_config(config: dict[str, any]) -> 'TranslationAgent':
        user_agent = config.get('net', {}).get('user-agent', '')
        return TranslationAgent(user_agent)

    def __init__(self, browser_user_agent: str = ""):
        self.__browser_user_agent = browser_user_agent

    def run(self, run_config: dict[str, any]) -> ActionResultSet:
        dir_path: str = run_config[TranslationEnvNames.INPUT_DIR]
        target_languages_str: str = run_config[TranslationEnvNames.OUTPUT_LANGUAGES]
        target_language_codes: [str] = target_languages_str.split(',')
        filepaths = [f for f in glob.glob(f"{dir_path}/*.vtt")]
        logger.debug(f"Output languages: {target_language_codes}, "
                     f"dir: {dir_path}, files: {filepaths}")
        result_set = ActionResultSet()
        for filepath in filepaths:
            result_set.add_all(self.translate_all(filepath, target_language_codes))
        return result_set.close()

    def translate_all(self, filename_in: str, output_language_codes: [str]) -> ActionResultSet:
        result_set = ActionResultSet()
        for output_language_code in output_language_codes:
            file_name_out = _compose_file_name(filename_in, output_language_code)
            result_set.add(self.translate(filename_in, file_name_out, output_language_code))
        return result_set.close()

    def translate(self,
                  filename_in: str,
                  filename_out: str,
                  output_language_code: str) -> ActionResult:
        action = Action(
            f"translate-subtitles-{os.path.basename(filename_out)}",
            "translate_subtitles",
            [filename_in, filename_out, output_language_code])
        try:
            self.__translate(filename_in, filename_out, output_language_code)
            return ActionResult(action, True, filename_out)
        except Exception as ex:
            logger.error(f"{str(ex)}")
            return ActionResult(action, False)

    def __translate(self, filename_in: str, filename_out: str, target_language_code: str):

        subtitles_list = subtitle_read(filename_in)
        grouped_list = grouping_subtitle(subtitles_list)

        self.__print_subtitles(grouped_list)

        q = (c.text for c in grouped_list)
        translated_result = translate_text(
            target_language_code,
            q,
            browser_user_agent=self.__browser_user_agent)
        for group_capt, translated_row in zip(grouped_list, translated_result):
            group_capt.text = translated_row

        # Will be printed only if debug is true
        self.__print_subtitles(grouped_list)

        self.save_subtitles(filename_out, grouped_list)

        logger.debug(f"{target_language_code} translated to: {filename_out}, from: {filename_in}")

    def mix_subtitles(self,
                      subtitles_list_1: list[webvtt.Caption],
                      subtitles_list_2: list[webvtt.Caption]) -> list[webvtt.Caption]:
        dual_lang_subtitles = mix_subtitles(subtitles_list_1, subtitles_list_2)
        self.__print_subtitles(dual_lang_subtitles)
        return dual_lang_subtitles

    def save_subtitles(self, filename: str, subtitles_list: list[webvtt.Caption]):
        subtitle_save(filename, subtitles_list)
        logger.debug("Saved subtitles to: " + filename)

    def __print_subtitles(self, subtitles_list: list[webvtt.Caption], title: str = ""):
        if self.__debug is not True:
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
