import os
from ....main.app.aideas.env import Env

from .test_functions import get_test_path

__env_names: [str] = Env.values()
for env_name in __env_names:
    os.environ[env_name] = f'test-{env_name}'

__user_home = '/Users/chinomso/dev_chinomso'
__app_home = f'{__user_home}/automate-idea-to-social'
__output_dir = get_test_path('resources/output')
__test_content_dir = f'{__app_home}/src/{__output_dir}/test-content'

os.environ[Env.OUTPUT_DIR.value] = __output_dir
os.environ[Env.VIDEO_INPUT_FILE.value] = f'{__test_content_dir}/content.txt'
os.environ[Env.VIDEO_CONTENT_FILE.value] = f'{__test_content_dir}/content.txt'
os.environ[Env.VIDEO_COVER_IMAGE.value] = f'{__test_content_dir}/cover.jpg'
os.environ[Env.VIDEO_COVER_IMAGE_SQUARE.value] = f'{__test_content_dir}/cover-square.jpg'
os.environ[Env.VIDEO_OUTPUT_TYPE.value] = 'mp4'
os.environ[Env.BLOG_ENV_FILE.value] = f'{__output_dir}/blog-app/blog.env'
os.environ[Env.BLOG_APP_DIR.value] = f'{__output_dir}/blog-app'

os.environ[Env.TRANSLATION_OUTPUT_LANGUAGES.value] = "ar,de,zh"

del os.environ[Env.BROWSER_CHROME_EXECUTABLE_PATH.value]
del os.environ[Env.BROWSER_CHROME_OPTIONS_USERDATA_DIR.value]
del os.environ[Env.BROWSER_CHROME_OPTIONS_PROFILE_DIR.value]
