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


@web_app.errorhandler(Exception)
def handle_error(e):
    if not is_production():
        print(e)
    error_data = {"error": e.message if hasattr(e, 'message') else str(e)}
    if request.content_type and 'json' in request.content_type:
        return error_data, 400
    return render_template(
        AUTOMATION_INDEX_TEMPLATE, **web_service.automation_index(error_data)), 400

@web_app.route('/')
def index():
    return render_template(INDEX_TEMPLATE, **web_service.index())


@web_app.route('/info/health/status')
def health_status():
    """
    Health check endpoint to verify that the web service is running.
    :return: A simple message indicating the service is running.
    """
    return "Up", 200

@web_app.route('/' + AUTOMATION_INDEX_TEMPLATE)
def automaton_index():
    return render_template(AUTOMATION_INDEX_TEMPLATE, **web_service.automation_index())


@web_app.route('/automate/select-agents.html')
def select_automaton_agents():
    return render_template('automate/select-agents.html',
                           **web_service.select_automation_agents(RequestData.require(request, 'tag')))


@web_app.route('/automate/enter-details.html')
def enter_automation_details():
    data: dict[str, any] = RequestData.automation_details(request)
    return render_template(
        'automate/enter-details.html', **web_service.enter_automation_details(data))


TASK_INDEX_TEMPLATE = 'task/index.html'


@web_app.route('/automate/start', methods=['POST'])
def start_automation():
    task_id = str(uuid.uuid4().hex)

    data = RequestData.task_config_from_form(task_id, request)

    if data['async'] is True:
        web_service.start_automation_async(task_id, data)
        return _render_task_index_template(f"Submitted task: {task_id}")

    task = web_service.start_automation(task_id, data)
    args = {"info": f'<span style="font-size:0.75rem;">{task.to_html()}</span>'}
    template_args = {**web_service.automation_index(), **args}
    return render_template(AUTOMATION_INDEX_TEMPLATE, **template_args)


@web_app.route('/api/tasks', methods=['POST'])
def api_tasks():

    task_id = str(uuid.uuid4().hex)

    data = RequestData.task_config_from_json_body(task_id, request)

    if data['async'] is True:
        web_service.start_automation_async(task_id, data)
        return { "id": task_id }, 201

    web_service.start_automation(task_id, data)
    return { "task": web_service.api_task(_api_get_task_links, task_id) }, 201


@web_app.route('/' + TASK_INDEX_TEMPLATE)
def view_tasks():
    return _render_task_index_template()

@web_app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    return {**web_service.api_tasks(_api_get_task_links)}

@web_app.route('/task/<task_id>')
def task_by_id(task_id: str):
    task = _task_by_id(task_id, request.args.get('action'))
    if task.is_stopped():
        info = f"<p>Task stopped: {task_id}</p>{task.to_html()}"
    else:
        info = f"<p>Displaying task: {task_id}</p>{task.to_html()}"
    return _render_task_index_template(info)

@web_app.route('/api/tasks/<task_id>', methods=['GET'])
def api_task_by_id(task_id: str):
    _task_by_id(task_id, request.args.get('action'))
    return { "task": web_service.api_task(_api_get_task_links, task_id) }


@web_app.route('/api/agents', methods=['GET'])
def api_get_agents():
    """
    Get the names of all agents, limited to those matching a tag, if specified in the request.
    :return: A list of agent names, limited to those matching a tag if specified in the request.
    """
    return {**web_service.api_get_automation_agent_names(RequestData.get(request, 'tag'))}


@web_app.route('/api/agents/<agent_name>', methods=['GET'])
def api_get_agent_config_by_name(agent_name: str):
    return {**web_service.api_get_automation_agent_config(agent_name)}


def _task_by_id(task_id: str, action = None):
    task = get_task(task_id)

    if task is None:
        raise FileNotFoundError(f"Task not found: {task_id}")

    if not task.is_started():
        raise ValidationError(f"Task not started: {task_id}")

    if action == 'stop':
        if task.is_completed():
            raise ValidationError(f"Task already completed: {task_id}")
        stop_task(task_id)

    return task


def _get_task_links(task_id: str) -> dict[str, any]:
    return {'view': '/task/' + task_id, 'stop': '/task/' + task_id + '?action=stop'}

def _api_get_task_links(task_id: str) -> dict[str, any]:
    return {'view': '/api/tasks/' + task_id, 'stop': '/api/tasks/' + task_id + '?action=stop'}

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

