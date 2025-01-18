import logging
import os.path
from typing import Union

from .config import RunArg
from .image_service import save_files

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]


class RequestData:
    @staticmethod
    def require_tag(request) -> Union[str, None]:
        tag = RequestData.get(request, 'tag')
        if not tag:
            raise ValidationError("Specify what you want to automate using a 'tag'.")
        return tag

    @staticmethod
    def require_agent_names(request) -> [str]:
        agent_names = request.args.to_dict(flat=False).get(RunArg.AGENTS.value)
        if not agent_names:
            agent_names = request.form.getlist(RunArg.AGENTS.value)
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
    def automation_details(request) -> dict[str, any]:
        return {
            'tag': RequestData.require_tag(request),
            RunArg.AGENTS.value: RequestData.require_agent_names(request)}

    @staticmethod
    def task_config(task_id: str, request) -> dict[str, any]:
        form_data = dict(request.form)

        def get_file_name(input_name: str, upload_file_name: str) -> str:
            text_title = form_data.get(RunArg.TEXT_TITLE.value, None)
            if not text_title:
                return upload_file_name
            if input_name == RunArg.TEXT_FILE.value:
                _, ext = os.path.splitext(upload_file_name)
                logger.debug(f"For {input_name} using file name: {text_title}{ext}, "
                             f"instead of {upload_file_name}")
                return f'{text_title}{ext}'
            return upload_file_name

        asynch = RequestData.get(request, 'async', True)
        try:
            form_data = RequestData.strip_values(form_data)
            logger.debug(f"Form data: {form_data}")

            run_config = RunArg.of_dict(form_data)
            RequestData.validate_task_config_form_data(run_config)
            agent_names = RequestData.require_agent_names(request)

            form_data.update(save_files(task_id, request.files, get_file_name))

            result = {**run_config, RunArg.AGENTS.value: agent_names, 'async': asynch}
            logger.debug(f"Result: {result}")
            return result
        except ValueError as value_ex:
            logger.exception(value_ex)
            raise ValidationError(value_ex.args[0])

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
