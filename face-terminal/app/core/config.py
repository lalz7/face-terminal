# face-terminal/app/core/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = "Face Terminal"
    DEBUG: bool = bool(int(os.getenv("DEBUG", "1")))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:password@localhost/face_terminal"
    )

settings = Settings()
