import logging
from enum import unique
from typing import Union

from content_publisher.app.app import App
from content_publisher.app.content_publisher import Content, SocialPlatformType
from content_publisher.app.run_arg import RunArg as PublisherArg

from ..action.action import Action
from ..action.action_handler import ActionHandler, BaseActionId
from ..action.action_result import ActionResult
from ..run_context import RunContext
from ..config import RunArg


logger = logging.getLogger(__name__)


@unique
class ContentPublisherActionId(BaseActionId):
    PUBLISH = ('publish', True)

class ContentPublisherActionHandler(ActionHandler):
    @staticmethod
    def get_supported_platforms() -> list[str]:
        return [SocialPlatformType.YOUTUBE.value, SocialPlatformType.X.value,
                SocialPlatformType.FACEBOOK.value, SocialPlatformType.REDDIT.value]

    @staticmethod
    def to_action_id(action: str) -> BaseActionId:
        try:
            return ActionHandler.to_action_id(action)
        except ValueError:
            return ContentPublisherActionId(action)

    def _execute_by_key(self, run_context: RunContext, action: Action, key: str) -> ActionResult:
        if key == ContentPublisherActionId.PUBLISH.value:
            result = self.publish(run_context, action)
        else:
            return super()._execute_by_key(run_context, action, key)
        logger.debug(f'{result}')
        return result

    def publish(self, run_context: RunContext, action: Action) -> ActionResult:
        args: dict[PublisherArg, any] = PublisherArg.of_list({}, action.get_args())
        platforms = run_context.get_arg("platforms", args.get(PublisherArg.PLATFORMS, None))
        if not platforms:
            return ActionResult.failure(action, "No platforms specified")
        if isinstance(platforms, str):
            platforms: list[str] = platforms.split(",")

        content: Content = self.__to_content(run_context, args)
        logger.debug(f"Publishing to platforms: {platforms}, content:\n{content}")

        result = App().publish_content(platforms, content)

        return ActionResult.success(action, result)

    @staticmethod
    def __to_content(run_context: RunContext, args: dict[str, PublisherArg]) -> Content:
        dir_path = args.get(PublisherArg.DIR, None)
        text_title: Union[str, None] = args.get(PublisherArg.TEXT_TITLE, run_context.get_arg(RunArg.TEXT_TITLE))
        media_orientation = args.get(PublisherArg.MEDIA_ORIENTATION, "square")

        if dir_path:
            return Content.of_dir(dir_path, text_title, media_orientation)
        else:

            def media_file_arg(media_type: str) -> RunArg:
                return RunArg(f"{media_type}-file-{media_orientation}")

            description: str = run_context.get_arg(RunArg.TEXT_CONTENT)
            video_file: Union[str, None] = run_context.get_arg(media_file_arg("video"))
            image_file: Union[str, None] = run_context.get_arg(media_file_arg("image"))
            subtitle_files: Union[dict[str, str], None] = run_context.get_arg(RunArg.SUBTITLES_FILE)

            return Content(description, video_file, image_file, text_title, subtitle_files)




