# Run Options

```yaml
agents:
- test-log

# video input
#############################################################################
# If running in docker (usually the case)
# These can be full paths, because we are mounting their directory in docker
# They must however be contained within our CONTENT_DIR
# See environment variables for CONTENT_DIR
#############################################################################
# Optional. Used for title and description. Either set this, or provide a title and description
video-content-file:

# Optional. If not set, the name (without extension) of video-content-file will be used
video-title:

# Optional. If not set, the content of video-content-file will be used
video-content:

image-file: 

# Optional. If not set, image-file will be used
image-file-square: 
```