# Run Options

```yaml
# Name of agents to run
# Possible values: [pictory, translation, subtitles-translation, youtube, blog, twitter, facebook, instagram, tiktok, reddit]
agents:

# input

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

subtitles-file:

# Optional. If cover image should be shared when multiple translations of one post is being made.
share-cover-image:
  
# Optional. Possible values: visible|undetected
browser-mode: 

continue-on-error: false

# Possible values: always|never|onerror|onfailure|onsuccess|onstart
# always and never are exclusive. The rest may be combined with each other.
save-screens: onerror

input-language-code: en

language-codes:
  - ar
  - bn
  - de
  - en
  - es
  - fr
  - hi
  - it
  - ja
  - ko
  - ru
  - tr
  - uk
  - zh
  - zh-TW
```