"""Authentication middleware and utilities."""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.supabase_client import supabase_service

logger = logging.getLogger(__name__)

# Security scheme for FastAPI
security = HTTPBearer()

class AuthenticationError(Exception):
    """Custom authentication error."""
    pass

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Authenticate with Supabase
        user = await supabase_service.authenticate_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"User authenticated: {user.get('id')}")
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get the current user (doesn't raise if not authenticated).
    
    Args:
        credentials: HTTP Bearer token credentials (optional)
        
    Returns:
        User information dictionary or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
    except Exception as e:
        logger.warning(f"Optional authentication failed: {e}")
        return None

def require_user_access(user: Dict[str, Any], resource_user_id: str) -> None:
    """
    Ensure the authenticated user has access to a resource.
    
    Args:
        user: Current authenticated user
        resource_user_id: User ID that owns the resource
        
    Raises:
        HTTPException: If user doesn't have access
    """
    if user.get("id") != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions"
        ) 