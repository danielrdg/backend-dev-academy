from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str = "roteamento_ia"

    class Config:
        env_file = ".env"

settings = Settings()
