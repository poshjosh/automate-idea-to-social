import logging
import os
import shutil
import time
from enum import Enum, unique
from typing import Callable, Union

from .action import Action
from .action_result import ActionResult
from ..io.file import read_content, write_content

logger = logging.getLogger(__name__)

DEFAULT_FILE_NAME = "result.txt"


class ActionError(Exception):
    pass


def execute_for_result(func: Callable[[any], any],
                       arg: any,
                       action: Action) -> ActionResult:
    try:
        result = func(arg)
    except Exception as ex:
        raise ActionError(f'Error while executing {action}') from ex
    else:
        return ActionResult(action, True, result)


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
    GET_FILE_CONTENT = 'get_file_content'
    GET_FILES = 'get_files'
    GET_FIRST_FILE = 'get_first_file'
    GET_NEWEST_FILE_IN_DIR = 'get_newest_file_in_dir'
    LOG = 'log'
    SAVE_FILE = 'save_file'
    SAVE_TO_FILE = 'save_to_file'
    STARTS_WITH = 'starts_with'
    WAIT = ('wait', False)


class ActionHandler:
    __ALL_FILE_TYPES = '*'

    @staticmethod
    def noop() -> 'ActionHandler':
        return NOOP

    @staticmethod
    def to_action_id(action: str) -> BaseActionId:
        return ActionId(action)

    def execute(self, action: Action) -> ActionResult:
        key = action.get_name_without_negation() if action.is_negation() else action.get_name()
        result = self._execute(key, action)
        if action.is_negation():
            result = result.flip()
        return result

    def _execute(self, key: str, action: Action) -> ActionResult:
        if action == Action.none():
            result = ActionResult.none()
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
        elif key == ActionId.SAVE_FILE.value:
            result: ActionResult = self.save_file(action)
        elif key == ActionId.SAVE_TO_FILE.value:
            result: ActionResult = self.save_to_file(action)
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
        arg: str = action.require_first_arg()
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
        args: [str] = action.get_args()
        dir_path: str = action.require_first_arg()
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
        arg_list: [] = action.get_args()
        logger.log(logging.getLevelName(arg_list[0]), ' '.join(arg_list[1:]))
        return ActionResult(action, True)

    @staticmethod
    def save_file(action: Action) -> ActionResult:
        src = action.require_first_arg()
        tgt_dir = ActionHandler.__make_target_dirs_if_need(action)
        tgt = os.path.join(tgt_dir, os.path.basename(src))
        logger.debug(f'Copying {src} to {tgt}')
        return execute_for_result(lambda arg: shutil.copy2(src, tgt), src, action)

    @staticmethod
    def save_to_file(action: Action) -> ActionResult:
        args: [str] = action.get_args()

        def save_content(content: str):
            tgt_dir = ActionHandler.__make_target_dirs_if_need(action)
            tgt = os.path.join(tgt_dir, DEFAULT_FILE_NAME if len(args) < 2 else args[1])
            logger.debug(f'Writing to {tgt}')
            return write_content(content, tgt)

        return execute_for_result(save_content, args[0], action)

    @staticmethod
    def starts_with(action: Action) -> ActionResult:
        success, prefix = ActionHandler.__starts_with(action)
        return ActionResult(action, success, prefix)

    @staticmethod
    def __starts_with(action: Action) -> tuple[bool, str or None]:
        args: [str] = action.get_args()
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
    def get_file_content(action: Action) -> ActionResult:
        file_path = action.get_first_arg()
        return execute_for_result(lambda arg: read_content(arg), file_path, action)

    @staticmethod
    def get_files(action: Action) -> ActionResult:
        return execute_for_result(
            lambda args: ActionHandler.__get_files(action), action.get_args(), action)

    @staticmethod
    def __get_files(action: Action) -> list[str]:
        args: [] = action.get_args()
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

    @staticmethod
    def __make_target_dirs_if_need(action: Action) -> str:
        tgt_dir = action.get_results_dir()
        if not os.path.exists(tgt_dir):
            os.makedirs(tgt_dir)
        return tgt_dir


class NoopActionHandler(ActionHandler):
    def execute(self, action: Action) -> ActionResult:
        return ActionResult.none()


NOOP: ActionHandler = NoopActionHandler()