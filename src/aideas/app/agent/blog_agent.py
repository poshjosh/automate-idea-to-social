import logging
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from typing import Union

from pyu.io.file import extract_zip_file, prepend_line, read_content, visit_dirs
from pyu.io.shell import execute_command, run_command, run_commands_from_dir, run_script
from .agent import Agent
from ..agent.agent_name import AgentName
from ..action.action import Action
from ..action.action_result import ActionResult
from ..config import Name, RunArg
from ..env import Env, is_docker
from ..io.net import download_file
from ..result.result_set import ElementResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class BlogAgent(Agent):
    def run_stage(self,
                  run_context: RunContext,
                  stage: Name) -> ElementResultSet:
        stage_id: str = stage.id
        action = Action.of_generic(self.get_name(), stage_id)

        if stage_id == AgentName.BlogUpdaterStage.DOWNLOAD_APP:
            result: ActionResult = self.download_app(action)
        elif stage_id == AgentName.BlogUpdaterStage.CLONE_BLOG:
            result: ActionResult = self.clone_blog(action, run_context)
        elif stage_id == AgentName.BlogUpdaterStage.CONVERT_TO_MARKDOWN:
            result: ActionResult = self.convert_to_markdown(action, run_context)
        elif stage_id == AgentName.BlogUpdaterStage.UPDATE_BLOG_CONTENT:
            result: ActionResult = self.push_new_content_to_blog_repository(action, run_context)
        elif stage_id == AgentName.BlogUpdaterStage.UPDATE_BLOG:
            result: ActionResult = self.update_blog(action, run_context)
        else:
            return super().run_stage(run_context, stage)

        run_context.add_action_result(result)

        return run_context.get_element_results(self.get_name(), stage_id)

    def download_app(self, action: Action) -> ActionResult:
        # save_to_dir = /some/path
        # base_dir = ${save_to_dir}/app-name
        save_to_dir: str = self.get_app_tgt_dir()
        if os.path.exists(self.get_app_base_dir()):  # Already downloaded
            return ActionResult(action, True, save_to_dir)
        url: str = self.get_app_src_url()
        success = self.__download_and_extract_zip_to_dir(url, save_to_dir)
        return ActionResult(action, success, save_to_dir)

    def clone_blog(self, action: Action, run_context: RunContext) -> ActionResult:
        target_dir: str = self.get_blog_tgt_dir()

        # Rather than git pull, we are using git clone for each run.
        # For future git clones to succeed we need to remove the existing directory.
        # TODO - Implement git pull, if the directory already exists.
        self.__delete_cloned_blog_if_exists()

        git_clone_url: str = self.__get_blog_src_url_with_credentials(run_context)
        success = self.__clone_git_repo_to_dir(git_clone_url, target_dir)

        logger.debug(f"Cloned: {success} to: {target_dir}")  # git_clone_url contains sensitive info
        return ActionResult(action, success, target_dir)

    def convert_to_markdown(self, action: Action, run_context: RunContext) -> ActionResult:
        script_path: str = self.get_convert_to_markdown_script()
        input_file: str = self.__get_video_source(run_context)
        language_code: str = run_context.get_arg(RunArg.LANGUAGE_CODE, '')

        output_file: str = self.__convert_to_markdown(script_path, input_file, language_code, None)
        logger.debug(f"Converted to markdown: {output_file}, from: {input_file}, "
                     f"using script: {script_path}")
        if output_file is None:
            return ActionResult(action, False, output_file)

        src_image_path = run_context.get_arg(RunArg.IMAGE_FILE_LANDSCAPE)
        self.__prepend_image_link_to_file_content(src_image_path, output_file)

        return ActionResult(action, True, output_file)

    def push_new_content_to_blog_repository(self, action: Action, run_context: RunContext) -> ActionResult:
        blog_src_dir: str = self.get_blog_input_dir(run_context)
        if not os.path.exists(blog_src_dir):
            raise ValueError(f"Blog source directory does not exist: {blog_src_dir}")
        blog_target_dir: str = self.get_blog_tgt_dir()

        moved: [str] = []

        def move(src: str, dst: str):
            shutil.move(src, dst)
            logger.debug(f"Moved to: {dst}, from: {src}")
            moved.append(src)

        def may_move(_, dst: str) -> bool:
            return False if os.path.exists(dst) else True

        visit_dirs(move, blog_src_dir, blog_target_dir, may_move)

        if len(moved) == 0:  # Nothing to update
            logger.info(f"Moved {len(moved)} files to: {blog_target_dir} from: {blog_src_dir}")
            return ActionResult(action, True)

        commands: list[list[str]] = self._get_update_blog_content_commands(run_context)

        success = run_commands_from_dir(blog_target_dir, commands)

        return ActionResult(action, success)

    def update_blog(self, action: Action, run_context: RunContext) -> ActionResult:
        return ActionResult(action, self.__update_blog(run_context))

    @staticmethod
    def get_blog_input_dir(run_context: RunContext) -> str:
        video_input_file = BlogAgent.__get_video_source(run_context)
        # 'blog' is the name of the dir where the markdown content is saved
        # @see function BlogAgent.__convert_to_markdown
        return os.path.join(os.path.dirname(video_input_file), 'blog')

    @staticmethod
    def __get_video_source(run_context: RunContext):
        return run_context.get_arg(RunArg.TEXT_FILE)

    def __update_blog(self, run_context: RunContext) -> bool:

        app_base_dir = self.get_app_base_dir()

        if not os.path.exists(os.path.join(app_base_dir, 'Dockerfile')):
            logger.error("Dockerfile not found in dir: %s", app_base_dir)
            return False

        docker_container = self.get_app_docker_container_name()

        # Stop docker container if it is running
        # We run this container separately, because we ignore the error if it fails
        docker_stop_container_cmd = (f'docker ps -a | grep {docker_container} '
                                     f'&& timeout --kill-after=10 30 '
                                     f'docker container stop {docker_container}')
        execute_command(docker_stop_container_cmd, 60)

        docker_build_cmd = self._get_build_update_blog_image_command_args()

        docker_run_cmd = self._get_update_blog_command_args(run_context)

        timeout = self.get_config().get_stage_wait_timeout('update-blog', 1800)

        return run_commands_from_dir(
            app_base_dir, [docker_build_cmd, docker_run_cmd], [600, timeout - 600])

    def __download_and_extract_zip_to_dir(self,
                                          url: str,
                                          save_to_dir: str) -> bool:
        temp_file = os.path.join(tempfile.gettempdir(), f'{self.get_name()}-{uuid.uuid4().hex}')
        success: bool = download_file(url, temp_file)
        logger.debug(f"Downloaded: {success}, to: {temp_file}, from: {url}")
        if not success:
            return False
        success: bool = extract_zip_file(temp_file, save_to_dir, True)
        logger.debug(f"Extracted zip file: {success}, from: {save_to_dir}, from: {temp_file}")
        return success

    def __delete_blog_related_dirs_if_exists(self):
        if os.path.exists(self.get_blog_tgt_dir()):
            shutil.rmtree(self.get_blog_tgt_dir())
            logger.debug("Deleted blog target dir: %s", self.get_blog_tgt_dir())

    def __delete_cloned_blog_if_exists(self):
        # TODO Rather than remove the dir, we could just pull the latest changes
        self.__delete_blog_related_dirs_if_exists()
        # if os.path.exists(self.get_blog_base_dir()):  # Already cloned
        #     shutil.rmtree(self.get_blog_base_dir())

    @staticmethod
    def __clone_git_repo_to_dir(url: str, save_to_dir: str) -> bool:
        if not url.endswith(".git"):
            raise ValueError("URL must end with .git")

        return run_command(['git', 'clone', url, save_to_dir]).returncode == 0

    def __get_blog_src_url_with_credentials(self, run_context: RunContext) -> str:
        return self.__add_credentials_to_url(
            self.get_blog_src_url(),
            run_context.get_env(Env.GIT_USER_NAME),
            run_context.get_env(Env.GIT_TOKEN))

    @staticmethod
    def __add_credentials_to_url(url: str, user: str, password: str) -> str:
        if user is None or user == '':
            raise ValueError("User cannot be none or empty")
        if password is None or password == '':
            raise ValueError("Password cannot be none or empty")
        if url.startswith("https://"):
            return url.replace("https://", f"https://{user}:{password}@", 1)
        else:
            raise ValueError("URL must start with https://")

    @staticmethod
    def __convert_to_markdown(script_path: str,
                              src_file: str,
                              language_code: str,
                              result_if_none: Union[str, None]) -> str:
        """
        Converts a file to markdown
        Creates a directory of format "blog/YYYY/MM/DD" for the output files
        :param script_path: The script to run
        :param src_file: The file to convert to markdown
        :param result_if_none: The result to return if the output is None
        :return: The path to the markdown version of the input file
        """
        if script_path is None or script_path == '':
            raise ValueError("Script path cannot be none or empty")

        if not os.path.exists(script_path):
            raise ValueError(f"Script path does not exist: {script_path}")

        if not os.path.isfile(script_path):
            raise ValueError(f"Script path must be a file: {script_path}")

        if src_file is None or src_file == '':
            raise ValueError("Input file cannot be none or empty")

        if not src_file.endswith(".txt"):
            raise ValueError(f"Input file must end with .txt, file: {src_file}")

        args = BlogAgent._get_convert_to_markdown_args(src_file, language_code)

        found_text: str = ''
        completed_process = run_script(script_path, args, timeout=30, stdout=subprocess.PIPE)
        if completed_process.returncode == 0:
            shell_log = str(completed_process.stdout.strip())
            m = re.search(r'^Target: (.*)$', shell_log, flags=re.MULTILINE)
            if m is not None:
                found_text = m.group(1)
        return result_if_none if found_text is None or found_text == '' else found_text

    @staticmethod
    def _get_convert_to_markdown_args(src_file, language_code) -> [str]:
        if language_code:

            if len(language_code) != 2:
                raise ValueError(f"Language code must be 2 characters, code: {language_code}")

            return ['-f', f'"{src_file}"', '-p', f'"/{language_code}"']
        else:
            return ['-f', f'"{src_file}"']


    @staticmethod
    def __prepend_image_link_to_file_content(src_image_path: str, target_file: str):
        # Move cover image to the same directory as the output file
        tgt_image_name = os.path.basename(src_image_path)
        shutil.copy2(src_image_path, os.path.join(os.path.dirname(target_file), tgt_image_name))

        # Add the cover image at the top of the file
        prepend_line(target_file, f"![Video cover image](./{tgt_image_name})\n")

    def _get_update_blog_content_commands(self, run_context: RunContext) -> list[list[str]]:
        return [
            ['git', 'config', 'user.email', f'"{run_context.get_env(Env.GIT_USER_EMAIL)}"'],
            ['git', 'remote', 'set-url', 'origin',
             self.__get_blog_src_url_with_credentials(run_context)],
            ['git', 'add', '.'],
            ['git', 'commit', '-m', '"Add blog post"'],
            ['git', 'push']
        ]

    def _get_build_update_blog_image_command_args(self) -> [str]:
        return ['docker', 'build', '-t', self.get_app_docker_image_name(), '.']

    def _get_update_blog_command_args(self, run_context: RunContext) -> [str]:

        blog_env_file = run_context.get_env(Env.BLOG_ENV_FILE)

        m = re.search(r"^APP_PORT=(\d*)", read_content(blog_env_file), re.MULTILINE)
        port_str: str = None if not m else m.group(1)
        port = 8000 if not port_str else int(port_str)

        commands = ['docker', 'run', '--name', self.get_app_docker_container_name(), '--rm']

        if is_docker() is False:
            app_base_dir = os.path.join(os.getcwd(), self.get_app_base_dir())
            commands.extend(['-v', f'"{app_base_dir}/app:/blog-app"'])

        commands.extend(['--env-file', f'"{blog_env_file}"',
                         '-u', '0',
                         '-p', f'{port}:{port}',
                         '-e', f'APP_PORT={port}',
                         self.get_app_docker_image_name()])
        return commands

    def __app(self):
        return self.get_config().get('app')

    def __blog(self):
        return self.get_config().get('blog')

    def __script(self):
        return self.__app().get('script')

    def get_convert_to_markdown_script(self) -> str:
        return self.__script().get('convert-to-markdown')

    def get_docker_entrypoint_script(self) -> str:
        return self.__script().get('docker-entrypoint')

    def get_update_blog_script(self) -> str:
        return self.__script().get('update-blog')

    def get_app_base_dir(self) -> str:
        return self.__app()['base']['dir']

    def get_app_docker_container_name(self) -> str:
        return self.get_app_docker_image_name().replace('/', '-')

    def get_app_docker_image_name(self) -> str:
        return self.__app()['docker']['image']

    def get_app_src_url(self) -> str:
        return self.__app()['source']['url']

    def get_app_tgt_dir(self) -> str:
        return self.__app()['target']['dir']

    def get_blog_src_url(self) -> str:
        return self.__blog()['source']['url']

    def get_blog_tgt_dir(self) -> str:
        return self.__blog()['target']['dir']