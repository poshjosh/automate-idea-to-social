import pickle
import shutil
import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Union, TypeVar, Callable

from pyu.io.file import create_file
from pyu.io.logging import SecretsMaskingFilter
from .action.action import Action
from .action.action_result import ActionResult
from .agent.agent_factory import AgentFactory
from .env import get_cached_results_file
from .result.result_set import AgentResultSet, StageResultSet
from .config_loader import ConfigLoader
from .run_context import RunContext

logger = logging.getLogger(__name__)

secrets_masking_filter = SecretsMaskingFilter(
    ["(pass|key|secret|token|jwt|hash|signature|credential|auth|certificate|connection|pat)"])

RESULT = TypeVar("RESULT", bound=Union[any, None])


class Task:
    def __init__(self):
        self.__started = False
        self.__completed = False

    def start(self) -> RESULT:
        try:
            if self.is_started():
                logger.error(
                    "Task already running" if self.is_running() else "Task already completed")
                return None
            self.__started = True
            return self._start()
        except Exception as ex:
            logger.exception("Task error", ex)
        finally:
            self.__completed = True

    def _start(self) -> RESULT:
        raise NotImplementedError()

    def to_html(self) -> str:
        raise NotImplementedError()

    def stop(self) -> 'Task':
        self.__completed = True
        return self

    def is_started(self) -> bool:
        return self.__started

    def is_running(self) -> bool:
        return self.__started and not self.__completed

    def is_completed(self) -> bool:
        return self.__started and self.__completed


class AgentTask(Task):
    @staticmethod
    def of_defaults(config_loader: ConfigLoader, run_config: dict[str, any]) -> 'AgentTask':
        config_loader = config_loader.with_added_variable_source(run_config)
        app_config = config_loader.load_app_config()
        agent_factory = AgentFactory(config_loader, app_config)
        return AgentTask(agent_factory, RunContext.of_config(app_config, run_config))

    def __init__(self, agent_factory: AgentFactory, run_context: RunContext):
        super().__init__()
        self.__agent_factory = agent_factory
        self.__run_context = run_context
        self.__agent_states = {}
        for name in run_context.get_agent_names():
            self.__agent_states[name] = "PENDING"

    def get_run_context(self) -> RunContext:
        return self.__run_context

    def to_html(self) -> str:
        state_str = "<table><thead><tr><th>Agent</th><th>State</th></tr></thead><tbody>"
        for agent_name, state in self.__agent_states.items():
            state_str += f"<tr><td>{agent_name}</td><td>{state}</td></tr>"
        state_str += "</tbody></table>"
        result_str = (self.__run_context.get_result_set().pretty_str("\n", "&emsp;&emsp;")
                      .replace("ActionResult(", "(")
                      .replace(", Action(", ", (")
                      .replace(", result: None)", ")")
                      .replace(", result: ResultSet(success-rate=0/0))", ")")
                      .replace("(success=True,", '(<span style="color:green">SUCCESS</span>,')
                      .replace("(success=False,", '(<span style="color:red">FAILURE</span>,'))

        result_str = secrets_masking_filter.redact(result_str)

        # Replace new-line only after masking secrets
        return state_str + result_str.replace("\n", "<br/>")

    def _start(self) -> AgentResultSet:

        agent_names = self.__run_context.get_agent_names()

        logger.debug(f"Running agents: {agent_names}")

        try:
            for agent_name in agent_names:

                try:

                    self.__add_agent_state(agent_name, "LOADING")

                    agent = self.__agent_factory.get_agent(agent_name)

                    self.__add_agent_state(agent_name, "RUNNING")

                    stage_result_set = agent.run(self.__run_context)

                    self.__add_agent_state(agent_name, "SUCCESS")

                    self.__save_agent_results(agent_name, stage_result_set)

                except Exception as ex:

                    self.__add_agent_state(agent_name, "FAILURE")

                    if self.__run_context.get_run_config().is_continue_on_error() is True:
                        logger.exception(ex)
                        result = self.__run_context.get_stage_results(agent_name)
                        if not result or result.is_empty():
                            action = Action.of(agent_name, "*", "*", "*", self.__run_context)
                            self.__run_context.add_action_result(ActionResult.failure(action, "Error"))
                    else:
                        raise ex
        finally:
            self.__run_context.get_result_set().close()

        return self.__run_context.get_result_set()

    def __add_agent_state(self, agent_name: str, state: str):
        self.__agent_states[agent_name] = self.__agent_states[agent_name] + ' >> ' + state

    def __save_agent_results(self, agent_name, result_set: StageResultSet):
        """
        Save the result to a file. (e.g. twitter/2021/01/01_12-34-56-uuid.pkl)
        Save a success file if the result is successful. (e.g. 01_12-34-56-uuid.pkl.success)
        :param agent_name: The name of the agent whose result is to be saved.
        :param result_set: The result to be saved.
        :return: None
        """
        name: str = "result-set"
        object_path: str = get_cached_results_file(agent_name, f'{name}.pkl')

        create_file(object_path)
        with open(object_path, 'wb') as file:
            pickle.dump(result_set, file)

        if result_set.is_successful():
            success_path = f'{object_path}.success'
            create_file(success_path)
        logger.debug(f"Agent: {agent_name}, result saved to: {object_path}")

        config_loader: ConfigLoader = self.__agent_factory.get_config_loader()
        config_path = config_loader.get_agent_config_path(agent_name)
        shutil.copy2(config_path, f'{object_path[:object_path.index(name)]}config.yaml')


__tasks: dict[str, Task] = {}
__executor = ThreadPoolExecutor(max_workers=10)


def init_tasks_cleanup(should_stop: Callable[[], bool], interval_seconds: int):
    def cleanup():
        if should_stop is True:
            logger.debug("Stopping tasks cleanup")
            return
        remove_completed_tasks()
        time.sleep(interval_seconds)
        __executor.submit(cleanup)

    __executor.submit(cleanup)


def add_task(task_id: str, task: Task):
    __tasks[task_id] = task
    return task


def submit_task(task_id: str, task: Task) -> Future:
    add_task(task_id, task)
    return __executor.submit(task.start)


def get_task(task_id: str, result_if_none: Union[Task, None] = None) -> Union[Task, None]:
    return __tasks.get(task_id, result_if_none)


def require_task(task_id: str) -> Task:
    return __tasks[task_id]


def get_task_ids() -> list[str]:
    return [e for e in __tasks.keys()]


def shutdown() -> dict[str, Task]:
    try:
        tasks = {**__tasks}
        logger.debug(f"Shutting down {len(tasks)} tasks")
        for task_id in get_task_ids():
            stop_task(task_id)
        __executor.shutdown(wait=False, cancel_futures=True)
        logger.debug(f"Done shutting down {len(tasks)} tasks")
        return tasks
    except Exception as ex:
        logger.exception(ex)


def stop_task(task_id: str) -> Task:
    return __tasks.pop(task_id).stop()


def remove_completed_tasks():
    logger.debug("Removing completed tasks")
    for task_id, task in __tasks.items():
        if task.is_completed():
            __tasks.pop(task_id)
