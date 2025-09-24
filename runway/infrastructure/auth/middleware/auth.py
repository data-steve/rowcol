from fastapi import Request, status, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import jwt
import os
from typing import Optional
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for JWT token validation"""
    
    # Routes that don't require authentication
    EXEMPT_ROUTES = {
        "/",
        "/docs",
        "/openapi.json",
        "/runway/auth/login",
        "/runway/auth/register",
        "/health",
        "/static"
    }

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for exempt routes
        if self._is_exempt_route(request.url.path):
            return await call_next(request)
        
        # Extract and validate token
        token = self._extract_token(request)
        if not token:
            return self._unauthorized_response("Missing authentication token")
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            business_id = payload.get("business_id")
            
            if not user_id:
                return self._unauthorized_response("Invalid token payload")
            
            # Add user context to request state
            request.state.user_id = user_id
            request.state.business_id = business_id
            request.state.token_payload = payload
            
        except jwt.ExpiredSignatureError:
            return self._unauthorized_response("Token has expired")
        except jwt.InvalidTokenError:
            return self._unauthorized_response("Invalid token")
        
        return await call_next(request)
    
    def _is_exempt_route(self, path: str) -> bool:
        """Check if route is exempt from authentication"""
        return any(path.startswith(exempt) for exempt in self.EXEMPT_ROUTES)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from Authorization header"""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None
    
    def _unauthorized_response(self, detail: str) -> Response:
        """Return unauthorized response"""
        return Response(
            content=f'{{"detail": "{detail}"}}',
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"Content-Type": "application/json"}
        )

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """Create JWT access token"""
    import datetime
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_delta)
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None

# Dependency functions for FastAPI routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # For now, return a simple user object with business_id
    # In a real implementation, you'd fetch from database
    return {
        "user_id": payload.get("user_id"),
        "business_id": payload.get("business_id"),
        "email": payload.get("email")
    }

def get_current_business_id(current_user: dict = Depends(get_current_user)) -> str:
    """Get current business ID from authenticated user"""
    if not current_user.get("business_id"):
        raise HTTPException(status_code=403, detail="No business access")
    return current_user["business_id"]
