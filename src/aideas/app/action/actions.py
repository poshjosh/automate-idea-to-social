import logging
import os.path
import shutil
import webvtt

from enum import Enum
from typing import Union, Any

from content_publisher.app.app import App
from content_publisher.app.content_publisher import Content, PostResult, SocialPlatformType
from content_publisher.app.run_arg import RunArg as PublisherArg
from pyu.io.file import read_content, write_content

from ..action.action import Action
from ..action.action_result import ActionResult
from ..agent.translation.subtitles import grouping_subtitle, subtitle_read, subtitle_save
from ..agent.translation.translator import Translator
from ..config import RunArg
from ..env import Env, require_env_value
from ..run_context import RunContext
from ..text import list_from_object

logger = logging.getLogger(__name__)


def _detect_language_code_from_filename(filename: str) -> Union[str, None]:
    file_ext = require_env_value(Env.SUBTITLES_FILE_EXTENSION)
    import re
    match = re.search(r'\.(\w{2})\.' + re.escape(file_ext), filename)
    if match:
        return match.group(1)
    raise ValueError(f"File name does not include valid language code as suffix: {filename}")


def _copy_to_dir(src: str, tgt_dir):
    if not os.path.exists(tgt_dir):
        os.makedirs(tgt_dir)
        logger.debug(f'Created dir: {tgt_dir}')
    tgt = os.path.join(tgt_dir, os.path.basename(src))
    logger.debug(f"Copied to: {tgt} from: {src}")
    shutil.copy2(src, tgt)


class PublishContentAction:
    @staticmethod
    def get_supported_platforms() -> list[str]:
        return [SocialPlatformType.YOUTUBE.value, SocialPlatformType.X.value,
                SocialPlatformType.FACEBOOK.value, SocialPlatformType.REDDIT.value]

    def execute(self, run_context: RunContext, action: Action) -> ActionResult:
        args: dict[PublisherArg, Any] = PublisherArg.of_list({}, action.get_args())
        platforms = self._get_value(run_context, args, PublisherArg.PLATFORMS)
        if not platforms:
            return ActionResult.failure(action, "No platforms specified")
        platforms: list[str] = list_from_object(platforms)

        content: Content = self.__to_content(run_context, args)
        logger.debug(f"Publishing to platforms: {platforms}, content:\n{content}")

        result: dict[str, Any] = App().publish_content(platforms, content)

        def is_success(r: Any) -> bool:
            if isinstance(r, PostResult):
                return r.success
            elif isinstance(r, bool):
                return r
            raise ValueError(f"Unknown result type: {type(r)}")

        success = len([e for e in result.values() if not is_success(e)]) == 0

        return ActionResult(action, success, result)

    def __to_content(self, run_context: RunContext, args: dict[PublisherArg, Any]) -> Content:
        dir_path = self._get_value(run_context, args, PublisherArg.DIR)
        text_title = self._get_value(run_context, args, PublisherArg.TEXT_TITLE)
        media_orientation = self._get_value(run_context, args, PublisherArg.MEDIA_ORIENTATION)
        language_code = self._get_value(run_context, args, PublisherArg.LANGUAGE_CODE)
        language_code = language_code if language_code else "en"
        tags = self._get_value(run_context, args, PublisherArg.TAGS)

        if dir_path:
            tags: Union[list[str], bool] = list_from_object(tags) if tags else True
            return Content.of_dir(dir_path, text_title, media_orientation, language_code, tags)
        else:

            def media_file_arg(media_type: str) -> RunArg:
                return RunArg(f"{media_type}-file-{media_orientation}")

            description: str = self._get_value(run_context, args, RunArg.TEXT_CONTENT)
            video_file: Union[str, None] = self._get_value(run_context, args, media_file_arg("video"))
            image_file: Union[str, None] = self._get_value(run_context, args, media_file_arg("image"))
            subtitle_files = self._get_value(run_context, args, f'{RunArg.SUBTITLES_FILE.value}s')
            subtitle_files_by_lang: Union[dict[str, str], None] = PublishContentAction.__subtitles_files_by_lang(subtitle_files)
            logger.debug(f"Subtitle files by lang: {subtitle_files_by_lang}")

            if not tags:
                # TODO - determine max length based on platform
                #  currently we use 500, which applies to youtube and subtract some margin
                tags = PublishContentAction.__extract_hashtags_from_text(description, 450)
                logger.debug(f"Extracted hashtags from text: {tags}")

            return Content(description, video_file, image_file, text_title,
                           language_code, tags, subtitle_files_by_lang)

    # TODO - Remove this method and use Content.extract_hashtags_from_text(str, int) instead.
    @staticmethod
    def __extract_hashtags_from_text(text: str, max_tags_length: int) -> list[str]:
        import re
        hashtags = re.findall(r'#\w+', text)
        all_tags = [tag.lstrip('#') for tag in hashtags]
        total_len = 0
        result = []
        for tag in all_tags:
            tag_len = len(tag) + (1 if result else 0) # add one for comma
            if total_len + tag_len > max_tags_length:
                break
            result.append(tag)
            total_len += tag_len
        return result

    @staticmethod
    def __subtitles_files_by_lang(subtitle_files: Any) -> dict[str, str]:

        subtitle_files_by_lang: Union[dict[str, str], None] = {}

        if subtitle_files:
            subtitle_files: list[str] = list_from_object(subtitle_files)
            for subtitle_file in subtitle_files:
                lang_code = _detect_language_code_from_filename(subtitle_file)
                if lang_code:
                    subtitle_files_by_lang[lang_code] = subtitle_file
        return subtitle_files_by_lang

    @staticmethod
    def _get_value(run_context: RunContext, args: dict[PublisherArg, Any], key: Union[str, Enum]) -> Any:
        key_str = key.value if isinstance(key, Enum) else key
        return run_context.get_arg(key, args.get(key, run_context.get(key_str, None)))


class TranslateAction:
    @classmethod
    def of_config(cls, config: dict[str, Any]) -> 'TranslateAction':
        return cls(Translator.of_config(config), config.get("verbose", False))
    
    def __init__(self, translator: Translator, verbose: bool = False):
        self.__translator = translator
        self.__verbose = verbose

    def get_dir_name(self)  -> str:
        return "translations"

    def execute(self, _, action: Action) -> ActionResult:

        args = action.get_args_as_str_list()

        filepath_in: str = args[0]
        from_lang: str = args[1]
        output_language_codes: list[str] = list_from_object(args[2])

        if from_lang in output_language_codes:
            output_language_codes.remove(from_lang)

        for target_dir in action.get_output_dirs(self.get_dir_name()):
            _copy_to_dir(filepath_in, target_dir)

        result = []

        for to_lang in output_language_codes:

            if not to_lang:
                continue

            output_filepaths = self.translate(action, from_lang, to_lang)
            if output_filepaths:
                result.append(output_filepaths[0])

        return ActionResult.success(action, result)

    def translate(self, action: Action, input_language_code: str, output_language_code: str) -> list[str]:
        try:
            filepath_in = action.get_first_arg()
            filepath_out = self._output_file_path(filepath_in, input_language_code, output_language_code)

            filename = os.path.basename(filepath_out)

            filepaths_out = [os.path.join(e, filename) for e in action.get_output_dirs(self.get_dir_name())]

            self._translate(filepath_in, filepaths_out, input_language_code, output_language_code)

            return filepaths_out

        except Exception as ex:
            logger.exception(ex)
            return []

    def _output_file_path(self, filepath_in, input_language_code, output_language_code) -> str:
        return self.__translator.translate_file_path(filepath_in, input_language_code, output_language_code)

    def _translate(self, filepath_in: str, filepaths_out: list[str],
                   input_language_code: str, output_language_code: str):

        input_text:str = read_content(filepath_in).strip()

        self.__print_if_verbose(" Input", input_text)

        result_text = self.__translator.translate(input_text, input_language_code, output_language_code)

        self.__print_if_verbose(" Result", result_text)

        for filepath_out in filepaths_out:
            write_content(result_text, filepath_out)
            logger.debug(f'{output_language_code} translations saved to: '
                         f'{filepath_out}, from: {filepath_in}')

    def __print_if_verbose(self, key: str, text: str):
        if not self.__verbose:
            return
        logger.debug(f"{key}\n{text}")

    def is_verbose(self) -> bool:
        return self.__verbose

    def get_translator(self) -> Translator:
        return self.__translator

class TranslateSubtitlesAction(TranslateAction):
    def __init__(self, translator: Translator, verbose: bool = False):
        super().__init__(translator, verbose)

    def get_dir_name(self)  -> str:
        return "subtitles"

    def _output_file_path(self, filepath_in, input_language_code, output_language_code) -> str:
        parts: list[str] = filepath_in.rsplit('.', 1)
        if len(parts) < 2:
            return filepath_in + "." + output_language_code
        else:
            return parts[0] + "." + output_language_code + "." + parts[1]


    def _translate(self, filepath_in: str, filepaths_out: list[str],
                   input_language_code: str, output_language_code: str):

        subtitles_list = subtitle_read(filepath_in)
        grouped_list = grouping_subtitle(subtitles_list)

        self.__print_subtitles_if_verbose(grouped_list)

        q = (c.text for c in grouped_list)

        translated_result = self.get_translator().translate(q, input_language_code, output_language_code)

        for group_capt, translated_row in zip(grouped_list, translated_result):
            group_capt.text = translated_row

        self.__print_subtitles_if_verbose(grouped_list)

        for filepath_out in filepaths_out:
            subtitle_save(filepath_out, grouped_list)
            logger.debug(f'{output_language_code} subtitles saved to: '
                         f'{filepath_out}, from: {filepath_in}')

    def __print_subtitles_if_verbose(self, subtitles_list: list[webvtt.Caption], title: str = ""):
        if self.is_verbose():
            return
        output: str = title
        for i in subtitles_list:
            output += f'\n{i}'
        logger.debug(output)



