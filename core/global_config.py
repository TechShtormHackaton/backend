import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))


class Settings(BaseSettings):
    database_host: str = Field(..., validation_alias="DATABASE_HOST")
    database_user: str = Field(..., validation_alias="DATABASE_USER")
    database_password: str = Field(..., validation_alias="DATABASE_PASSWORD")
    database_name: str = Field(..., validation_alias="DATABASE_NAME")
    database_port: int = Field(..., validation_alias="DATABASE_PORT")

    @property
    def database_uri(self) -> str:
        return (f'postgresql+asyncpg://{self.database_user}:{self.database_password}@{self.database_host}'
                f':{self.database_port}/{self.database_name}')

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


settings = Settings(_env_file=f"{BASE_DIR}/.env", _env_file_encoding='utf-8')
