import os
from ...main.aideas.env import Env

__env_names: [str] = Env.values()
for env_name in __env_names:
    os.environ[env_name] = f'test-{env_name}'
__user_home = '/Users/chinomso/dev_chinomso'
__app_home = f'{__user_home}/automate-idea-to-social'
__test_resources_dir = f'{__app_home}/src/python/test/resources'
__test_downloads_dir = f'{__test_resources_dir}/downloads'
__test_content_dir = f'{__test_downloads_dir}/days-of-signs-and-wonders'
os.environ[Env.VIDEO_INPUT_FILE.value] = f'{__test_content_dir}/content.txt'
os.environ[Env.VIDEO_CONTENT_FILE.value] = f'{__test_content_dir}/content.txt'
os.environ[Env.VIDEO_COVER_IMAGE.value] = f'{__test_content_dir}/cover.jpg'
os.environ[Env.VIDEO_COVER_IMAGE_SQUARE.value] = f'{__test_content_dir}/cover-square.jpg'
os.environ[Env.VIDEO_OUTPUT_DIR.value] = __test_downloads_dir
os.environ[Env.VIDEO_OUTPUT_TYPE.value] = 'mp4'
os.environ[Env.BLOG_ENV_FILE.value] = f'{__app_home}/blog.env'
os.environ[Env.BLOG_APP_DIR.value] = f'{__app_home}/src/downloads'

os.environ[Env.TRANSLATION_OUTPUT_LANGUAGES.value] = "ar,de,zh"

del os.environ[Env.BROWSER_CHROME_EXECUTABLE_PATH.value]
del os.environ[Env.BROWSER_CHROME_OPTIONS_ARGS_USER_DATA_DIR.value]
del os.environ[Env.BROWSER_CHROME_OPTIONS_ARGS_PROFILE_DIRECTORY.value]
