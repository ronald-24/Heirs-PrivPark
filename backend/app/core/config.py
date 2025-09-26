from functools import lru_cache
from typing import List

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()  # Chargement du fichier .env

firebaseConfig = {
    "apiKey": "AIzaSyCzIVVnmyYerQxNtpDAXHYGInMTsOrPEF4",
    "authDomain": "heirsprivpark.firebaseapp.com",
    "projectId": "heirsprivpark",
    "storageBucket": "heirsprivpark.firebasestorage.app",
    "messagingSenderId": "788141115039",
    "appId": "1:788141115039:web:4709d890fa30b54d1ec4aa",
    "measurementId": "G-6EW6TF2SMC",
    "databaseURL": "postgresql+psycopg://postgres:123456789@localhost:5432/privpark"
}


def _parse_cors(origins_raw: str | None) -> List[str]:
    if not origins_raw or origins_raw.strip() == "*":
        return ["*"]
    # Handle comma-separated values
    return [o.strip() for o in origins_raw.split(",") if o.strip()]


class Settings(BaseSettings):
    env: str = os.getenv("ENV", "dev")
    project_name: str = os.getenv("PROJECT_NAME", "HeirsPrivPark")
    api_prefix: str = os.getenv("API_PREFIX", "/api")
    docs_url: str = os.getenv("DOCS_URL", "/docs")
    # PostgreSQL par défaut; surcharge possible via .env
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/privpark",
    )
    firebase_project_id: str | None = os.getenv("FIREBASE_PROJECT_ID")
    firebase_credentials_path: str | None = os.getenv(
        "FIREBASE_CREDENTIALS_PATH")
    firebase_config: dict = os.getenv("FIREBASE_CONFIG", firebaseConfig)
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    # AWS S3
    aws_s3_bucket: str | None = os.getenv("AWS_S3_BUCKET")
    aws_s3_region: str | None = os.getenv("AWS_S3_REGION")
    aws_access_key_id: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")

    class Config:
        env_file = "backend/.env"
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
