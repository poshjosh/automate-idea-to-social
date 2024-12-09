# Run Options

```yaml
agents:
- test-log

# video input
#############################################################################
# If running in docker (usually the case)
# These can be full paths, because we are mounting their directory in docker
# They must however be contained within our DOCKER_MOUNT_CONTENT_DIR
# See environment variables for DOCKER_MOUNT_CONTENT_DIR
#############################################################################
input-dir: 
  
# Optional. Used for title and description. Either set this, or provide a title and description
video-content-file:

# Optional. Used for suffix to append to the description. If not set, description-suffix will be used
video-content-suffix-file:

# Optional. If not set, the name (without extension) of video-content-file will be used
video-title:

# Optional. If not set, the content of video-content-file will be used
video-content:
  
# Optional. If not set, the content of video-content-suffix-file will be used.
video-content-suffix: 

video-cover-image: 

# Optional. If not set, video-cover-image will be used
video-cover-image-square: 
```