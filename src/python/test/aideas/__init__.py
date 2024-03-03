import os
from ...main.aideas.env import Env

#print("XX XX XX INITIALIZING TEST ENVIRONMENT XX XX XX")
__env_names: [str] = [e.value for e in Env]
for env_name in __env_names:
    os.environ[env_name] = f'test-{env_name}'
__pictory_dir = 'python/main/resources/agent/pictory'
os.environ[Env.VIDEO_INPUT_FILE.value] = f'{__pictory_dir}/Spread love not hate.txt'
os.environ[Env.VIDEO_COVER_IMAGE.value] = f'{__pictory_dir}/cover.jpeg'
os.environ[Env.VIDEO_COVER_IMAGE_SQUARE.value] = f'{__pictory_dir}/cover.jpeg'
os.environ[Env.VIDEO_OUTPUT_TYPE.value] = 'mp4'
os.environ[Env.TRANSLATION_OUTPUT_LANGUAGES.value] = "ar,de,zh"
