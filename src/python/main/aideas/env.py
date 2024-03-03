import os
from enum import Enum


class Env(Enum):
    __agent = 'agent'
    AGENT_DIR = f'{__agent}.dir'

    __video = 'video'
    VIDEO_INPUT_FILE = f'{__video}.input.file'
    VIDEO_TILE = f'{__video}.title'
    VIDEO_DESCRIPTION = f'{__video}.description'
    VIDEO_OUTPUT_DIR = f'{__video}.output.dir'
    VIDEO_OUTPUT_TYPE = f'{__video}.output.type'
    VIDEO_COVER_IMAGE = f'{__video}.cover.image'
    VIDEO_COVER_IMAGE_SQUARE = f'{__video}.cover.image.square'
    VIDEO_LINK = f'{__video}.link'

    __pictory = 'pictory'
    PICTORY_USER_NAME = f'{__pictory}.user.name'
    PICTORY_USER_PASS = f'{__pictory}.user.pass'

    __translation = 'translation'
    TRANSLATION_OUTPUT_LANGUAGES = f'{__translation}.output.languages'

    __tiktok = 'tiktok'
    TIKTOK_USER_NAME = f'{__tiktok}.user.name'
    TIKTOK_USER_PASS = f'{__tiktok}.user.pass'

    __twitter = 'twitter'
    TWITTER_USER_EMAIL = f'{__twitter}.user.email'
    TWITTER_USER_NAME = f'{__twitter}.user.name'
    TWITTER_USER_PASS = f'{__twitter}.user.pass'

    __reddit = 'reddit'
    REDDIT_USER_NAME = f'{__reddit}.user.name'
    REDDIT_USER_PASS = f'{__reddit}.user.pass'

    __facebook = 'facebook'
    FACEBOOK_USER_NAME = f'{__facebook}.user.name'
    FACEBOOK_USER_PASS = f'{__facebook}.user.pass'

    __instagram = 'instagram'
    INSTAGRAM_USER_NAME = f'{__instagram}.user.name'
    INSTAGRAM_USER_PASS = f'{__instagram}.user.pass'

    @staticmethod
    def collect(add_to: dict[str, any] = None) -> dict[str, any]:
        env_names: [str] = [e.value for e in Env]
        if add_to is None:
            add_to = {}
        for k, v in os.environ.items():
            if k in env_names:
                add_to[k] = v
        return add_to
