import logging
import os
import shutil
import zipfile
from typing import Any, Callable, Union, AnyStr

from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_file(path):
    make_dirs(os.path.dirname(path))
    if not os.path.exists(path):
        with open(path, 'a'):
            os.utime(path, None)


def copy_and_change_ext(file_path: str, new_extension: str) -> str:
    pre, _ = os.path.splitext(file_path)
    target = pre + new_extension
    shutil.copy2(file_path, target)
    return file_path


def extract_zip_file(zip_file: str,
                     extract_to: str = os.getcwd(),
                     delete_zip_file: bool = False) -> bool:
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

            if delete_zip_file:
                try:
                    os.remove(zip_file)
                except Exception as ex:
                    logger.warning(f'Error deleting file: {zip_file}. {ex}')
        return True
    except Exception as ex:
        logger.error(f'Error extracting file: {zip_file}. {ex}')
        return False


def find_parent_dir(path: str,
                    test: Callable[[str, str], bool],
                    limit: int = 100,
                    result_if_none: Union[str, None] = None) -> str:
    result: str = path

    def reached_end(s: str) -> bool:
        return s is None or s == result or s == "" or s == os.sep

    for _ in range(limit):

        parent, name = os.path.split(result)

        if test(parent, name):
            return result

        if reached_end(parent) or reached_end(name):
            break

        result = parent

    return result_if_none


def visit_dirs(action: Callable[[str, str], None],
               root_src_dir: str = '.',
               root_dst_dir: str = None,
               test: Union[Callable[[str, str], bool], None] = None):
    """
    Visits recursively the source directory and performs the action on each file.

    The below code moves all the dir and files from the current directory to the directory ./abc
    highlight:: python
    code-block:: python
    visit_dir(lambda src, dst: shutil.move(src, dst), '.', './abc')
    """
    if not root_src_dir:
        raise ValueError("Source directory cannot be none or empty")
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = None if not root_dst_dir else src_dir.replace(root_src_dir, root_dst_dir, 1)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = None if not dst_dir else os.path.join(dst_dir, file_)
            if test is None or test(src_file, dst_file):
                action(src_file, dst_dir)


def read_content(file_path: str):
    with open(file_path, 'r+') as text_file:
        return text_file.read()


def write_content(content: AnyStr, file_path: str):
    with open(file_path, 'w+') as text_file:
        text_file.write(content)


def prepend_line(filename, line, separator: str = '\n'):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + separator + content)


def load_yaml(yaml_file_path: str, file_open_mode='r') -> Any:
    logger.debug(f'Will load yaml from: {yaml_file_path}')
    yaml = YAML(typ='rt')
    with open(yaml_file_path, file_open_mode) as yaml_file:
        config = yaml.load(yaml_file)
        logger.debug(f'Loaded yaml: {config}')
        return config


def load_yaml_str(yaml_str: str) -> Any:
    yaml = YAML(typ='rt')
    config = yaml.load(yaml_str)
    logger.debug(f'Loaded yaml: {config}')
    return config


def save_yaml(obj: Any, yaml_file_path: str, file_open_mode='w') -> Any:
    logger.debug(f'Will save yaml to: {yaml_file_path}')
    yaml = YAML()
    yaml.default_flow_style = False
    with open(yaml_file_path, file_open_mode) as yaml_file:
        config = yaml.dump(obj, yaml_file)
        logger.debug(f'Saved yaml: {config}')
        return config
