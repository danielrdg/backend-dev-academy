from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Carrega .env e ignora variáveis extras (por exemplo OPENAI_API_KEY, GOOGLE_API_KEY)
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    MONGO_URI: str
    MONGO_DB: str = "roteamento_ia"

settings = Settings()
