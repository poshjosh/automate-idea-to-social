# Environment

The complete list of environment variables that can be used to configure the behavior of the application.

```dotenv
################################################################################################
# All paths which start with a / are absolute paths and a dir thereof must be mounted in docker.
# All non-absolute paths are relative to the application's working dir.
################################################################################################

# docker
# default value is: latest
APP_VERSION=[OPTIONAL]
APP_LANGUAGE=en-GB
DOCKER_MOUNT_CONTENT_DIR=
DOCKER_MOUNT_BROWSER_PROFILE_DIR=
# This is needed if we want to user undetected chromedriver with display.
# If we don't set this, we get error: cannot connect to chrome at 127.0.0.1:
# https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/743#issuecomment-1420119272
SETUP_DISPLAY=true

# agents
AGENTS=[OPTIONAL]

OUTPUT_DIR=resources/output

# video input
# VIDEO_CONTENT_FILE is used for title and description.
# VIDEO_INPUT_FILE is used to generate the video.
VIDEO_CONTENT_FILE=
# Optional. If not set, the name (without extension) of VIDEO_CONTENT_FILE will be used
VIDEO_TITLE=[OPTIONAL]
# Optional. If not set, the content of VIDEO_CONTENT_FILE will be used
VIDEO_DESCRIPTION=[OPTIONAL]
# Optional. If not set, VIDEO_CONTENT_FILE is used
VIDEO_INPUT_FILE=[OPTIONAL]
# Optional. If not set, the content of VIDEO_INPUT_FILE will be used
VIDEO_INPUT_TEXT=[OPTIONAL]
VIDEO_COVER_IMAGE=
# Optional. If not set, VIDEO_COVER_IMAGE will be used
VIDEO_COVER_IMAGE_SQUARE=[OPTIONAL]

# video output
VIDEO_OUTPUT_TYPE=mp4

# pictory
PICTORY_USER_EMAIL=
PICTORY_USER_PASS=
PICTORY_BRAND_NAME=
PICTORY_BG_MUSIC_NAME=
PICTORY_VOICE_NAME=
PICTORY_TEXT_STYLE=

# translation
#TRANSLATION_OUTPUT_LANGUAGES=
TRANSLATION_FILE_EXTENSION=vtt

# youtube
YOUTUBE_USER_EMAIL=
YOUTUBE_USER_PASS=
YOUTUBE_PLAYLIST_NAME=

# tiktok
TIKTOK_USER_EMAIL=
TIKTOK_USER_PASS=

# twitter
TWITTER_USER_EMAIL=
TWITTER_USER_NAME=
TWITTER_USER_PASS=

# reddit
REDDIT_USER_NAME=
REDDIT_USER_PASS=
REDDIT_COMMUNITY_NAME=

# facebook
FACEBOOK_USER_EMAIL=
FACEBOOK_USER_PASS=

# instagram
INSTAGRAM_USER_EMAIL=
INSTAGRAM_USER_PASS=

# git
GIT_USER_NAME=
GIT_USER_EMAIL=
GIT_TOKEN=

# blog
# The environment file to use for blog updater app
BLOG_ENV_FILE=
BLOG_APP_DIR=
```