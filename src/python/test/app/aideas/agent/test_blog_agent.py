import os.path
import shutil

from .....main.app.aideas.action.action import Action
from .....main.app.aideas.action.action_result import ActionResult
from .....main.app.aideas.agent.blog_agent import BlogAgent
from .....main.app.aideas.result.result_set import StageResultSet
from .....main.app.aideas.run_context import RunContext


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

    def convert_to_markdown(self, action: Action, run_context: RunContext) -> ActionResult:
        result = super().convert_to_markdown(action, run_context)
        dir_to_create = self.get_blog_input_dir(run_context)
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)
            print(f'{__name__} Manually created dir: {dir_to_create}')
        return result

    def _get_update_blog_content_commands(self, run_context: RunContext) -> list[list[str]]:
        commands: list[list[str]] = super()._get_update_blog_content_commands(run_context)
        # We remove the last command which is: git push
        return commands[:-1]

    def _get_build_update_blog_image_command_args(self) -> [str]:
        return ['echo', '"Test mode: Skipping actual build of blog update image."']

    def _get_update_blog_command_args(self, run_context: RunContext) -> [str]:
        return ['echo', '"Test mode: Skipping actual blog update."']

    def __delete_dirs(self, run_context: RunContext):
        dirs_to_delete = [self.get_blog_input_dir(run_context), self.get_blog_tgt_dir()]

        def onerror(func, path, exc_info):
            print(f'{__name__} Failed to remove: {path}. {exc_info}')

        for dir_to_delete in dirs_to_delete:
            if os.path.exists(dir_to_delete):
                shutil.rmtree(dir_to_delete, onerror=onerror)
                print(f'{__name__} Successfully removed: {dir_to_delete}')
