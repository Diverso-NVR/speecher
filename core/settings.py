from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    common_words: str = Field(..., env="COMMON")
    creds_path: str = Field(..., env="CREDS_PATH")
    token_path: str = Field(..., env="TOKEN_PATH")
    erudite_api_key: str = Field(..., env="ERUDITE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings(_env_file="../.env")
