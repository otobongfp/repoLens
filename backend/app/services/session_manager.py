# Redis-based session management
import redis.asyncio as redis
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisSessionManager:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.session_prefix = "session:"
        self.refresh_prefix = "refresh:"
        self.user_sessions_prefix = "user_sessions:"

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()

    async def create_session(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        expires_in: int = 3600,  # 1 hour
    ) -> str:
        """Create a new session"""
        if not self.redis_client:
            await self.connect()

        session_id = str(uuid.uuid4())
        session_key = f"{self.session_prefix}{session_id}"

        session_data.update(
            {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat(),
            }
        )

        await self.redis_client.setex(session_key, expires_in, json.dumps(session_data))

        # Track user sessions
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis_client.sadd(user_sessions_key, session_id)
        await self.redis_client.expire(user_sessions_key, expires_in)

        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        if not self.redis_client:
            await self.connect()

        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis_client.get(session_key)

        if session_data:
            # Update last accessed time
            session_dict = json.loads(session_data)
            session_dict["last_accessed"] = datetime.utcnow().isoformat()
            await self.redis_client.setex(
                session_key,
                await self.redis_client.ttl(session_key),
                json.dumps(session_dict),
            )
            return session_dict

        return None

    async def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        if not self.redis_client:
            await self.connect()

        session_key = f"{self.session_prefix}{session_id}"
        existing_data = await self.redis_client.get(session_key)

        if existing_data:
            session_dict = json.loads(existing_data)
            session_dict.update(data)
            session_dict["last_accessed"] = datetime.utcnow().isoformat()

            ttl = await self.redis_client.ttl(session_key)
            await self.redis_client.setex(session_key, ttl, json.dumps(session_dict))
            return True

        return False

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if not self.redis_client:
            await self.connect()

        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis_client.get(session_key)

        if session_data:
            session_dict = json.loads(session_data)
            user_id = session_dict.get("user_id")

            # Remove from Redis
            await self.redis_client.delete(session_key)

            # Remove from user sessions set
            if user_id:
                user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
                await self.redis_client.srem(user_sessions_key, session_id)

            logger.info(f"Deleted session {session_id}")
            return True

        return False

    async def delete_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user"""
        if not self.redis_client:
            await self.connect()

        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        session_ids = await self.redis_client.smembers(user_sessions_key)

        deleted_count = 0
        for session_id in session_ids:
            if await self.delete_session(session_id):
                deleted_count += 1

        logger.info(f"Deleted {deleted_count} sessions for user {user_id}")
        return deleted_count

    async def create_refresh_token(
        self, user_id: str, expires_in: int = 604800  # 7 days
    ) -> str:
        """Create a refresh token"""
        if not self.redis_client:
            await self.connect()

        refresh_token = str(uuid.uuid4())
        refresh_key = f"{self.refresh_prefix}{refresh_token}"

        refresh_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (
                datetime.utcnow() + timedelta(seconds=expires_in)
            ).isoformat(),
        }

        await self.redis_client.setex(refresh_key, expires_in, json.dumps(refresh_data))

        logger.info(f"Created refresh token for user {user_id}")
        return refresh_token

    async def validate_refresh_token(self, refresh_token: str) -> Optional[str]:
        """Validate refresh token and return user_id"""
        if not self.redis_client:
            await self.connect()

        refresh_key = f"{self.refresh_prefix}{refresh_token}"
        refresh_data = await self.redis_client.get(refresh_key)

        if refresh_data:
            refresh_dict = json.loads(refresh_data)
            return refresh_dict.get("user_id")

        return None

    async def delete_refresh_token(self, refresh_token: str) -> bool:
        """Delete a refresh token"""
        if not self.redis_client:
            await self.connect()

        refresh_key = f"{self.refresh_prefix}{refresh_token}"
        result = await self.redis_client.delete(refresh_key)

        if result:
            logger.info(f"Deleted refresh token")
            return True

        return False

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (Redis handles this automatically, but useful for monitoring)"""
        if not self.redis_client:
            await self.connect()

        # Get all session keys
        session_keys = await self.redis_client.keys(f"{self.session_prefix}*")
        expired_count = 0

        for key in session_keys:
            ttl = await self.redis_client.ttl(key)
            if ttl == -2:  # Key doesn't exist (expired)
                expired_count += 1

        return expired_count

    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        if not self.redis_client:
            await self.connect()

        session_keys = await self.redis_client.keys(f"{self.session_prefix}*")
        refresh_keys = await self.redis_client.keys(f"{self.refresh_prefix}*")
        user_session_keys = await self.redis_client.keys(
            f"{self.user_sessions_prefix}*"
        )

        return {
            "active_sessions": len(session_keys),
            "active_refresh_tokens": len(refresh_keys),
            "users_with_sessions": len(user_session_keys),
            "redis_memory_usage": await self.redis_client.memory_usage(),
        }


# Global session manager instance
session_manager = RedisSessionManager()
