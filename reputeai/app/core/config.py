from pydantic import BaseSettings


class Settings(BaseSettings):
    db_url: str
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = 3600
    stripe_secret_key: str | None = None
    stripe_public_key: str | None = None
    openai_api_key: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
