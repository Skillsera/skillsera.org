from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql://skillsera:skillsera@localhost/skillsera"
    secret_key: str = "dev-secret-key-change-in-production"
    auth_server_url: str = "https://auth.skillsera.org"
    cors_origins: str = "https://skillsera.org,https://api.skillsera.org"
    debug: bool = False


settings = Settings()
