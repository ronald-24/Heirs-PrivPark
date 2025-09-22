from functools import lru_cache
from typing import List
from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
import json

# Charger le fichier .env
load_dotenv(dotenv_path=".env")

firebaseConfig = {
  "apiKey": "AIzaSyCzIVVnmyYerQxNtpDAXHYGInMTsOrPEF4",
  "authDomain": "heirsprivpark.firebaseapp.com",
  "projectId": "heirsprivpark",
  "storageBucket": "heirsprivpark.firebasestorage.app",
  "messagingSenderId": "788141115039",
  "appId": "1:788141115039:web:4709d890fa30b54d1ec4aa",
  "measurementId": "G-6EW6TF2SMC",
  "databaseURL": "postgresql+psycopg://postgres:admin123@localhost:5432/privpark"
}

class Settings(BaseSettings):
    env: str = os.getenv("ENV", "dev")
    project_name: str = os.getenv("PROJECT_NAME", "HeirsPrivPark")
    api_prefix: str = os.getenv("API_PREFIX", "/api")
    docs_url: str = os.getenv("DOCS_URL", "/docs")

    # Charger DATABASE_URL depuis .env
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:admin123@localhost:5432/privpark",
    )

    firebase_project_id: str | None = os.getenv("FIREBASE_PROJECT_ID")
    firebase_credentials_path: str | None = os.getenv("FIREBASE_CREDENTIALS_PATH")

    # Si FIREBASE_CONFIG existe dans .env, le parser en dict
    firebase_config: dict = json.loads(os.getenv("FIREBASE_CONFIG", "null")) if os.getenv("FIREBASE_CONFIG") else firebaseConfig

    cors_origins: str = os.getenv("CORS_ORIGINS", "*")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator('cors_origins')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @computed_field  # type: ignore[misc]
    @property
    def is_dev(self) -> bool:
        return (self.env or "").lower() in {"dev", "development", "local"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
