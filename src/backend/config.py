from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URL: str = "mongodb://admin:password123@localhost:27017"
    MONGO_DB_NAME: str = 'voc_analytics'
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()