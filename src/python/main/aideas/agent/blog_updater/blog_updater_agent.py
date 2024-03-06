import logging
import os
import subprocess
import tempfile
import uuid
import zipfile

from ..agent import Agent
from ...agent.agent_name import AgentName
from ...action.action import Action
from ...action.action_result import ActionResult
from ...config.name import Name
from ...io.net import download_file
from ...io.file import extract_zip_file
from ...result.element_result_set import ElementResultSet
from ...env import Env
from ...run_context import RunContext



logger = logging.getLogger(__name__)


class BlogUpdaterAgent(Agent):
    @staticmethod
    def of_config(agent_config: dict[str, any]) -> 'BlogUpdaterAgent':
        return BlogUpdaterAgent(agent_config)

    def __init__(self, agent_config: dict[str, any]):
        super().__init__(AgentName.TRANSLATION, agent_config)

    def run_stage(self,
                  run_context: RunContext,
                  stage_name: Name) -> ElementResultSet:
        #file_type = stages_config[stage_name.value]['file-type']
        #dir_path: str = run_context.get_arg(Env.VIDEO_OUTPUT_DIR.value)
        subprocess.run(['mkdir', '-p', 'output'])

        stage_config = self.get_stage_config(stage_name.value)
        if stage_name == AgentName.BlogUpdaterStage.DOWNLOAD_SOURCE:
            self.download_source(run_context)
        return run_context.get_element_results(self.get_name(), stage_name.alias)

    def download_source(self, run_context: RunContext) -> ActionResult:
        url: str = run_context.get_arg(Env.BLOG_UPDATER_SRC_URL.value)
        save_to_dir: str = run_context.get_arg(Env.BLOG_UPDATER_DIR.value)
        temp_file = os.path.join(tempfile.gettempdir(), f'{self.get_name()}-{uuid.uuid4().hex}')
        success: bool = download_file(url, temp_file)
        if success:
            success = extract_zip_file(temp_file, save_to_dir, True)
        action = Action.of_generic(
            AgentName.BLOG_UPDATER, AgentName.BlogUpdaterStage.DOWNLOAD_SOURCE)
        return ActionResult(action, success, save_to_dir)

