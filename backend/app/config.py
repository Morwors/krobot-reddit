"""Application configuration."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage"))
    BACKGROUNDS_PATH: str = ""
    LOGOS_PATH: str = ""
    OUTPUT_PATH: str = ""
    TEMP_PATH: str = ""

    # TTS settings
    TTS_MODEL: str = "tts_models/en/vctk/vits"
    TTS_DEFAULT_SPEAKER: str = "p226"
    TTS_SPEED: float = 1.0

    # Video settings
    VIDEO_WIDTH: int = 1080
    VIDEO_HEIGHT: int = 1920
    VIDEO_FPS: int = 30
    VIDEO_BITRATE: str = "4M"

    # Subtitle settings
    SUBTITLE_FONT: str = "Liberation-Sans-Bold"
    SUBTITLE_FONT_SIZE: int = 48
    SUBTITLE_COLOR: str = "#FFFFFF"
    SUBTITLE_HIGHLIGHT_COLOR: str = "#FFFF00"
    SUBTITLE_BG_COLOR: str = "rgba(0,0,0,0.7)"

    class Config:
        env_file = ".env"

    def model_post_init(self, __context):
        self.BACKGROUNDS_PATH = os.path.join(self.STORAGE_PATH, "backgrounds")
        self.LOGOS_PATH = os.path.join(self.STORAGE_PATH, "logos")
        self.OUTPUT_PATH = os.path.join(self.STORAGE_PATH, "output")
        self.TEMP_PATH = os.path.join(self.STORAGE_PATH, "temp")

        for path in [self.BACKGROUNDS_PATH, self.LOGOS_PATH, self.OUTPUT_PATH, self.TEMP_PATH]:
            os.makedirs(path, exist_ok=True)


settings = Settings()
