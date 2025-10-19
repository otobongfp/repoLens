# Core dependencies and dependency injection
import os
from typing import Any

import boto3
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..features.ai_analysis.services.ai_analyzer_service import AIAnalyzerService
from ..features.repository.services import RepositoryAnalyzer
from ..services.action_service import ActionService
from ..services.audit_service import AuditService
from ..services.neo4j_service import Neo4jService
from ..services.parser_service import ParserService
from ..services.project_service import ProjectService, StorageManager
from ..services.requirement_service import RequirementService
from ..services.security_service import SecurityService
from ..services.symbol_service import SymbolService
from ..services.vector_service import VectorService
from .config import settings


# Feature-specific services
def get_repository_service() -> RepositoryAnalyzer:
    """Dependency for repository analysis service"""
    return RepositoryAnalyzer()


def get_ai_service() -> AIAnalyzerService:
    """Dependency for AI analysis service"""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Please set OPENAI_API_KEY.",
        )
    return AIAnalyzerService()


# Core enterprise services
def get_neo4j_service() -> Neo4jService:
    """Get Neo4j service instance"""
    # Read from environment variables
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    if not uri or not user or not password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j not configured. Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD.",
        )

    return Neo4jService(uri=uri, user=user, password=password)


def get_parser_service() -> ParserService:
    """Get parser service instance"""
    return ParserService()


def get_vector_service() -> VectorService:
    """Get vector service instance"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pgvector_url = os.getenv("PGVECTOR_DB_URL")

    if not openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI not configured. Please set OPENAI_API_KEY.",
        )

    if not pgvector_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL not configured. Please set PGVECTOR_DB_URL.",
        )

    return VectorService(openai_api_key=openai_api_key, pgvector_url=pgvector_url)


def get_requirement_service(
    neo4j_service: Neo4jService, vector_service: VectorService
) -> RequirementService:
    """Get requirement service instance"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI not configured. Please set OPENAI_API_KEY.",
        )

    return RequirementService(
        openai_api_key=openai_api_key,
        vector_service=vector_service,
        neo4j_service=neo4j_service,
    )


def get_symbol_service(neo4j_service: Neo4jService) -> SymbolService:
    """Get symbol service instance"""
    return SymbolService(neo4j_service)


def get_security_service(neo4j_service: Neo4jService) -> SecurityService:
    """Get security service instance"""
    return SecurityService(neo4j_service)


def get_action_service(neo4j_service: Neo4jService) -> ActionService:
    """Get action service instance"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI not configured. Please set OPENAI_API_KEY.",
        )

    # Initialize S3 client with environment variables
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    if not aws_access_key_id or not aws_secret_access_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AWS S3 not configured. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.",
        )

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
    )

    return ActionService(
        openai_api_key=openai_api_key, neo4j_service=neo4j_service, s3_client=s3_client
    )


def get_audit_service(neo4j_service: Neo4jService) -> AuditService:
    """Get audit service instance"""
    return AuditService(neo4j_service)


# Global service instances - lazy initialization
_neo4j_service = None
_parser_service = None
_vector_service = None
_requirement_service = None
_symbol_service = None
_security_service = None
_action_service = None
_audit_service = None
_project_service = None


def _get_neo4j_service_instance() -> Neo4jService:
    """Get or create Neo4j service instance"""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = get_neo4j_service()
    return _neo4j_service


def _get_parser_service_instance() -> ParserService:
    """Get or create parser service instance"""
    global _parser_service
    if _parser_service is None:
        _parser_service = get_parser_service()
    return _parser_service


def _get_vector_service_instance() -> VectorService:
    """Get or create vector service instance"""
    global _vector_service
    if _vector_service is None:
        _vector_service = get_vector_service()
    return _vector_service


def _get_requirement_service_instance() -> RequirementService:
    """Get or create requirement service instance"""
    global _requirement_service
    if _requirement_service is None:
        _requirement_service = get_requirement_service(
            _get_neo4j_service_instance(), _get_vector_service_instance()
        )
    return _requirement_service


def _get_symbol_service_instance() -> SymbolService:
    """Get or create symbol service instance"""
    global _symbol_service
    if _symbol_service is None:
        _symbol_service = get_symbol_service(_get_neo4j_service_instance())
    return _symbol_service


def _get_security_service_instance() -> SecurityService:
    """Get or create security service instance"""
    global _security_service
    if _security_service is None:
        _security_service = get_security_service(_get_neo4j_service_instance())
    return _security_service


def _get_action_service_instance() -> ActionService:
    """Get or create action service instance"""
    global _action_service
    if _action_service is None:
        _action_service = get_action_service(_get_neo4j_service_instance())
    return _action_service


def _get_audit_service_instance() -> AuditService:
    """Get or create audit service instance"""
    global _audit_service
    if _audit_service is None:
        _audit_service = get_audit_service(_get_neo4j_service_instance())
    return _audit_service


def _get_project_service_instance() -> ProjectService:
    """Get or create project service instance"""
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service


# FastAPI dependency functions
async def get_neo4j() -> Neo4jService:
    return _get_neo4j_service_instance()


async def get_parser() -> ParserService:
    return _get_parser_service_instance()


async def get_vector() -> VectorService:
    return _get_vector_service_instance()


async def get_requirement() -> RequirementService:
    return _get_requirement_service_instance()


async def get_symbol() -> SymbolService:
    return _get_symbol_service_instance()


async def get_security() -> SecurityService:
    return _get_security_service_instance()


async def get_action() -> ActionService:
    return _get_action_service_instance()


async def get_audit() -> AuditService:
    return _get_audit_service_instance()


async def get_project_service() -> ProjectService:
    return _get_project_service_instance()


# Background task functions
async def process_repository_analysis(
    repo_data: dict[str, Any],
    repo_url: str,
    neo4j: Neo4jService,
    parser: ParserService,
    audit: AuditService,
):
    """Process repository analysis with enterprise services"""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"Starting analysis for repository {repo_data['repo_id']}")

    try:
        # Step 1: Parse repository
        parsed_files = parser.parse_repository(repo_url)

        # Step 2: Index into Neo4j
        from ..services.neo4j_service import GraphService

        graph_service = GraphService(neo4j)
        index_result = graph_service.index_repository(repo_data, parsed_files)

        # Step 3: Log completion
        audit.log_repository_operation(
            tenant_id=repo_data["tenant_id"],
            repo_id=repo_data["repo_id"],
            actor_id="system",
            operation="index",
            details={
                "files_processed": len(parsed_files),
                "functions_indexed": index_result["functions_indexed"],
                "classes_indexed": index_result["classes_indexed"],
            },
        )

        logger.info(f"Completed analysis for repository {repo_data['repo_id']}")

    except Exception as e:
        logger.error(f"Failed to analyze repository {repo_data['repo_id']}: {e}")
        # Log the error
        audit.log_repository_operation(
            tenant_id=repo_data["tenant_id"],
            repo_id=repo_data["repo_id"],
            actor_id="system",
            operation="index_error",
            details={"error": str(e)},
        )
        raise


# Authentication and authorization dependencies
async def get_user_tenant(user_id: str, db: AsyncSession) -> str:
    """Get the tenant for the user (should already exist from registration)"""
    import logging

    from fastapi import HTTPException, status
    from sqlalchemy import select

    from app.database.models.tenant import TenantMember

    logger = logging.getLogger(__name__)

    try:
        # Get user's tenant membership (should exist from registration)
        result = await db.execute(
            select(TenantMember).where(TenantMember.user_id == user_id)
        )
        membership = result.scalars().first()

        logger.info(
            f"Looking for tenant for user {user_id}, found membership: {membership}"
        )

        if membership:
            logger.info(f"Found tenant {membership.tenant_id} for user {user_id}")
            return str(membership.tenant_id)

        # If no membership found, try to create one (for existing users)
        logger.warning(
            f"No tenant membership found for user {user_id}, attempting to create one"
        )
        from app.database.models.user import User
        from app.services.auth_service import auth_service

        # Get the user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if user:
            # Create a tenant for this existing user
            tenant = await auth_service.create_default_tenant(db, user)
            logger.info(f"Created tenant {tenant.id} for existing user {user_id}")
            return str(tenant.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user tenant",
        )


async def authenticate(request: Request) -> dict[str, Any]:
    """Real authentication using JWT tokens"""
    from app.services.auth_service import auth_service

    # Get authorization header
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = authorization.split(" ")[1]

    try:
        # Verify token and get user info
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")
        session_id = payload.get("session_id")

        if not user_id or not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        # Get user session from Redis
        user_data = await auth_service.get_user_by_session(session_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid",
            )

        # Get tenant for user using a proper database session
        from app.database.connection import get_db

        tenant_id = None
        async for db in get_db():
            try:
                tenant_id = await get_user_tenant(user_id, db)
                break
            except Exception as e:
                logger.error(f"Failed to get tenant for user {user_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to get user tenant information",
                )

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User tenant information not available",
            )

        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "email": user_data.get("email"),
            "role": user_data.get("role"),
            "session_id": session_id,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )


def require_permissions(required: list):
    """Require specific permissions - returns a dependency function"""

    def check_permissions(user: dict[str, Any] = Depends(authenticate)):
        user_permissions = user.get("permissions", [])
        if not any(p in user_permissions for p in required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required permissions: {required}",
            )
        return user

    return check_permissions


async def get_tenant_id(user: dict[str, Any] = Depends(authenticate)) -> str:
    """Get tenant ID from user"""
    return user["tenant_id"]


async def get_db_session():
    """Get database session dependency"""
    from app.database.connection import get_db as _get_db

    async for session in _get_db():
        yield session


# Mock database service
class DatabaseService:
    def __init__(self):
        self.repos = {}
        self.requirements = {}
        self.verifications = {}
        self.proposals = {}
        self.tenants = {}
        self.projects = {}
        self.analyses = {}
        self.settings = {}

    async def get_tenant(self, tenant_id: str):
        return self.tenants.get(tenant_id)

    async def create_tenant(self, tenant):
        """Create a new tenant"""
        self.tenants[tenant.tenant_id] = {
            "tenant_id": tenant.tenant_id,
            "name": tenant.name,
            "plan": tenant.plan,
            "billing_contact": tenant.billing_contact,
            "created_at": "2024-01-01T00:00:00Z",
        }
        return tenant

    async def get_repo_count(self, tenant_id: str):
        return len([r for r in self.repos.values() if r.get("tenant_id") == tenant_id])

    async def decrement_repos(self, tenant_id: str):
        pass

    async def log_audit(
        self, actor_id: str, action: str, target_ids: list, details: dict
    ):
        pass


async def get_db() -> DatabaseService:
    """Get database service instance"""
    return DatabaseService()


def validate_file_path(file_path: str) -> str:
    """Validate and normalize file path"""
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File path is required"
        )

    # Normalize path
    normalized_path = os.path.normpath(file_path)

    # Security check - prevent directory traversal
    if ".." in normalized_path or normalized_path.startswith("/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file path"
        )

    return normalized_path


def validate_repository_path(repo_path: str) -> str:
    """Validate repository path"""
    if not repo_path:
        repo_path = "."

    if not os.path.exists(repo_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository path not found: {repo_path}",
        )

    if not os.path.isdir(repo_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Path must be a directory: {repo_path}",
        )

    return repo_path
