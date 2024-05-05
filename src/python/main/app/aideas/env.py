import os
from enum import Enum, unique
from typing import Union

_video = 'VIDEO'
_pictory = 'PICTORY'
_translation = 'TRANSLATION'
_youtube = 'YOUTUBE'
_tiktok = 'TIKTOK'
_twitter = 'TWITTER'
_reddit = 'REDDIT'
_facebook = 'FACEBOOK'
_instagram = 'INSTAGRAM'
_git = 'GIT'
_blog = 'BLOG'
_browser_chrome = 'BROWSER_CHROME'

_DEFAULT_OUTPUT_LANGUAGES = [
    "ar", "bn", "de", "es", "fr", "hi", "it", "ja", "ko", "ru", "zh", "zh-TW"]


@unique
class Env(str, Enum):
    def __new__(cls, value, optional: bool = False, path: bool = False):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.__optional = optional
        obj.__path = path
        return obj

    def is_optional(self) -> bool:
        return self.__optional

    def is_path(self) -> bool:
        return self.__path

    SETUP_DISPLAY = ('SETUP_DISPLAY', True, False)

    AGENTS = ('AGENTS', True, False)

    OUTPUT_DIR = ('OUTPUT_DIR', False, True)

    # VIDEO_CONTENT_FILE is used for title and description.
    VIDEO_CONTENT_FILE = (f'{_video}_CONTENT_FILE', True, True)
    # VIDEO_INPUT_FILE is used to generate the video.
    VIDEO_INPUT_FILE = (f'{_video}_INPUT_FILE', False, True)
    VIDEO_INPUT_TEXT = (f'{_video}_INPUT_TEXT', True)
    VIDEO_TILE = (f'{_video}_TITLE', True)
    VIDEO_DESCRIPTION = (f'{_video}_DESCRIPTION', True)
    VIDEO_OUTPUT_TYPE = f'{_video}_OUTPUT_TYPE'
    VIDEO_COVER_IMAGE = (f'{_video}_COVER_IMAGE', False, True)
    VIDEO_COVER_IMAGE_SQUARE = (f'{_video}_COVER_IMAGE_SQUARE', True, True)

    PICTORY_USER_EMAIL = f'{_pictory}_USER_EMAIL'
    PICTORY_USER_PASS = f'{_pictory}_USER_PASS'
    PICTORY_BRAND_NAME = f'{_pictory}_BRAND_NAME'
    PICTORY_BG_MUSIC_NAME = f'{_pictory}_BG_MUSIC_NAME'
    PICTORY_VOICE_NAME = f'{_pictory}_VOICE_NAME'
    PICTORY_TEXT_STYLE = f'{_pictory}_TEXT_STYLE'

    TRANSLATION_OUTPUT_LANGUAGES = f'{_translation}_OUTPUT_LANGUAGES'
    TRANSLATION_FILE_EXTENSION = f'{_translation}_FILE_EXTENSION'

    YOUTUBE_USER_EMAIL = f'{_youtube}_USER_EMAIL'
    YOUTUBE_USER_PASS = f'{_youtube}_USER_PASS'
    YOUTUBE_PLAYLIST_NAME = f'{_youtube}_PLAYLIST_NAME'

    TIKTOK_USER_EMAIL = f'{_tiktok}_USER_EMAIL'
    TIKTOK_USER_PASS = f'{_tiktok}_USER_PASS'

    TWITTER_USER_EMAIL = f'{_twitter}_USER_EMAIL'
    TWITTER_USER_NAME = f'{_twitter}_USER_NAME'
    TWITTER_USER_PASS = f'{_twitter}_USER_PASS'

    REDDIT_USER_NAME = f'{_reddit}_USER_NAME'
    REDDIT_USER_PASS = f'{_reddit}_USER_PASS'
    REDDIT_COMMUNITY_NAME = f'{_reddit}_COMMUNITY_NAME'

    FACEBOOK_USER_EMAIL = f'{_facebook}_USER_EMAIL'
    FACEBOOK_USER_PASS = f'{_facebook}_USER_PASS'

    INSTAGRAM_USER_EMAIL = f'{_instagram}_USER_EMAIL'
    INSTAGRAM_USER_PASS = f'{_instagram}_USER_PASS'

    GIT_USER_NAME = f'{_git}_USER_NAME'
    GIT_USER_EMAIL = f'{_git}_USER_EMAIL'
    GIT_TOKEN = f'{_git}_TOKEN'

    BLOG_ENV_FILE = (f'{_blog}_ENV_FILE', False, True)
    BLOG_APP_DIR = (f'{_blog}_APP_DIR', False, True)

    @staticmethod
    def values():
        return [Env(e).value for e in Env]

    @staticmethod
    def load(app_name: Union[str, None] = None) -> dict[str, any]:
        result = {Env.TRANSLATION_OUTPUT_LANGUAGES.value: ','.join(_DEFAULT_OUTPUT_LANGUAGES)}

        if app_name:
            result.update({'app.name': app_name})

        def read_file(file_path: str):
            with open(file_path) as file:
                return file.read()

        result.update(Env.__collect())

        if not result.get(Env.VIDEO_INPUT_TEXT.value):
            result[Env.VIDEO_INPUT_TEXT.value] = read_file(require_path(Env.VIDEO_INPUT_FILE))

        video_content_file = get_video_file()
        result[Env.VIDEO_CONTENT_FILE.value] = video_content_file

        if not result.get(Env.VIDEO_TILE.value):
            result[Env.VIDEO_TILE.value] = os.path.basename(video_content_file).split('.')[0]

        if not result.get(Env.VIDEO_DESCRIPTION.value):
            result[Env.VIDEO_DESCRIPTION.value] = read_file(video_content_file)

        if not result.get(Env.VIDEO_COVER_IMAGE_SQUARE.value):
            result[Env.VIDEO_COVER_IMAGE_SQUARE.value] = result.get(Env.VIDEO_COVER_IMAGE.value)

        return result

    @staticmethod
    def __collect(add_to: dict[str, any] = None) -> dict[str, any]:
        all_env_names: [str] = Env.values()
        if add_to is None:
            add_to = {}
        for k, v in os.environ.items():
            if k in all_env_names:
                env = Env(k)
                if env.is_path():
                    v = get_path(k) if env.is_optional() else require_path(k)
                add_to[k] = v

        return add_to


def is_docker() -> bool:
    return 'docker' in os.environ.get('PROFILES', '')


def get_cached_results_dir(agent_name: str) -> str:
    if not agent_name:
        raise ValueError('agent name required')
    return os.path.join(get_value(Env.OUTPUT_DIR), 'results', agent_name)


def get_agent_results_dir(agent_name: str) -> str:
    return os.path.join(get_agent_output_dir(agent_name), 'results')


def get_agent_output_dir(agent_name: str):
    if not agent_name:
        raise ValueError('agent name required')
    return os.path.join(get_value(Env.OUTPUT_DIR), 'agent', agent_name)


def get_value(env: Union[str, Env], default: any = None) -> any:
    return os.environ.get(env.value if isinstance(env, Env) else env, default)


def get_video_file() -> str:
    return get_path(Env.VIDEO_CONTENT_FILE, default=require_path(Env.VIDEO_INPUT_FILE))


def get_cookies_file_path(domain: str, file_name: str = "cookies.pkl") -> str:
    dir_path = get_path(Env.OUTPUT_DIR, "cookies")
    return os.path.join(dir_path, domain, file_name)


def get_path(env: Union[str, Env], extra: str = None, default: any = None) -> any:
    path = get_value(env, default)
    if not path:
        return default
    return __explicit(path) if not extra else os.path.join(__explicit(path), extra)


def require_path(env: Union[str, Env]):
    path = get_value(env)
    if not path:
        raise ValueError(f'Value required for: {env}')
    path = __explicit(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f'File not found: {path}')
    return path


def __explicit(path: str) -> str:
    explicit: bool = path.startswith('/') or path.startswith('.')
    return path if explicit else os.path.join(os.getcwd(), path)


def get_content_file_path(file_name: str):
    return os.path.join(os.path.dirname(get_path(Env.VIDEO_CONTENT_FILE)), file_name)
