import os.path
import shutil

from aideas.app.action.action import Action
from aideas.app.action.action_result import ActionResult
from aideas.app.agent.blog_automator_agent import BlogAutomatorAgent
from aideas.app.env import Env
from aideas.app.result.result_set import StageResultSet
from aideas.app.run_context import RunContext


class TestBlogAutomatorAgent(BlogAutomatorAgent):
    def run(self, run_context: RunContext) -> StageResultSet:
        try:
            return super().run(run_context)
        finally:
            self.__delete_dirs(run_context)

    def clone_blog(self, action: Action, run_context: RunContext) -> ActionResult:
        # Rather than clone the blog we create its dir and init a git repo there
        # This way we can call git commands on it
        working_dir = self.get_blog_tgt_dir()
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
        return [
            ['git', 'config', 'user.email', f'"{run_context.get_env(Env.GIT_USER_EMAIL)}"'],
            # ['git', 'remote', 'set-url', 'origin',
            #  self.__get_blog_src_url_with_credentials(run_context)],
            ['git', 'add', '.'],
            ['git', 'commit', '-m', '"Add blog post"'],
            # ['git', 'push']
        ]

    def _get_build_update_blog_image_command_args(self) -> list[str]:
        return ['echo', '"Test mode: Skipping actual build of blog update image."']

    def _get_update_blog_command_args(self, run_context: RunContext) -> list[str]:
        return ['echo', '"Test mode: Skipping actual blog update."']

    def __delete_dirs(self, run_context: RunContext):
        dirs_to_delete = [self.get_blog_input_dir(run_context), self.get_blog_tgt_dir()]

        def onerror(_, path, exc_info):
            print(f'{__name__} Failed to remove: {path}. {exc_info}')

        for dir_to_delete in dirs_to_delete:
            if os.path.exists(dir_to_delete):
                shutil.rmtree(dir_to_delete, onerror=onerror)
                print(f'{__name__} Successfully removed: {dir_to_delete}')
