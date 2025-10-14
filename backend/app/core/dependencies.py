# Core dependencies and dependency injection
from fastapi import Depends, HTTPException, status
from typing import Generator, Dict, Any
import os
from pathlib import Path
import boto3

from .config import settings
from ..features.repository.services import RepositoryAnalyzer
from ..features.ai_analysis.services.ai_analyzer_service import AIAnalyzerService
from ..services.neo4j_service import Neo4jService, GraphService
from ..services.parser_service import ParserService
from ..services.requirement_service import RequirementService
from ..services.vector_service import VectorService
from ..services.symbol_service import SymbolService
from ..services.security_service import SecurityService
from ..services.action_service import ActionService
from ..services.audit_service import AuditService
from ..services.project_service import ProjectService, StorageManager

# Feature-specific services
def get_repository_service() -> RepositoryAnalyzer:
    """Dependency for repository analysis service"""
    return RepositoryAnalyzer()

def get_ai_service() -> AIAnalyzerService:
    """Dependency for AI analysis service"""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Please set OPENAI_API_KEY."
        )
    return AIAnalyzerService()

# Core enterprise services
def get_neo4j_service() -> Neo4jService:
    """Get Neo4j service instance"""
    return Neo4jService(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )

def get_parser_service() -> ParserService:
    """Get parser service instance"""
    return ParserService()

def get_vector_service() -> VectorService:
    """Get vector service instance"""
    return VectorService(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        pgvector_url=os.getenv("PGVECTOR_DB_URL", "postgresql://user:pass@localhost/vectordb")
    )

def get_requirement_service(neo4j_service: Neo4jService, vector_service: VectorService) -> RequirementService:
    """Get requirement service instance"""
    return RequirementService(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        vector_service=vector_service,
        neo4j_service=neo4j_service
    )

def get_symbol_service(neo4j_service: Neo4jService) -> SymbolService:
    """Get symbol service instance"""
    return SymbolService(neo4j_service)

def get_security_service(neo4j_service: Neo4jService) -> SecurityService:
    """Get security service instance"""
    return SecurityService(neo4j_service)

def get_action_service(neo4j_service: Neo4jService) -> ActionService:
    """Get action service instance"""
    s3_client = boto3.client('s3')
    return ActionService(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        neo4j_service=neo4j_service,
        s3_client=s3_client
    )

def get_audit_service(neo4j_service: Neo4jService) -> AuditService:
    """Get audit service instance"""
    return AuditService(neo4j_service)

def get_project_service(neo4j_service: Neo4jService) -> ProjectService:
    """Get project service instance"""
    # Create environment config from settings
    from ..shared.models.project_models import EnvironmentConfig
    env_config = EnvironmentConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_region=os.getenv("AWS_REGION"),
        s3_bucket=os.getenv("S3_BUCKET"),
        neo4j_uri=os.getenv("NEO4J_URI"),
        neo4j_user=os.getenv("NEO4J_USER"),
        neo4j_password=os.getenv("NEO4J_PASSWORD"),
        use_local_backend=True,
        backend_url="http://localhost:8000"
    )
    
    storage_manager = StorageManager(env_config)
    return ProjectService(neo4j_service, storage_manager)

# Global service instances
neo4j_service = get_neo4j_service()
parser_service = get_parser_service()
vector_service = get_vector_service()
requirement_service = get_requirement_service(neo4j_service, vector_service)
symbol_service = get_symbol_service(neo4j_service)
security_service = get_security_service(neo4j_service)
action_service = get_action_service(neo4j_service)
audit_service = get_audit_service(neo4j_service)
project_service = get_project_service(neo4j_service)

# FastAPI dependency functions
async def get_neo4j() -> Neo4jService:
    return neo4j_service

async def get_parser() -> ParserService:
    return parser_service

async def get_vector() -> VectorService:
    return vector_service

async def get_requirement() -> RequirementService:
    return requirement_service

async def get_symbol() -> SymbolService:
    return symbol_service

async def get_security() -> SecurityService:
    return security_service

async def get_action() -> ActionService:
    return action_service

async def get_audit() -> AuditService:
    return audit_service

async def get_project() -> ProjectService:
    return project_service

# Authentication and authorization dependencies
async def authenticate(credentials = None) -> Dict[str, Any]:
    """Mock authentication - replace with real implementation"""
    return {
        "user_id": "user_123",
        "tenant_id": "tenant_123",
        "roles": ["dev", "pm"],
        "permissions": ["read", "write", "verify", "approve"]
    }

async def require_permissions(required: list, user: Dict[str, Any] = Depends(authenticate)):
    """Require specific permissions"""
    user_permissions = user.get("permissions", [])
    if not any(p in user_permissions for p in required):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Required permissions: {required}"
        )
    return user

async def get_tenant_id(user: Dict[str, Any] = Depends(authenticate)) -> str:
    """Get tenant ID from user"""
    return user["tenant_id"]

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
    
    async def get_repo_count(self, tenant_id: str):
        return len([r for r in self.repos.values() if r.get("tenant_id") == tenant_id])
    
    async def decrement_repos(self, tenant_id: str):
        pass
    
    async def log_audit(self, actor_id: str, action: str, target_ids: list, details: dict):
        pass

async def get_db() -> DatabaseService:
    """Get database service instance"""
    return DatabaseService()

def validate_file_path(file_path: str) -> str:
    """Validate and normalize file path"""
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File path is required"
        )
    
    # Normalize path
    normalized_path = os.path.normpath(file_path)
    
    # Security check - prevent directory traversal
    if ".." in normalized_path or normalized_path.startswith("/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path"
        )
    
    return normalized_path

def validate_repository_path(repo_path: str) -> str:
    """Validate repository path"""
    if not repo_path:
        repo_path = "."
    
    if not os.path.exists(repo_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository path not found: {repo_path}"
        )
    
    if not os.path.isdir(repo_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Path must be a directory: {repo_path}"
        )
    
    return repo_path
