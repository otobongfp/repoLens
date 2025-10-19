# RepoLens API - Auth Endpoints
# Authentication API routes
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models.user import User
from app.services.auth_service import auth_service


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Authentication failed"}},
)

security = HTTPBearer()


# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    username: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_verified: bool
    role: str
    tenant_id: str


class OAuthUrlResponse(BaseModel):
    authorization_url: str


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = auth_service.verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post(
    "/register",
    response_model=TokenResponse,
    summary="Register New User",
    description="""""",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Invalid registration data"},
        409: {"description": "User already exists"},
    },
)
async def register_user(
    user_data: UserRegister, request: Request, db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Password validation temporarily disabled
    # from app.services.auth_service import validate_password
    # is_valid, error_msg = validate_password(user_data.password)
    # if not is_valid:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f"Password validation failed: {error_msg}",
    #     )

    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    # Create new user
    user = await auth_service.create_user(
        db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        username=user_data.username,
    )

    # Create session and tokens using Redis
    session_data = await auth_service.create_user_session(
        db,
        user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return TokenResponse(
        access_token=session_data["access_token"],
        refresh_token=session_data["refresh_token"],
        token_type=session_data["token_type"],
        expires_in=session_data["expires_in"],
        user=session_data["user"],
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login User",
    description="Authenticate user and return tokens",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login_user(
    user_data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)
):
    """Login user with email and password"""
    user = await auth_service.authenticate_user(db, user_data.email, user_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    await auth_service.update_user_last_login(db, str(user.id))

    # Create session and tokens using Redis
    session_data = await auth_service.create_user_session(
        db,
        user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return TokenResponse(
        access_token=session_data["access_token"],
        refresh_token=session_data["refresh_token"],
        token_type=session_data["token_type"],
        expires_in=session_data["expires_in"],
        user=session_data["user"],
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Token",
    description="Refresh access token using refresh token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid refresh token"},
    },
)
async def refresh_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """Refresh access token using Redis"""
    # Use Redis-based refresh token validation
    refresh_data = await auth_service.refresh_access_token(request.refresh_token)

    if not refresh_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    return TokenResponse(
        access_token=refresh_data["access_token"],
        refresh_token=request.refresh_token,  # Keep the same refresh token
        token_type=refresh_data["token_type"],
        expires_in=refresh_data["expires_in"],
        user={},  # User data not needed for refresh
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get current user information",
    responses={
        200: {"description": "User information retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user information"""
    # Get user's tenant_id
    from sqlalchemy import select

    from app.database.models.tenant import TenantMember

    result = await db.execute(
        select(TenantMember).where(TenantMember.user_id == current_user.id)
    )
    membership = result.scalars().first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User has no tenant membership",
        )

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        is_verified=current_user.is_verified,
        role=current_user.role,
        tenant_id=str(membership.tenant_id),
    )


@router.post(
    "/logout",
    summary="Logout User",
    description="Logout user and revoke session",
    responses={
        200: {"description": "Logout successful"},
        401: {"description": "Authentication required"},
    },
)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Logout user and revoke session"""
    token = credentials.credentials
    payload = auth_service.verify_token(token)

    if payload:
        user_id = payload.get("sub")
        if user_id:
            await auth_service.revoke_all_user_sessions(db, user_id)

    return {"message": "Successfully logged out"}


# OAuth endpoints
@router.get(
    "/oauth/google",
    response_model=OAuthUrlResponse,
    summary="Google OAuth",
    description="Get Google OAuth authorization URL",
    responses={
        200: {"description": "OAuth URL generated successfully"},
        503: {"description": "Google OAuth not configured"},
    },
)
async def get_google_oauth_url():
    """Get Google OAuth authorization URL"""
    url = await auth_service.get_google_authorization_url()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )

    return OAuthUrlResponse(authorization_url=url)


@router.get(
    "/oauth/github",
    response_model=OAuthUrlResponse,
    summary="GitHub OAuth",
    description="Get GitHub OAuth authorization URL",
    responses={
        200: {"description": "OAuth URL generated successfully"},
        503: {"description": "GitHub OAuth not configured"},
    },
)
async def get_github_oauth_url():
    """Get GitHub OAuth authorization URL"""
    url = await auth_service.get_github_authorization_url()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured",
        )

    return OAuthUrlResponse(authorization_url=url)


@router.post(
    "/oauth/google/callback",
    response_model=TokenResponse,
    summary="Google OAuth Callback",
    description="Handle Google OAuth callback",
    responses={
        200: {"description": "OAuth authentication successful"},
        400: {"description": "Invalid OAuth code"},
        503: {"description": "Google OAuth not configured"},
    },
)
async def handle_google_callback(
    code: str, request: Request, db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback"""
    user = await auth_service.handle_google_callback(db, code)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google",
        )

    # Create session
    session = await auth_service.create_user_session(
        db,
        user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Create tokens
    access_token = auth_service.create_access_token({"sub": str(user.id)})
    refresh_token = auth_service.create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60,  # 30 minutes
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "is_verified": user.is_verified,
            "role": user.role,
        },
    )


@router.post(
    "/oauth/github/callback",
    response_model=TokenResponse,
    summary="GitHub OAuth Callback",
    description="""""",
    responses={
        400: {"description": "Invalid OAuth code"},
        503: {"description": "GitHub OAuth not configured"},
    },
)
async def handle_github_callback(
    code: str, request: Request, db: AsyncSession = Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    user = await auth_service.handle_github_callback(db, code)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with GitHub",
        )

    # Create session
    session = await auth_service.create_user_session(
        db,
        user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Create tokens
    access_token = auth_service.create_access_token({"sub": str(user.id)})
    refresh_token = auth_service.create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60,  # 30 minutes
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "is_verified": user.is_verified,
            "role": user.role,
        },
    )
