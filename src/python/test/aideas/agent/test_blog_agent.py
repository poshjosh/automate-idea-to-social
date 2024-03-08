import os.path
import shutil

from ....main.aideas.action.action import Action
from ....main.aideas.action.action_result import ActionResult
from ....main.aideas.agent.blog_agent import BlogAgent
from ....main.aideas.result.stage_result_set import StageResultSet
from ....main.aideas.run_context import RunContext


class TestBlogAgent(BlogAgent):
    @staticmethod
    def of_config(agent_config: dict[str, any]) -> BlogAgent:
        return TestBlogAgent(agent_config)

    def run(self, run_context: RunContext) -> StageResultSet:
        try:
            return super().run(run_context)
        finally:
            self.__delete_dirs(run_context)

    def clone_blog(self, action: Action, run_context: RunContext) -> ActionResult:
        # Rather than clone the blog we create its dir and init a git repo there
        # This way we can call git commands on it
        working_dir = self.get_blog_base_dir()
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
            command = f'cd {working_dir} && git init'
            return_code = os.system(command)
            print(f'{__name__} Command: {command} returned: {return_code}')
        return ActionResult(action, True, self.get_blog_tgt_dir())

    def _get_update_blog_content_commands(self):
        commands: list[list[str]] = super()._get_update_blog_content_commands()
        # We remove the last command which is: git push
        return commands[:-1]

    def _get_update_blog_command_args(self, run_context: RunContext) -> [str]:
        command: [str] = super()._get_update_blog_command_args(run_context)
        command.append('-s true')  # skip running the app
        return command

    def __delete_dirs(self, run_context: RunContext):
        dirs_to_delete = [self.get_blog_input_dir(run_context), self.get_blog_tgt_dir()]

        def onerror(func, path, exc_info):
            print(f'{__name__} Failed to remove: {path}. {exc_info}')

        for dir_to_delete in dirs_to_delete:
            if os.path.exists(dir_to_delete):
                shutil.rmtree(dir_to_delete, onerror=onerror)
                print(f'{__name__} Successfully removed: {dir_to_delete}')
