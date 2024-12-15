import imghdr
import logging
import os
from typing import Union

from pyu.io.file import create_file
from .config import RunArg
from .env import get_upload_file

logger = logging.getLogger(__name__)


def _secure_filename(filename: str) -> str:
    # TODO - Implement this or use a library function like: werkzeug.utils.secure_filename
    return filename


def _get_image_ext(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    file_ext = imghdr.what(None, header)
    if not file_ext:
        return None
    return '.' + file_ext


def _validate_image_ext(uploaded_file):
    file_ext = os.path.splitext(uploaded_file.filename)[1]
    if file_ext not in [".jpeg", ".jpg"]:
        raise ValueError(f"Invalid file type: {file_ext}")
    img_ext = _get_image_ext(uploaded_file.stream)
    if not img_ext or img_ext not in [".jpeg", ".jpg"]:
        raise ValueError(f"Invalid image type: {img_ext}")


def _save_file(task_id, files, input_name) -> Union[str, None]:
    uploaded_file = files.get(input_name)
    if not uploaded_file:
        return None
    if not uploaded_file.filename:
        return None
    if input_name == RunArg.IMAGE_FILE.value or \
            input_name == RunArg.IMAGE_FILE_SQUARE.value:
        _validate_image_ext(uploaded_file)
    filepath = get_upload_file(task_id, _secure_filename(uploaded_file.filename))
    logger.debug(f"Will save: {input_name} to {filepath}")
    create_file(filepath)
    uploaded_file.save(filepath)
    return filepath


def save_files(task_id, files) -> dict[str, any]:
    saved_files = {}
    for e in RunArg:
        run_arg = RunArg(e)
        if not run_arg.is_path:
            continue
        saved_file = _save_file(task_id, files, run_arg.value)
        if not saved_file:
            continue
        saved_files[run_arg.value] = saved_file
    return saved_files
