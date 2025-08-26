try:
    from pydantic_settings import BaseSettings
except Exception:  # pragma: no cover - fallback for missing package
    from pydantic import BaseModel as BaseSettings  # type: ignore


class Settings(BaseSettings):
    db_url: str = "sqlite:///./test.db"
    redis_url: str = "redis://localhost:6379/0"
    frontend_url: str = "http://localhost:3000"

    # Auth configuration
    jwt_private_key: str = (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIBUwIBADANBgkqhkiG9w0BAQEFAASCAT0wggE5AgEAAkEAtWd1ags663Bo/pr7\n"
        "a6p2pz/P3sN5w4BtxCtneKwJpmdrS4FwGcRUs3bnB3ISHVJQEOu1ynPzLrwWRnQI\n"
        "rMUtswIDAQABAkAlW0DaraVchrGYfOH5sgjtOD7eaPLSR8hS9X1BZGw4UAre9asm\n"
        "gfNKS6fhAPYxp91Y781UlfTPmFW6FA1JKfRBAiEA5fKFHOxmykbSu3dUCZmLtgqv\n"
        "FdfHdrrvAntaw4kyBXUCIQDJ9PkZIUfOep9F4PvA1viLvqpfOEOZ8CMra510iZB5\n"
        "hwIgURFUTqMlhhC8AK2MKipA8DgKDBhb0QcMdoKIuEEpKnUCIEAB300iqiJ75Kz+\n"
        "EGxe9ak8xbymFW7dmBfz5JSB4QNTAiAsASXJra6RqeELr/6lBj3+zymTWDJtjNNJ\n"
        "QsbIqN5/QQ==\n"
        "-----END PRIVATE KEY-----"
    )
    jwt_public_key: str = (
        "-----BEGIN PUBLIC KEY-----\n"
        "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBALVndWoLOutwaP6a+2uqdqc/z97DecOA\n"
        "bcQrZ3isCaZna0uBcBnEVLN25wdyEh1SUBDrtcpz8y68FkZ0CKzFLbMCAwEAAQ==\n"
        "-----END PUBLIC KEY-----"
    )
    jwt_algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    use_cookies: bool = True

    stripe_secret_key: str | None = None
    stripe_public_key: str | None = None
    openai_api_key: str | None = None
    openai_model: str = "gpt-3.5-turbo"
    oauth_encryption_key: str = "dev_secret_key"

    class Config:
        env_file = ".env"


settings = Settings()
