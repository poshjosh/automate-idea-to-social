class AgentName:
    PICTORY: str = "pictory"
    TRANSLATION: str = "translation"
    TIKTOK: str = "tiktok"

    class PictoryStage:
        SAVE_DOWNLOADED_VIDEO: str = "save-downloaded-video"
        DOWNLOAD_VIDEO_LAYOUT_2: str = "download-video-layout-2"

        class Action:
            GET_FILE: str = "get-file"
            SAVE_FILE: str = "save-file"
