import os
from ...main.aideas.env import Env

print(f"{__name__}     - - - INITIALIZING TEST ENVIRONMENT - - -")
__env_names: [str] = [e.value for e in Env]
for env_name in __env_names:
    os.environ[env_name] = f'test-{env_name}'
__user_home = '/Users/chinomso/dev_chinomso'
__app_home = f'{__user_home}/automate-idea-to-social'
__test_resources_dir = f'{__app_home}/src/python/test/resources'
__test_pictory_dir = f'{__test_resources_dir}/agent/pictory'
os.environ[Env.VIDEO_INPUT_FILE.value] = f'{__test_pictory_dir}/content.txt'
os.environ[Env.VIDEO_COVER_IMAGE.value] = f'{__test_pictory_dir}/cover.jpg'
os.environ[Env.VIDEO_COVER_IMAGE_SQUARE.value] = f'{__test_pictory_dir}/cover-square.jpg'
os.environ[Env.VIDEO_OUTPUT_DIR.value] = f'{__test_resources_dir}/downloads'
os.environ[Env.VIDEO_OUTPUT_TYPE.value] = 'mp4'
os.environ[Env.TRANSLATION_OUTPUT_LANGUAGES.value] = "ar,de,zh"
os.environ[Env.BLOG_UPDATER_ENV_FILE.value] = f'{__app_home}/blog_updater.env'
print(f"{__name__} - - - DONE INITIALIZING TEST ENVIRONMENT - - -")
