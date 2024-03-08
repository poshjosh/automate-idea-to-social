import os
from enum import Enum

_agent = 'agent'
_video = 'video'
_pictory = 'pictory'
_translation = 'translation'
_tiktok = 'tiktok'
_twitter = 'twitter'
_reddit = 'reddit'
_facebook = 'facebook'
_instagram = 'instagram'
_github = 'github'
_blog = 'blog'


class Env(Enum):
    AGENT_DIR = f'{_agent}.dir'

    VIDEO_INPUT_FILE = f'{_video}.input.file'
    VIDEO_TILE = f'{_video}.title'
    VIDEO_DESCRIPTION = f'{_video}.description'
    VIDEO_OUTPUT_DIR = f'{_video}.output.dir'
    VIDEO_OUTPUT_TYPE = f'{_video}.output.type'
    VIDEO_COVER_IMAGE = f'{_video}.cover.image'
    VIDEO_COVER_IMAGE_SQUARE = f'{_video}.cover.image.square'
    VIDEO_LINK = f'{_video}.link'

    PICTORY_USER_NAME = f'{_pictory}.user.name'
    PICTORY_USER_PASS = f'{_pictory}.user.pass'

    TRANSLATION_OUTPUT_LANGUAGES = f'{_translation}.output.languages'

    TIKTOK_USER_NAME = f'{_tiktok}.user.name'
    TIKTOK_USER_PASS = f'{_tiktok}.user.pass'

    TWITTER_USER_EMAIL = f'{_twitter}.user.email'
    TWITTER_USER_NAME = f'{_twitter}.user.name'
    TWITTER_USER_PASS = f'{_twitter}.user.pass'

    REDDIT_USER_NAME = f'{_reddit}.user.name'
    REDDIT_USER_PASS = f'{_reddit}.user.pass'

    FACEBOOK_USER_NAME = f'{_facebook}.user.name'
    FACEBOOK_USER_PASS = f'{_facebook}.user.pass'

    INSTAGRAM_USER_NAME = f'{_instagram}.user.name'
    INSTAGRAM_USER_PASS = f'{_instagram}.user.pass'

    GITHUB_USER_NAME = f'{_github}.user.name'
    GITHUB_TOKEN = f'{_github}.token'

    BLOG_ENV_FILE = f'{_blog}.env.file'

    @staticmethod
    def collect(add_to: dict[str, any] = None) -> dict[str, any]:
        env_names: [str] = [e.value for e in Env]
        if add_to is None:
            add_to = {}
        for k, v in os.environ.items():
            if k in env_names:
                add_to[k] = v
        return add_to
