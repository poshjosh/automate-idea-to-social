import os
from enum import Enum, unique
from typing import Union

_video = 'video'
_pictory = 'pictory'
_translation = 'translation'
_youtube = 'youtube'
_tiktok = 'tiktok'
_twitter = 'twitter'
_reddit = 'reddit'
_facebook = 'facebook'
_instagram = 'instagram'
_github = 'github'
_blog = 'blog'
_browser_chrome = 'browser.chrome'


@unique
class Env(str, Enum):
    def __new__(cls, value, optional: bool = False, path: bool = False):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.__optional = optional
        obj.__path = path
        return obj

    @property
    def value(self) -> str:
        return self._value_

    def is_optional(self) -> bool:
        return self.__optional

    def is_path(self) -> bool:
        return self.__path

    AGENTS_DIR = ('agents.dir', False, True)
    # video.content.file is used for title and description.
    VIDEO_CONTENT_FILE = (f'{_video}.content.file', True, True)
    # video.input.file is used to generate the video.
    VIDEO_INPUT_FILE = (f'{_video}.input.file', False, True)
    VIDEO_INPUT_TEXT = (f'{_video}.input.text', True)
    VIDEO_TILE = (f'{_video}.title', True)
    VIDEO_DESCRIPTION = (f'{_video}.description', True)
    VIDEO_OUTPUT_DIR = (f'{_video}.output.dir', False, True)
    VIDEO_OUTPUT_TYPE = f'{_video}.output.type'
    VIDEO_COVER_IMAGE = (f'{_video}.cover.image', False, True)
    VIDEO_COVER_IMAGE_SQUARE = (f'{_video}.cover.image.square', True, True)

    PICTORY_USER_NAME = f'{_pictory}.user.name'
    PICTORY_USER_PASS = f'{_pictory}.user.pass'
    PICTORY_BRAND_NAME = f'{_pictory}.brand.name'
    PICTORY_BG_MUSIC_NAME = f'{_pictory}.bg-music.name'
    PICTORY_VOICE_NAME = f'{_pictory}.voice.name'

    TRANSLATION_OUTPUT_LANGUAGES = f'{_translation}.output.languages'
    TRANSLATION_FILE_EXTENSION = f'{_translation}.file.extension'

    YOUTUBE_USER_EMAIL = f'{_youtube}.user.email'
    YOUTUBE_USER_PASS = f'{_youtube}.user.pass'
    YOUTUBE_PLAYLIST_NAME = f'{_youtube}.playlist.name'

    TIKTOK_USER_NAME = f'{_tiktok}.user.name'
    TIKTOK_USER_PASS = f'{_tiktok}.user.pass'

    TWITTER_USER_EMAIL = f'{_twitter}.user.email'
    TWITTER_USER_NAME = f'{_twitter}.user.name'
    TWITTER_USER_PASS = f'{_twitter}.user.pass'

    REDDIT_USER_NAME = f'{_reddit}.user.name'
    REDDIT_USER_PASS = f'{_reddit}.user.pass'
    REDDIT_COMMUNITY_NAME = f'{_reddit}.community.name'

    FACEBOOK_USER_NAME = f'{_facebook}.user.name'
    FACEBOOK_USER_PASS = f'{_facebook}.user.pass'

    INSTAGRAM_USER_NAME = f'{_instagram}.user.name'
    INSTAGRAM_USER_PASS = f'{_instagram}.user.pass'

    GITHUB_USER_NAME = f'{_github}.user.name'
    GITHUB_TOKEN = f'{_github}.token'

    BLOG_ENV_FILE = (f'{_blog}.env.file', False, True)
    BLOG_APP_DIR = (f'{_blog}.app.dir', False, True)

    BROWSER_CHROME_EXECUTABLE_PATH = (f'{_browser_chrome}.executable-path', False, True)
    BROWSER_CHROME_OPTIONS_ARGS_USER_DATA_DIR = \
        (f'{_browser_chrome}.options.args.user-data-dir', True, True)
    BROWSER_CHROME_OPTIONS_ARGS_PROFILE_DIRECTORY = \
        (f'{_browser_chrome}.options.args.profile-directory', True)

    @staticmethod
    def values():
        return [Env(e).value for e in Env]

    @staticmethod
    def collect(add_to: dict[str, any] = None) -> dict[str, any]:
        all_env_names: [str] = Env.values()
        if add_to is None:
            add_to = {}
        for k, v in os.environ.items():
            if k in all_env_names:
                env = Env(k)
                if env.is_path():
                    add_to[k] = get_path(k) if env.is_optional() else require_path(k)
                else:
                    add_to[k] = v

        return add_to


def get_value(env: Union[str, Env], default: any = None) -> any:
    return os.environ.get(env.value if isinstance(env, Env) else env, default)


def get_video_file() -> str:
    return get_path(Env.VIDEO_CONTENT_FILE, default=require_path(Env.VIDEO_INPUT_FILE))


def get_cookies_file_path(domain: str, file_name: str = "cookies.pkl") -> str:
    dir_path = get_path(Env.AGENTS_DIR, domain)
    return os.path.join(dir_path, file_name)


def get_path(env: Union[str, Env], extra: str = None, default: any = None) -> any:
    path = get_value(env, default)
    if not path:
        return default
    return os.path.join(os.getcwd(), path) if not extra \
        else os.path.join(os.getcwd(), path, extra)


def require_path(env: Union[str, Env]):
    path = get_value(env)
    if not path:
        raise ValueError(f'Value required for: {env}')
    path = os.path.join(os.getcwd(), path)
    if not os.path.exists(path):
        raise FileNotFoundError(f'File not found: {path}')
    return path
