from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Blooming API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"


settings = Settings()
