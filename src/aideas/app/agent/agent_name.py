class AgentName:
    BLOG: str = "blog"
    FACEBOOK: str = "facebook"
    INSTAGRAM: str = "instagram"
    PICTORY: str = "pictory"
    REDDIT: str = "reddit"
    REDDIT_API: str = "reddit-api"
    SUBTITLES_TRANSLATION: str = "subtitles-translation"
    TIKTOK: str = "tiktok"
    TRANSLATION: str = "translation"
    TWITTER: str = "twitter"
    TWITTER_API: str = "twitter-api"
    YOUTUBE: str = "youtube"
    YOUTUBE_API: str = "youtube-api"

    class PictoryStage:
        VIDEO_LANDSCAPE: str = "video-landscape"
        VIDEO_PORTRAIT: str = "video-portrait"

        class Action:
            GET_FILE: str = "get-file"
            SAVE_FILE: str = "save-file"

    class BlogUpdaterStage:
        DOWNLOAD_APP: str = "download-app"
        CLONE_BLOG: str = "clone-blog"
        CONVERT_TO_MARKDOWN: str = "convert-to-markdown"
        UPDATE_BLOG_CONTENT: str = "update-blog-content"
        UPDATE_BLOG: str = "update-blog"
