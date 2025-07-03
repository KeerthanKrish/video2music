"""Supabase client service and utilities."""

from functools import lru_cache
from typing import AsyncGenerator

from supabase import Client, create_client

from ..config import settings


@lru_cache()
def get_supabase_client() -> Client:
    """Create and cache Supabase client instance."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


@lru_cache()
def get_supabase_admin_client() -> Client:
    """Create and cache Supabase admin client instance."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


async def get_supabase_dependency() -> AsyncGenerator[Client, None]:
    """FastAPI dependency for Supabase client."""
    client = get_supabase_client()
    try:
        yield client
    finally:
        # Cleanup if needed
        pass 