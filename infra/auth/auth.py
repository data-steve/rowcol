from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

class LoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class LoginResponse(BaseModel):
    """Response schema for successful login"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: Dict[str, Any]
    business: Optional[Dict[str, Any]] = None

class TokenRefreshRequest(BaseModel):
    """Request schema for token refresh"""
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    """Response schema for token refresh"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class RegisterRequest(BaseModel):
    """Request schema for user registration"""
    email: EmailStr
    password: str
    confirm_password: str
    business_name: str
    user_role: Optional[str] = "owner"
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class PasswordResetRequest(BaseModel):
    """Request schema for password reset"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Request schema for password reset confirmation"""
    token: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return user info from token payload (no database lookup to avoid circular imports)
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role"),
        "business_id": payload.get("business_id")
    }

def get_current_business_id(
    current_user: dict = Depends(get_current_user)
) -> str:
    """Get current business ID from authenticated user"""
    return current_user["business_id"]

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for FastAPI"""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/login",
            "/auth/register",
            "/auth/password-reset",
            "/static"
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip auth for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                content='{"detail": "Missing or invalid authorization header"}',
                status_code=401,
                media_type="application/json"
            )
        
        # Extract token
        token = auth_header.split(" ")[1]
        
        # Verify token
        payload = verify_token(token)
        if payload is None:
            return Response(
                content='{"detail": "Invalid token"}',
                status_code=401,
                media_type="application/json"
            )
        
        # Add user info to request state
        request.state.user_id = payload.get("sub")
        request.state.business_id = payload.get("business_id")
        request.state.user_email = payload.get("email")
        request.state.user_role = payload.get("role")
        
        return await call_next(request)
