from flask import Flask, render_template, request
from flask_cors import CORS
import uuid
import logging.config

from app.request_data import RequestData, ValidationError
from app.app import App
from app.env import get_app_port, is_production
from app.task import get_task, stop_task
from app.web_service import WebService

web_app = Flask(__name__)
CORS(web_app)


INDEX_TEMPLATE = 'index.html'
AUTOMATION_INDEX_TEMPLATE = 'automate/index.html'


@web_app.errorhandler(ValidationError)
def handle_validation_error(e):
    return render_template(
        AUTOMATION_INDEX_TEMPLATE, **web_service.automation_index({"error": e.message})), 400


@web_app.route('/')
def index():
    return render_template(INDEX_TEMPLATE, **web_service.index())


@web_app.route('/' + AUTOMATION_INDEX_TEMPLATE)
def automaton_index():
    return render_template(AUTOMATION_INDEX_TEMPLATE, **web_service.automation_index())


@web_app.route('/automate/select-agents.html')
def select_automaton_agents():
    return render_template('automate/select-agents.html',
                           **web_service.select_automation_agents(RequestData.require_tag(request)))


@web_app.route('/automate/enter-details.html')
def enter_automation_details():
    data: dict[str, any] = RequestData.automation_details(request)
    return render_template(
        'automate/enter-details.html', **web_service.enter_automation_details(data))


TASK_INDEX_TEMPLATE = 'task/index.html'


@web_app.route('/automate/start', methods=['POST'])
def start_automation():
    task_id = str(uuid.uuid4().hex)

    data = RequestData.task_config(task_id, request)

    if data['async'] is True:
        web_service.start_automation_async(task_id, data)
        return _render_task_index_template(f"Submitted task: {task_id}")

    task = web_service.start_automation(task_id, data)
    args = {"info": f'<span style="font-size:0.75rem;">{task.to_html()}</span>'}
    template_args = {**web_service.automation_index(), **args}
    return render_template(AUTOMATION_INDEX_TEMPLATE, **template_args)


@web_app.route('/' + TASK_INDEX_TEMPLATE)
def view_tasks():
    return _render_task_index_template()


@web_app.route('/task/<task_id>')
def task_by_id(task_id: str):
    return _render_task_index_template(_task_by_id(task_id))


def _task_by_id(task_id: str):
    task = get_task(task_id)

    if task is None:
        return f"Task not found: {task_id}"

    if task.is_started() is False:
        return f"Task not started: {task_id}"

    if task.is_completed() is True:
        return f"<p>Task already completed: {task_id}</p>{task.to_html()}"

    if request.args.get('action') == 'stop':

        stop_task(task_id)

        return f"<p>Task stopped: {task_id}</p>{task.to_html()}"

    return f"<p>Displaying task: {task_id}</p>{task.to_html()}"


def _get_task_links(task_id: str) -> dict[str, any]:
    return {'view': '/task/' + task_id, 'stop': '/task/' + task_id + '?action=stop'}


def _render_task_index_template(info: str = None):
    return render_template(TASK_INDEX_TEMPLATE, **web_service.tasks(_get_task_links, info))


if __name__ == '__main__':

    config_loader = App.init()

    logging.config.dictConfig(config_loader.load_logging_config())

    web_service = WebService(config_loader)

    web_app.run(
        host='0.0.0.0',
        port=get_app_port(),
        debug=is_production() is False)

