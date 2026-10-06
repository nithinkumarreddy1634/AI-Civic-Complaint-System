from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = 'CivicAI'
    DEBUG: bool = True
    SECRET_KEY: str = 'change_this_to_a_secure_random_string'
    ALLOWED_ORIGINS: str = 'http://localhost:5173'
    DATABASE_URL: str = 'sqlite:///./civicai.db'
    JWT_SECRET_KEY: str = 'change_this_to_a_secure_jwt_secret'
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = './uploads'
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = 'jpg,jpeg,png'
    AI_MODEL_PATH: str = './ml/models/best.pt'
    AI_CONFIDENCE_THRESHOLD: float = 0.5

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]

    @property
    def allowed_extensions_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(',')]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

@lru_cache
def get_settings() -> Settings:
    return Settings()
