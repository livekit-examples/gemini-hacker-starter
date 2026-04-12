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
    agent_name: str = "gemini-hackathon-agent"
    default_language: str = "en"
    default_industry: str = "hackathon"
    silence_timeout_seconds: float = 45.0
    silence_check_interval_seconds: float = 1.0
    silence_audio_level_threshold: float = 0.02


settings = Settings()
