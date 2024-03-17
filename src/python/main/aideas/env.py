import os
from enum import Enum, unique

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
class Env(Enum):
    AGENTS_DIR = 'agents.dir'

    VIDEO_INPUT_FILE = f'{_video}.input.file'
    VIDEO_TILE = f'{_video}.title'
    VIDEO_DESCRIPTION = f'{_video}.description'
    VIDEO_OUTPUT_DIR = f'{_video}.output.dir'
    VIDEO_OUTPUT_TYPE = f'{_video}.output.type'
    VIDEO_COVER_IMAGE = f'{_video}.cover.image'
    VIDEO_COVER_IMAGE_SQUARE = f'{_video}.cover.image.square'

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

    BLOG_ENV_FILE = f'{_blog}.env.file'

    BROWSER_CHROME_EXECUTABLE_PATH = f'{_browser_chrome}.executable-path'
    BROWSER_CHROME_OPTIONS_ARGS_USER_DATA_DIR = f'{_browser_chrome}.options.args.user-data-dir'
    BROWSER_CHROME_OPTIONS_ARGS_PROFILE_DIRECTORY = \
        f'{_browser_chrome}.options.args.profile-directory'

    @staticmethod
    def paths() -> list['Env']:
        return [
            Env.AGENTS_DIR,
            Env.VIDEO_INPUT_FILE,
            Env.VIDEO_OUTPUT_DIR,
            Env.VIDEO_COVER_IMAGE,
            Env.VIDEO_COVER_IMAGE_SQUARE,
            Env.BLOG_ENV_FILE,
            Env.BROWSER_CHROME_EXECUTABLE_PATH,
            Env.BROWSER_CHROME_OPTIONS_ARGS_USER_DATA_DIR
        ]

    @staticmethod
    def collect(add_to: dict[str, any] = None) -> dict[str, any]:
        all_env_names: [str] = [e.value for e in Env]
        path_env_names: [str] = [e.value for e in Env.paths()]
        if add_to is None:
            add_to = {}
        for k, v in os.environ.items():
            if k in path_env_names:
                add_to[k] = Env.__require_path(k)
            elif k in all_env_names:
                add_to[k] = v

        return add_to

    @staticmethod
    def get_value(env: 'Env', default: any = None) -> any:
        return os.environ.get(env.value, default)

    @staticmethod
    def get_path(env: 'Env', extra: str = None, default: any = None) -> any:
        path = Env.get_value(env)
        if not path:
            return default
        return os.path.join(os.getcwd(), path) if not extra \
            else os.path.join(os.getcwd(), path, extra)

    @staticmethod
    def require_path(env: 'Env'):
        return Env.__require_path(env.value)

    @staticmethod
    def __require_path(env_key: str):
        path = os.environ[env_key]
        path = os.path.join(os.getcwd(), path)
        if not path:
            raise ValueError(f'Not found: {path}')
        return path
