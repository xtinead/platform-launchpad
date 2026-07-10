import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Platform Launchpad API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://platform_user:platform_pass@localhost:5432/platform_launchpad"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_to_a_long_random_secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


settings = Settings()
