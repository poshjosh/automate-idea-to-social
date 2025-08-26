# Environment

The complete list of environment variables that can be used to configure the behavior of the application.

```dotenv
################################################################################################
# All paths which start with a / are absolute paths and a dir thereof must be mounted in docker.
# All non-absolute paths are relative to the application's working dir.
################################################################################################

APP_PROFILES=[prod|dev|test|docker]

# docker
# default value is: latest
APP_VERSION=[OPTIONAL]
APP_LANGUAGE=en-GB
# This is needed if we want to user undetected chromedriver with display.
# If we don't set this, we get error: cannot connect to chrome at 127.0.0.1:
# https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/743#issuecomment-1420119272
SETUP_DISPLAY=true

# Used when WEB_APP=true
APP_PORT=5001

WEB_APP="[OPTIONAL, default = true]

# Path to a directory containing additional configuation 
EXTERNAL_CONFIG_DIR="[OPTIONAL]"
CONTENT_DIR="[default = '~/.aideas/content']"
# This is required when running in docker
OUTPUT_DIR="[default = '~/.aideas/output']"
#########################################################################
# If you use a dir on the host machine, make sure the version of chrome 
# on the host machine is compatible with the one in the docker container.
#########################################################################
CHROME_PROFILE_DIR=[OPTIONAL]

# Space separated args to run each agent, usually presented as options to be provided by the user.
# See aideas.app.config.RunArg for possible values.
RUN_ARGS=[OPTIONAL]

# video output
VIDEO_FILE_EXTENSION=mp4

# pictory
PICTORY_USER_EMAIL=
PICTORY_USER_PASS=
PICTORY_BRAND_NAME=
PICTORY_BG_MUSIC_NAME=
PICTORY_VOICE_NAME=
PICTORY_TEXT_STYLE=

# translation
SUBTITLES_FILE_EXTENSION=vtt
TRANSLATION_OUTPUT_LANGUAGE_CODES=

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
```