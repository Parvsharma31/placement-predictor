from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    MODEL_PATH: str = "ml/model.pkl"
    MODEL_VERSION: str = "1.0.0"
    APP_TITLE: str = "Student Placement Prediction API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
