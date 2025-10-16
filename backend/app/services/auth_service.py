# RepoLens Service - Auth_Service Business Logic
#
# Copyright (C) 2024 RepoLens Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Authentication service with OAuth support
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from authlib.integrations.httpx_client import AsyncOAuth2Client
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.github import GitHubOAuth2
import secrets
import logging

from app.core.config import settings
from app.database.models.user import User, UserAuthProvider, UserSession, AuthProvider, UserRole
from app.database.models.tenant import Tenant, TenantMember, TenantMemberRole
from app.services.session_manager import session_manager

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        
        # Initialize OAuth clients
        self.google_client = None
        self.github_client = None
        
        if settings.google_client_id and settings.google_client_secret:
            self.google_client = GoogleOAuth2(
                settings.google_client_id,
                settings.google_client_secret
            )
        
        if settings.github_client_id and settings.github_client_secret:
            self.github_client = GitHubOAuth2(
                settings.github_client_id,
                settings.github_client_secret
            )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None
    
    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user or not user.hashed_password:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(self, db: AsyncSession, email: str, password: Optional[str] = None, 
                         full_name: Optional[str] = None, username: Optional[str] = None) -> User:
        """Create a new user"""
        hashed_password = None
        if password:
            hashed_password = self.get_password_hash(password)
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            username=username,
            is_active=True,
            is_verified=False,
            role=UserRole.USER
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Create default tenant for the user
        await self.create_default_tenant(db, user)
        
        return user
    
    async def create_default_tenant(self, db: AsyncSession, user: User) -> Tenant:
        """Create a default tenant for a new user"""
        tenant = Tenant(
            name=f"{user.full_name or user.email}'s Workspace",
            slug=f"user-{user.id}",
            plan="free"
        )
        
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        
        # Add user as owner of the tenant
        member = TenantMember(
            tenant_id=tenant.id,
            user_id=user.id,
            role=TenantMemberRole.OWNER
        )
        
        db.add(member)
        await db.commit()
        
        return tenant
    
    async def create_user_session(self, db: AsyncSession, user: User, ip_address: Optional[str] = None, 
                                 user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user session with Redis"""
        session_data = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        
        # Create session in Redis
        session_id = await session_manager.create_session(
            str(user.id), 
            session_data,
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )
        
        # Create tokens
        access_token = self.create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "session_id": session_id
        })
        
        refresh_token = await session_manager.create_refresh_token(
            str(user.id), 
            settings.jwt_refresh_token_expire_days * 24 * 60 * 60
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60,
            "session_id": session_id,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "is_verified": user.is_verified,
                "role": user.role
            }
        }
    
    async def get_user_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user by session ID from Redis"""
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            return None
        
        return {
            "id": session_data.get("user_id"),
            "email": session_data.get("email"),
            "role": session_data.get("role"),
            "is_verified": session_data.get("is_verified"),
            "session_id": session_id
        }
    
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a user session in Redis"""
        return await session_manager.delete_session(session_id)
    
    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user in Redis"""
        return await session_manager.delete_user_sessions(user_id)
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh an access token using refresh token from Redis"""
        user_id = await session_manager.validate_refresh_token(refresh_token)
        if not user_id:
            return None
        
        # Create new access token
        access_token = self.create_access_token({
            "sub": user_id,
            "type": "access"
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60
        }
    
    async def logout_user(self, session_id: str, refresh_token: str) -> bool:
        """Logout a user by invalidating their session and refresh token"""
        try:
            # Delete session from Redis
            await session_manager.delete_session(session_id)
            
            # Delete refresh token from Redis
            await session_manager.delete_refresh_token(refresh_token)
            
            logger.info(f"User logged out successfully")
            return True
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics from Redis"""
        return await session_manager.get_session_stats()
    
    async def update_user_last_login(self, db: AsyncSession, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if user:
                user.last_login = datetime.now(timezone.utc)
                await db.commit()
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
            return False
    
    # OAuth methods
    async def get_google_authorization_url(self) -> Optional[str]:
        """Get Google OAuth authorization URL"""
        if not self.google_client:
            return None
        
        return await self.google_client.get_authorization_url(
            redirect_uri=f"{settings.frontend_url}/auth/callback/google",
            scope=["openid", "email", "profile"]
        )
    
    async def get_github_authorization_url(self) -> Optional[str]:
        """Get GitHub OAuth authorization URL"""
        if not self.github_client:
            return None
        
        return await self.github_client.get_authorization_url(
            redirect_uri=f"{settings.frontend_url}/auth/callback/github",
            scope=["user:email"]
        )
    
    async def handle_google_callback(self, db: AsyncSession, code: str) -> Optional[User]:
        """Handle Google OAuth callback"""
        if not self.google_client:
            return None
        
        try:
            token = await self.google_client.get_access_token(code)
            user_info = await self.google_client.get_id_email(token["access_token"])
            
            # Get or create user
            user = await self.get_user_by_email(db, user_info["email"])
            if not user:
                user = await self.create_user(
                    db,
                    email=user_info["email"],
                    full_name=user_info.get("name"),
                    username=user_info.get("name", "").replace(" ", "_").lower()
                )
            
            # Create or update auth provider
            await self.create_or_update_auth_provider(
                db, user, AuthProvider.GOOGLE, user_info["id"], token
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Google OAuth error: {e}")
            return None
    
    async def handle_github_callback(self, db: AsyncSession, code: str) -> Optional[User]:
        """Handle GitHub OAuth callback"""
        if not self.github_client:
            return None
        
        try:
            token = await self.github_client.get_access_token(code)
            user_info = await self.github_client.get_id_email(token["access_token"])
            
            # Get or create user
            user = await self.get_user_by_email(db, user_info["email"])
            if not user:
                user = await self.create_user(
                    db,
                    email=user_info["email"],
                    full_name=user_info.get("name"),
                    username=user_info.get("login")
                )
            
            # Create or update auth provider
            await self.create_or_update_auth_provider(
                db, user, AuthProvider.GITHUB, user_info["id"], token
            )
            
            return user
            
        except Exception as e:
            logger.error(f"GitHub OAuth error: {e}")
            return None
    
    async def create_or_update_auth_provider(self, db: AsyncSession, user: User, 
                                           provider: AuthProvider, provider_user_id: str, 
                                           token: Dict[str, Any]) -> UserAuthProvider:
        """Create or update OAuth provider information"""
        result = await db.execute(
            select(UserAuthProvider).where(
                UserAuthProvider.user_id == user.id,
                UserAuthProvider.provider == provider
            )
        )
        auth_provider = result.scalar_one_or_none()
        
        if auth_provider:
            auth_provider.provider_user_id = provider_user_id
            auth_provider.access_token = token.get("access_token")
            auth_provider.refresh_token = token.get("refresh_token")
            auth_provider.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=token.get("expires_in", 3600))
        else:
            auth_provider = UserAuthProvider(
                user_id=user.id,
                provider=provider,
                provider_user_id=provider_user_id,
                access_token=token.get("access_token"),
                refresh_token=token.get("refresh_token"),
                token_expires_at=datetime.now(timezone.utc) + timedelta(seconds=token.get("expires_in", 3600))
            )
            db.add(auth_provider)
        
        await db.commit()
        await db.refresh(auth_provider)
        return auth_provider

# Global auth service instance
auth_service = AuthService()
