import logging
import os
import shutil
import subprocess
import time
from enum import Enum, unique
from typing import Union, TypeVar

from pyu.io.file import read_content, write_content
from .action import Action
from .action_result import ActionResult
from ..config import parse_query
from ..run_context import RunContext

logger = logging.getLogger(__name__)

TARGET = TypeVar("TARGET", bound=Union[any, None])


class ActionError(Exception):
    pass


class BaseActionId(str, Enum):
    def __new__(cls, value, result_producing: bool = True):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.__result_producing = result_producing
        return obj

    def is_result_producing(self) -> bool:
        return self.__result_producing


@unique
class ActionId(BaseActionId):
    EVAL = 'eval'
    EXEC = 'exec'
    GET_FILE_CONTENT = 'get_file_content'
    GET_FILES = 'get_files'
    GET_FIRST_FILE = 'get_first_file'
    GET_NEWEST_FILE_IN_DIR = 'get_newest_file_in_dir'
    LOG = ('log', False)
    RUN_SUBPROCESS = 'run_subprocess'
    SAVE_FILE = 'save_file'
    SAVE_TEXT = 'save_text'
    SET_CONTEXT_VALUES = ('set_context_values', False)
    STARTS_WITH = 'starts_with'
    WAIT = ('wait', False)


DEFAULT_FILE_NAME = "result.txt"


class ActionHandler:
    __ALL_FILE_TYPES = '*'

    @staticmethod
    def noop() -> 'ActionHandler':
        return NOOP

    @staticmethod
    def to_action_id(action: str) -> BaseActionId:
        return ActionId(action)

    @staticmethod
    def throw_error(ex: Exception, action: Action):
        if isinstance(ex, ActionError):
            raise ex
        error_msg = f'Error while executing {action}'
        logger.error(error_msg, exc_info=ex)
        raise ActionError(error_msg)

    def with_timeout(self, timeout: float) -> 'ActionHandler':
        # TODO Implement a timeout for this action handler
        return self

    def execute_on(
            self, run_context: RunContext, action: Action, target: TARGET = None) -> ActionResult:
        return self.execute(run_context, action)

    def execute(self, run_context: RunContext, action: Action) -> ActionResult:
        try:
            key = action.get_name_without_negation() if action.is_negation() else action.get_name()
            result = self._execute(run_context, action, key)
            if action.is_negation():
                result = result.flip()
            return result
        except Exception as ex:
            self.throw_error(ex, action)

    def _execute(self, run_context: RunContext, action: Action, key: str) -> ActionResult:
        if action == Action.none():
            result = ActionResult.none()
        elif key == ActionId.EVAL.value:
            result: ActionResult = self.eval(action)
        elif key == ActionId.EXEC.value:
            result: ActionResult = self.exec(action)
        elif key == ActionId.GET_FILE_CONTENT.value:
            result: ActionResult = self.get_file_content(action)
        elif key == ActionId.GET_FILES.value:
            result: ActionResult = self.get_files(action)
        elif key == ActionId.GET_FIRST_FILE.value:
            result: ActionResult = self.get_first_file(action)
        elif key == ActionId.GET_NEWEST_FILE_IN_DIR.value:
            result: ActionResult = self.get_newest_file_in_dir(action)
        elif key == ActionId.LOG.value:
            result: ActionResult = self.log(action)
        elif key == ActionId.RUN_SUBPROCESS.value:
            result: ActionResult = self.run_subprocess(action)
        elif key == ActionId.SAVE_FILE.value:
            result: ActionResult = self.save_file(action)
        elif key == ActionId.SAVE_TEXT.value:
            result: ActionResult = self.save_text(action)
        elif key == ActionId.SET_CONTEXT_VALUES.value:
            result: ActionResult = self.set_context_values(run_context, action)
        elif key == ActionId.STARTS_WITH.value:
            result: ActionResult = self.starts_with(action)
        elif key == ActionId.WAIT.value:
            result: ActionResult = self.wait(action)
        else:
            raise ValueError(f'Unsupported: {action}')
        logger.debug(f'{result}')
        return result

    @staticmethod
    def wait(action: Action) -> ActionResult:
        arg: str = action.require_first_arg_as_str()
        timeout: float = float(arg)
        if timeout < 0:
            raise ValueError(f'Invalid wait timeout: {timeout}')
        logger.debug(f'Waiting for {timeout} seconds')
        if timeout == 0:
            return ActionResult(action, True)
        time.sleep(timeout)
        return ActionResult(action, True)

    @staticmethod
    def get_newest_file_in_dir(action: Action) -> ActionResult:
        args: [str] = action.get_args_as_str_list()
        dir_path: str = action.require_first_arg_as_str()
        file_type: str = args[1]
        timeout: int = 30 if len(args) < 3 else int(args[2])
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            most_recent_file = ActionHandler.__get_newest_file_in_dir(dir_path, file_type, None)
            if most_recent_file is not None:
                return ActionResult(action, True, most_recent_file)
            time.sleep(1)
        return ActionResult(action, False)

    @staticmethod
    def log(action: Action) -> ActionResult:
        arg_list: [] = action.get_args_as_str_list()
        logger.log(logging.getLevelName(arg_list[0]), ' '.join(arg_list[1:]))
        return ActionResult(action, True)

    @staticmethod
    def run_subprocess(action: Action) -> ActionResult:
        arg_list: [] = action.get_args_as_str_list()
        result = subprocess.run(arg_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return ActionResult(action, True, result.stdout)

    @staticmethod
    def save_file(action: Action) -> ActionResult:
        args: [str] = action.get_args_as_str_list()
        src_file = args[0]
        tgt_filename = os.path.basename(src_file) if len(args) < 2 else args[1]
        tgt_dirs = action.get_output_dirs()
        if len(args) > 2:
            tgt_dirs.extend(args[2:])

        result = []
        for tgt_dir in tgt_dirs:
            tgt_file = os.path.join(tgt_dir, tgt_filename)
            logger.debug(f'Copying {src_file} to {tgt_file}')
            shutil.copy2(src_file, tgt_file)
            result.append(tgt_file)
        return ActionResult.success(action, result)

    @staticmethod
    def save_text(action: Action) -> ActionResult:
        args: [str] = action.get_args_as_str_list()
        content = args[0]
        chars = len(content)
        filename = DEFAULT_FILE_NAME if len(args) < 2 else args[1]
        tgt_dirs = action.get_output_dirs()
        if len(args) > 2:
            tgt_dirs.extend(args[2:])

        result = []
        for tgt_dir in tgt_dirs:
            tgt = os.path.join(tgt_dir, filename)
            logger.debug(f'Writing {chars} chars to {tgt}')
            write_content(content, tgt)
            result.append(tgt)

        return ActionResult.success(action, result)

    @staticmethod
    def set_context_values(run_context: RunContext, action: Action) -> ActionResult:
        query: str = action.get_arg_str()
        values: dict = parse_query(query)
        for key, value in values.items():
            run_context.set(key, value)
        return ActionResult.success(action)

    @staticmethod
    def starts_with(action: Action) -> ActionResult:
        success, prefix = ActionHandler.__starts_with(action)
        return ActionResult(action, success, prefix)

    @staticmethod
    def __starts_with(action: Action) -> tuple[bool, str or None]:
        args: [str] = action.get_args_as_str_list()
        value: str = args[0]
        prefixes: [str] = args[1:]
        for prefix in prefixes:
            if value.startswith(prefix):
                return True, prefix
        return False, None

    @staticmethod
    def get_first_file(action: Action) -> ActionResult:
        files_result: ActionResult = ActionHandler.get_files(action)
        if not files_result.is_success():
            return files_result
        files: list[str] = files_result.get_result()
        first_file = None if files is None or len(files) == 0 else files[0]
        return ActionResult(action, first_file is not None, first_file)

    @staticmethod
    def eval(action: Action) -> ActionResult:
        exec("import importlib")
        result = eval(action.get_arg_str())
        return ActionResult.success(action, result)

    @staticmethod
    def exec(action: Action) -> ActionResult:
        exec(action.get_arg_str())
        return ActionResult.success(action)

    @staticmethod
    def get_file_content(action: Action) -> ActionResult:
        file_path = action.get_first_arg_as_str()
        return ActionResult.success(action, read_content(file_path))

    @staticmethod
    def get_files(action: Action) -> ActionResult:
        return ActionResult.success(action, ActionHandler.__get_files(action))

    @staticmethod
    def __get_files(action: Action) -> list[str]:
        args: [] = action.get_args_as_str_list()
        dir_path: str = args[0]
        file_type: str = args[1]
        files: [] = []
        for entry in os.scandir(dir_path):
            if ActionHandler.accept_dir_entry(entry, file_type):
                files.append(entry.path)
        return files

    @staticmethod
    def __get_newest_file_in_dir(dir_path: str,
                                 file_type: str,
                                 result_if_none: Union[str, None]) -> str:
        # iterate over the files in the directory using os.scandir
        most_recent_file = None
        most_recent_time = 0
        for entry in os.scandir(dir_path):
            if ActionHandler.accept_dir_entry(entry, file_type):
                # get the modification time of the file using entry.stat().st_mtime_ns
                mod_time = entry.stat().st_mtime_ns
                if mod_time > most_recent_time:
                    # update the most recent file and its modification time
                    most_recent_file = entry.path
                    most_recent_time = mod_time
        return result_if_none if most_recent_file is None else most_recent_file

    @staticmethod
    def accept_dir_entry(entry: os.DirEntry, file_type: str) -> bool:
        return entry.is_file() and (file_type == ActionHandler.__ALL_FILE_TYPES or
                                    entry.name.endswith(file_type))


class NoopActionHandler(ActionHandler):
    def execute(self, run_context: RunContext, action: Action) -> ActionResult:
        return ActionResult.none()


NOOP: ActionHandler = NoopActionHandler()
