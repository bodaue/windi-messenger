from typing import Annotated

from pydantic import SecretStr, Field, BaseModel
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL


class BaseConfig(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class PostgresConfig(BaseConfig, env_prefix="POSTGRES_"):
    host: str
    port: Annotated[int, Field(gt=0, lt=65536)]
    user: str
    password: SecretStr
    db: str

    def build_dsn(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=str(self.host),
            port=self.port,
            database=self.db,
        )


class JWTConfig(BaseConfig, env_prefix="JWT_"):
    secret_key: SecretStr
    algorithm: str
    access_token_expires_minutes: int


class Config(BaseModel):
    postgres: PostgresConfig
    jwt: JWTConfig


def create_config() -> Config:
    return Config(postgres=PostgresConfig(), jwt=JWTConfig())


config = create_config()
