import logging

import os
from datetime import datetime
from enum import Enum, unique
from typing import Union

from .paths import Paths

logger = logging.getLogger(__name__)


@unique
class Env(str, Enum):
    def __new__(cls, value, optional: bool = False,
                path: bool = False, default_value: str = None):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.__optional = optional
        obj.__path = path
        obj.__default_value = default_value
        return obj

    def is_optional(self) -> bool:
        return self.__optional

    def is_path(self) -> bool:
        return self.__path

    def get_default_value(self) -> str:
        return self.__default_value

    APP_LANGUAGE = ('APP_LANGUAGE', True, False, 'en-GB')

    APP_PROFILES = ('APP_PROFILES', True, False, 'dev')

    CONTENT_DIR = ('CONTENT_DIR', False, True)
    CHROME_PROFILE_DIR = ('CHROME_PROFILE_DIR', True, True)

    SETUP_DISPLAY = ('SETUP_DISPLAY', True, False)

    APP_PORT = ('APP_PORT', True, False, '5001')

    WEB_APP = ('WEB_APP', True, False, 'true')

    CONFIG_DIR = ('CONFIG_DIR', True, True, 'resources/config')
    OUTPUT_DIR = ('OUTPUT_DIR', False, True, 'output')

    RUN_ARGS = ('RUN_ARGS', True, False)

    VIDEO_FILE_EXTENSION = ('VIDEO_FILE_EXTENSION', False, False, 'mp4')

    PICTORY_USER_EMAIL = 'PICTORY_USER_EMAIL'
    PICTORY_USER_PASS = 'PICTORY_USER_PASS'
    PICTORY_BRAND_NAME = 'PICTORY_BRAND_NAME'
    PICTORY_BG_MUSIC_NAME = 'PICTORY_BG_MUSIC_NAME'
    PICTORY_VOICE_NAME = 'PICTORY_VOICE_NAME'
    PICTORY_TEXT_STYLE = 'PICTORY_TEXT_STYLE'

    TRANSLATION_OUTPUT_LANGUAGE_CODES = ('TRANSLATION_OUTPUT_LANGUAGE_CODES',
                                         False, False, 'ar,bn,de,es,fr,hi,it,ja,ko,ru,tr,uk,zh')
    SUBTITLES_FILE_EXTENSION = ('SUBTITLES_FILE_EXTENSION', False, False, 'vtt')

    YOUTUBE_USER_EMAIL = 'YOUTUBE_USER_EMAIL'
    YOUTUBE_USER_PASS = 'YOUTUBE_USER_PASS'
    YOUTUBE_PLAYLIST_NAME = 'YOUTUBE_PLAYLIST_NAME'

    TIKTOK_USER_EMAIL = 'TIKTOK_USER_EMAIL'
    TIKTOK_USER_PASS = 'TIKTOK_USER_PASS'

    TWITTER_USER_EMAIL = 'TWITTER_USER_EMAIL'
    TWITTER_USER_NAME = 'TWITTER_USER_NAME'
    TWITTER_USER_PASS = 'TWITTER_USER_PASS'

    REDDIT_USER_NAME = 'REDDIT_USER_NAME'
    REDDIT_USER_PASS = 'REDDIT_USER_PASS'
    REDDIT_COMMUNITY_NAME = 'REDDIT_COMMUNITY_NAME'

    FACEBOOK_USER_EMAIL = 'FACEBOOK_USER_EMAIL'
    FACEBOOK_USER_PASS = 'FACEBOOK_USER_PASS'

    INSTAGRAM_USER_EMAIL = 'INSTAGRAM_USER_EMAIL'
    INSTAGRAM_USER_PASS = 'INSTAGRAM_USER_PASS'

    GIT_USER_NAME = 'GIT_USER_NAME'
    GIT_USER_EMAIL = 'GIT_USER_EMAIL'
    GIT_TOKEN = 'GIT_TOKEN'

    BLOG_ENV_FILE = ('BLOG_ENV_FILE', True, True)
    BLOG_APP_DIR = ('BLOG_APP_DIR', True, True)
    BLOG_APP_VERSION = ('BLOG_APP_VERSION', True, False, '0.1.6')

    @staticmethod
    def values() -> list[str]:
        return [str(Env(e).value) for e in Env]

    @staticmethod
    def set_defaults():
        for e in Env:
            default_value = Env(e).get_default_value()
            if default_value:
                Env.set_default(e, default_value)

    @staticmethod
    def set_default(k: Union[str, 'Env'], v: str):
        k = k.value if isinstance(k, Env) else k
        os.environ[k] = os.environ.get(k, v)

    @staticmethod
    def collect(add_to: dict[str, any] = None) -> dict[str, any]:
        if add_to is None:
            add_to = {}
        names = Env.values()
        for name in names:
            env = Env(name)
            value = os.environ.get(name, env.get_default_value())
            # print(f"'{name}' = '{value}' or '{env.get_default_value()}'")
            if env.is_path():
                try:
                    value = Paths.get_path(value) if env.is_optional() else Paths.require_path(value)
                except FileNotFoundError as ex:
                    logger.warning(f"The following error occurred while processing path for environment variable '{name}' = '{value}'")
                    raise ex
            add_to[name] = value
        return add_to


def get_app_language(full: bool, result_if_none: str) -> str:
    lang = get_env_value(Env.APP_LANGUAGE, result_if_none)
    return lang if full else lang.split('-')[0]


def get_app_port() -> int:
    return int(get_env_value(Env.APP_PORT))


def is_docker() -> bool:
    return 'docker' in os.environ.get('APP_PROFILES', '')


def is_production() -> bool:
    return 'prod' in os.environ.get('APP_PROFILES', '')


def is_web_app() -> bool:
    return get_env_value(Env.WEB_APP) == 'true'


def is_setup_display() -> bool:
    return get_env_value(Env.SETUP_DISPLAY) == 'true'


def get_cached_results_file(agent_name: str, filename: str = None) -> str:
    if not agent_name:
        raise ValueError('agent name required')

    now = datetime.now()

    if filename:
        filename = f'-{filename}'
    else:
        filename = ''

    dir_path: str = os.path.join(Paths.get_path(get_env_value(Env.OUTPUT_DIR)),
                                 'results',
                                 agent_name,
                                 now.strftime("%Y"),
                                 now.strftime("%m"),
                                 now.strftime("%d"))
    name_and_ext = os.path.splitext(filename)
    name = name_and_ext[0]
    suffix = ''
    ext = '' if len(name_and_ext) == 1 or not name_and_ext[1] else name_and_ext[1]
    for i in range(1000):
        if i > 0:
            suffix = f'-{i}'
        filepath = os.path.join(dir_path, f"{now.strftime('%Y-%m-%dT%H-%M-%S')}{name}{suffix}{ext}")
        if not os.path.exists(filepath):
            return filepath
    raise FileExistsError(f"File already exists: {os.path.join(dir_path, filename)}")


def get_agent_results_dir(agent_name: str) -> str:
    return os.path.join(get_agent_output_dir(agent_name), 'results')


def get_agent_output_dir(agent_name: str):
    if not agent_name:
        raise ValueError('agent name required')
    return os.path.join(get_env_value(Env.OUTPUT_DIR), 'agent', agent_name)


def has_env_value(name: str) -> bool:
    return name in Env.values() and get_env_value(name) is not None


def get_env_value(name: Union[str, Enum], default: str = None) -> Union[str, None]:
    if not name:
        return default
    if isinstance(name, Env):
        return os.environ.get(
            str(name.value), default if default is not None else name.get_default_value())
    if isinstance(name, Enum):
        return os.environ.get(str(name.value), default)
    if isinstance(name, str):
        value = os.environ.get(name)
        if value:
            return value
        if name in Env.values():
            return get_env_value(Env(name), default)
        return default
    return default


def get_cookies_file(domain: str, file_name: str = "cookies.pkl") -> str:
    dir_path = Paths.get_path(get_env_value(Env.OUTPUT_DIR), "cookies")
    return os.path.join(dir_path, domain, file_name)


def get_content_dir(sub_path=None):
    main = Paths.require_path(get_env_value(Env.CONTENT_DIR))
    return main if not sub_path else os.path.join(main, sub_path)


def get_uploads_dir():
    return get_content_dir('uploads')


def get_upload_file(task_id: str, filename: str) -> str:
    if not task_id:
        raise ValueError('task id is required')
    if not filename:
        raise ValueError('file name is required')
    now = datetime.now()
    return os.path.join(get_uploads_dir(),
                        now.strftime("%Y"),
                        now.strftime("%m"),
                        now.strftime("%d"),
                        task_id,
                        filename)
