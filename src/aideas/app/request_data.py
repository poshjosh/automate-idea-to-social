import logging
import os.path
from typing import Union

from .config import RunArg
from .env import Env, get_app_language
from .i18n import I18n
from .image_service import save_files

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]

class RequestData:
    @staticmethod
    def get_list(request, key: str, result_if_none: [str]) -> list[str]:
        values = request.args.to_dict(flat=False).get(key)
        if not values:
            values = request.form.getlist(key)
        return values if values else result_if_none

    @staticmethod
    def require_agent_names(request) -> [str]:
        agent_names = RequestData.get_list(request, RunArg.AGENTS.value, None)
        if not agent_names:
            raise ValidationError("No agents specified.")
        return agent_names

    @staticmethod
    def get(request, key: str, result_if_none: any = None) -> Union[str, None]:
        val = request.args.get(key)
        if not val:
            val = request.form.get(key)
        return result_if_none if not val else val

    @staticmethod
    def require_tag(request) -> Union[str, None]:
        tag = RequestData.get(request, 'tag')
        if not tag:
            raise ValidationError("Specify what you want to automate using a 'tag'.")
        return tag

    @staticmethod
    def automation_details(request) -> dict[str, any]:
        return {
            'tag': RequestData.require_tag(request),
            RunArg.AGENTS.value: RequestData.require_agent_names(request)}

    @staticmethod
    def task_config(task_id: str, request) -> dict[str, any]:
        request_data = {**dict(request.form)}
        lang_codes = RequestData.get_list(request, RunArg.LANGUAGE_CODES.value, None)
        if lang_codes:
            request_data[RunArg.LANGUAGE_CODES.value] = ",".join(lang_codes)

        def get_file_name(input_name: str, upload_file_name: str) -> str:
            text_title = request_data.get(RunArg.TEXT_TITLE.value, None)
            if not text_title:
                return upload_file_name
            if input_name == RunArg.TEXT_FILE.value:
                _, ext = os.path.splitext(upload_file_name)
                logger.debug(f"For {input_name} using file name: {text_title}{ext}, "
                             f"instead of {upload_file_name}")
                return f'{text_title}{ext}'
            return upload_file_name

        try:
            request_data = RequestData.strip_values(request_data)
            logger.debug(f" Input form data: {request_data}")

            # first this
            request_data.update(save_files(task_id, request.files, get_file_name))

            # then this, otherwise the world will end.
            request_data = RunArg.of_dict(request_data)

            request_data[RunArg.AGENTS.value] = RequestData.require_agent_names(request)
            request_data[RunArg.INPUT_LANGUAGE_CODE.value] = RequestData.get_language_code(request)
            request_data["async"] = RequestData.get(request, 'async', True)

            RequestData.validate_task_config_form_data(request_data)

            logger.debug(f"Request data: {request_data}")
            return request_data
        except ValueError as value_ex:
            logger.exception(value_ex)
            raise ValidationError(value_ex.args[0])

    @staticmethod
    def get_language_code(request) -> Union[str, None]:
        supported_lang_codes = I18n.get_supported_language_codes()
        return request.accept_languages.best_match(supported_lang_codes)

    @staticmethod
    def strip_values(data: dict[str, any]):
        for k, v in data.items():
            v = v.strip() if isinstance(v, str) else v
            data[k] = v
        return data

    @staticmethod
    def validate_task_config_form_data(form_data: dict[str, any]):
        for k, v in form_data.items():
            if v == '':
                raise ValidationError(f"'{k}' is required")
