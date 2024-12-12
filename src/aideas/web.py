from flask import Flask, render_template, request
# from flask_cors import CORS
import uuid
import logging.config

from app.app import App
from app.env import get_app_port, is_production
from app.task import get_task, stop_task
from app.web_service import WebService, ValidationError

web_app = Flask(__name__)
# CORS(web_app)


@web_app.route('/')
def index():
    return render_template('index.html', **web_service.index())


@web_app.route('/automate/index.html')
def automate():
    return render_template('automate/index.html', **web_service.automate())


@web_app.route('/automate/details.html')
def automate_task():
    tag = request.args['tag']
    return render_template('automate/details.html', **web_service.automate_task(tag))


TASK_INDEX_TEMPLATE = 'task/index.html'


@web_app.route('/automate/start', methods=['POST'])
def automate_start():
    asynch = request.args.get('async', True)
    task_id = str(uuid.uuid4())

    if asynch is True:
        web_service.automate_start_async(task_id, request.form, request.files)
        return _render_task_index_template(f"Submitted task: {task_id}")

    try:
        task = web_service.automate_start(task_id, request.form, request.files)
        args = {"info": f'<span style="font-size:0.75rem;">{task.to_html()}</span>'}
    except Exception as ex:
        args = _convert_to_error_obj(ex)
    template_args = {**web_service.automate(), **args}
    return render_template('automate/index.html', **template_args)


@web_app.route(f'/{TASK_INDEX_TEMPLATE}')
def view_tasks():
    return _render_task_index_template()


@web_app.route('/task/<task_id>')
def task_by_id(task_id: str):
    return _render_task_index_template(_task_by_id(task_id))


def _task_by_id(task_id: str):
    task = get_task(task_id)

    if task is None:
        return f"Task not found: {task_id}"

    if request.args.get('action') == 'stop':
        if task.is_started() is False:
            return f"Task is not started: {task_id}"
        if task.is_completed() is True:
            return f"Task is already completed: {task_id}"

        stop_task(task_id)

        return f"<p>Task stopped: {task_id}</p>{task.to_html()}"

    return f"<p>Displaying task: {task_id}</p>{task.to_html()}"


def _get_task_links(task_id: str) -> dict[str, any]:
    return {'view': '/task/' + task_id, 'stop': '/task/' + task_id + '?action=stop'}


def _render_task_index_template(info: str = None):
    return render_template(TASK_INDEX_TEMPLATE, **web_service.tasks(_get_task_links, info))


def _convert_to_error_obj(ex: Exception) -> dict[str, str]:
    default_err_msg = "An unexpected error occurred while trying to automate."
    if isinstance(ex, ValidationError):
        return {"error": ex.message if ex.message else default_err_msg}
    else:
        return {"error": default_err_msg}


if __name__ == '__main__':

    config_loader = App.init()

    logging.config.dictConfig(config_loader.load_logging_config())

    web_service = WebService(config_loader)

    web_app.run(
        host='0.0.0.0',
        port=get_app_port(),
        debug=is_production() is False)

