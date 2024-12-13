import pickle
import shutil
import logging
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Union

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


class Task:
    @staticmethod
    def of_defaults(config_loader: ConfigLoader, run_config: dict[str, any]) -> 'Task':
        config_loader = config_loader.with_added_variable_source(run_config)
        app_config = config_loader.load_app_config()
        agent_factory = AgentFactory(config_loader, app_config)
        return Task(agent_factory, RunContext.of_config(app_config, run_config))

    def __init__(self, agent_factory: AgentFactory, run_context: RunContext):
        self.__agent_factory = agent_factory
        self.__run_context = run_context
        self.__started = False
        self.__completed = False

    def start(self) -> 'Task':
        try:
            if self.is_started():
                raise Exception(
                    "Task already running" if self.is_running() else "Task already completed")
            self.__started = True
            self.__start()
            return self
        finally:
            self.__completed = True

    def stop(self) -> 'Task':
        self.__completed = True
        return self

    def is_started(self) -> bool:
        return self.__started

    def is_running(self) -> bool:
        return self.__started and not self.__completed

    def is_completed(self) -> bool:
        return self.__started and self.__completed

    def get_run_context(self) -> RunContext:
        return self.__run_context

    def get_result_set(self) -> AgentResultSet:
        return self.__run_context.get_result_set()

    def get_agent_names(self) -> [str]:
        return self.__run_context.get_agent_names()

    def to_html(self) -> str:
        result_str = (self.get_result_set().pretty_str("\n", "&emsp;")
                      .replace("ActionResult(", "(")
                      .replace(", Action(", ", (")
                      .replace(", result: None)", ")")
                      .replace(", result: ResultSet(success-rate=0/0))", ")")
                      .replace("(success=True,", '(<span style="color:green">SUCCESS</span>,')
                      .replace("(success=False,", '(<span style="color:red">FAILURE</span>,'))
        result_str = secrets_masking_filter.redact(result_str)
        return result_str.replace("\n", "<br>")  # Replace new-line only after masking secrets

    def __start(self) -> AgentResultSet:

        agent_names = self.__run_context.get_agent_names()

        logger.debug(f"Running agents: {agent_names}")

        for agent_name in agent_names:
            agent = self.__agent_factory.get_agent(agent_name)

            try:
                stage_result_set = agent.run(self.__run_context)
                self.__save_agent_results(agent_name, stage_result_set)
            except Exception as ex:
                if self.__run_context.get_run_config().is_continue_on_error() is True:
                    logger.exception(ex)
                    result = self.__run_context.get_stage_results(agent_name)
                    if not result or result.is_empty():
                        action = Action.of(agent_name, "*", "*", "*", self.__run_context)
                        self.__run_context.add_action_result(ActionResult.failure(action, "Error"))
                else:
                    raise ex
        return self.__run_context.get_result_set().close()

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
    tasks = {**__tasks}
    for task_id in get_task_ids():
        stop_task(task_id)
    with __executor as executor:
        executor.shutdown(wait=True, cancel_futures=True)
    return tasks


def stop_task(task_id: str) -> Task:
    return __tasks.pop(task_id).stop()
