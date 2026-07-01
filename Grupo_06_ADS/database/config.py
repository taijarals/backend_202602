"""Database configuration and connection management."""
import os
from typing import Optional
from supabase import create_client, Client
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "EduGame Platform"
    app_version: str = "1.0.0"
    debug: bool = True

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    vite_supabase_url: str = ""
    vite_supabase_anon_key: str = ""

    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    api_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def effective_supabase_url(self) -> str:
        return self.supabase_url or self.vite_supabase_url

    @property
    def effective_supabase_anon_key(self) -> str:
        return self.supabase_anon_key or self.vite_supabase_anon_key


settings = Settings()


class DatabaseConnection:
    """Singleton database connection manager."""
    _instance: Optional['DatabaseConnection'] = None
    _client: Optional[Client] = None
    _admin_client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_client(cls) -> Client:
        """Get Supabase client with anon key."""
        if cls._client is None:
            cls._client = create_client(
                settings.effective_supabase_url,
                settings.effective_supabase_anon_key
            )
        return cls._client

    @classmethod
    def get_admin_client(cls) -> Client:
        """Get Supabase client with service role key for admin operations."""
        if cls._admin_client is None:
            anon_key = settings.effective_supabase_anon_key
            cls._admin_client = create_client(
                settings.effective_supabase_url,
                settings.supabase_service_role_key or anon_key
            )
        return cls._admin_client


def get_db() -> Client:
    """Dependency to get database client."""
    return DatabaseConnection.get_client()


def get_admin_db() -> Client:
    """Get admin database client."""
    return DatabaseConnection.get_admin_client()
