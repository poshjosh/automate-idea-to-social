import logging
import os.path
import shutil

from .translator import Translator
from ..agent import Agent, Automator
from ...action.action import Action
from ...action.action_result import ActionResult
from ...config import Name, RunArg
from ...env import Env
from ...result.result_set import ElementResultSet
from ...run_context import RunContext

from pyu.io.file import read_content, write_content

logger = logging.getLogger(__name__)

DIR_NAME = "translations"
DEFAULT_STAGE = Name.of("translate")
DEFAULT_STAGE_ITEM = DEFAULT_STAGE
DEFAULT_ACTION = "translate"


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

    def run_stage(self, run_context: RunContext, stage: Name) -> ElementResultSet:
        if stage == DEFAULT_STAGE:
            return self.__run_default_stage(run_context)
        else:
            return super().run_stage(run_context, stage)

    def __run_default_stage(self, run_context: RunContext) -> ElementResultSet:
        stage_id = DEFAULT_STAGE.id
        stage_item_id = DEFAULT_STAGE_ITEM.id

        src_file = run_context.get_arg(RunArg.TEXT_FILE)
        if not src_file:
            logger.warning(f'File not found: {src_file}')
            return run_context.get_element_results(self.get_name(), stage_id)

        logger.debug(f'Source file: {src_file}')

        from_lang: str = run_context.get_app_language()
        to_langs_str: str = run_context.get_arg(RunArg.LANGUAGE_CODES,
                                                        run_context.get_env(Env.TRANSLATION_OUTPUT_LANGUAGE_CODES))
        logger.debug(f'Translate from: {from_lang}, to: {to_langs_str}')

        action = Action.of(
            self.get_name(), stage_id, stage_item_id,
            f"{DEFAULT_ACTION} \"{src_file}\" {from_lang} {to_langs_str}",
            run_context)

        self.__do_run_default_stage(run_context, action)

        return run_context.get_element_results(self.get_name(), stage_id)

    def __do_run_default_stage(self, run_context: RunContext, action: Action) -> ElementResultSet:

        args = action.get_args_as_str_list()

        filepath_in: str = args[0]
        from_lang: str = args[1]
        output_language_codes: [str] = args[2].split(',')

        for target_dir in action.get_output_dirs(DIR_NAME):
            self.__copy_to_dir(filepath_in, target_dir)

        for to_lang in output_language_codes:

            if not to_lang:
                continue

            result: ActionResult = self.__translate(action, from_lang, to_lang)

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

    def __translate(self, action: Action, input_language_code: str, output_language_code: str) -> ActionResult:
        try:
            filepath_in = action.get_first_arg()
            filepath_out = self.__translator.translate_file_path(filepath_in, input_language_code, output_language_code)

            filename = os.path.basename(filepath_out)

            filepaths_out = [os.path.join(e, filename) for e in action.get_output_dirs(DIR_NAME)]

            self.__do_translate(filepath_in, filepaths_out, input_language_code, output_language_code)

            return ActionResult(action, True, filepaths_out)

        except Exception as ex:
            logger.exception(ex)
            return ActionResult(action, False)

    def __do_translate(self, filepath_in: str, filepaths_out: [str], input_language_code: str, output_language_code: str):

        input_text:str = read_content(filepath_in).strip()

        self.__print_if_verbose(input_text)

        result_text = self.__translator.translate(input_text, input_language_code, output_language_code)

        self.__print_if_verbose(result_text)

        for filepath_out in filepaths_out:
            write_content(result_text, filepath_out)
            logger.debug(f'{output_language_code} translations saved to: '
                         f'{filepath_out}, from: {filepath_in}')

    def __print_if_verbose(self, text: str):
        if self.__verbose is not True:
            return
        logger.debug(text)