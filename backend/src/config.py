from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = 'RS256'
    access_token_expire_minutes: int = 360
    refresh_token_expire_days: int = 30
    # verify_token_expire_minutes: int = 15
    key_cookie: str = 'Auth-refresh'

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_ENDPOINTPUT: str
    S3_REGION: str
    S3_PRIVATE_BUCKET_NAME: str

    REDIS_USER_PASSWORD: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_EXP: int

    auth_jwt: AuthJWT = AuthJWT()

    model_config = SettingsConfigDict(env_file=".env")

    def DATABASE_URL(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    @property
    def DATABASE_URL_alembic(self):
        return (f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    @property
    def REDIS_BASE_URL(self) -> str:
        return f"redis://:{self.REDIS_USER_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"


settings = Settings()
