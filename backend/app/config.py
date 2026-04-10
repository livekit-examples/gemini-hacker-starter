from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    livekit_url: str = ""
    livekit_api_key: str = ""
    livekit_api_secret: str = ""
    google_api_key: str = ""
    realtime_model: str = "gemini-2.5-flash-native-audio-latest"
    realtime_voice: str = "Aoede"
    default_language: str = "en"
    default_industry: str = "hackathon"


settings = Settings()
