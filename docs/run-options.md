# Run Options

```yaml
# Name of agents to run
# Possible values: [pictory, translation, subtitles-translation, youtube, blog, twitter, facebook, instagram, tiktok, reddit]
agents:

# input
#############################################################################
# If running in docker (usually the case)
# These can be full paths, because we are mounting their directory in docker
# They must however be contained within our CONTENT_DIR
# See environment variables for CONTENT_DIR
#############################################################################
# Comma separated list of language codes e.g. en,de,fr
language-codes: en

# Optional. Used for title and description. Either set this, or provide a text-title and text-content
text-file: 

# Optional. If not set, the name (without extension) of text-file will be used
text-title:

# Optional. If not set, the content of text-file will be used
text-content:

image-file-landscape: 

# Optional. If not set, image-file-landscape will be used
image-file-square:

video-file-landscape:
  
video-file-portrait:
  
video-file-square:  

# Optional. If cover image should be shared when multiple translations of one post is being made.
share-cover-image:

input-language-code: en

subtitles-file:
  
browser_visible: false

continue-on-error: false
```