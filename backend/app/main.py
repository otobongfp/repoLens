# RepoLens API
# Production FastAPI application with multi-tenant SaaS architecture
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

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import os
import logging
from datetime import datetime, timezone
import uuid
import jwt
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from app.services.neo4j_service import Neo4jService, GraphService
from app.services.parser_service import ParserService
from app.services.requirement_service import RequirementService
from app.services.vector_service import VectorService
from app.services.symbol_service import SymbolService
from app.services.security_service import SecurityService
from app.services.action_service import ActionService
from app.services.audit_service import AuditService

# Import API routers
from app.api.v1 import ai, repository, health, repositories, requirements, action_proposals, security, admin, projects, settings, auth
from app.core.config import settings as app_settings
from app.services.session_manager import session_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
security_scheme = HTTPBearer()

# Enums
class Plan(str, Enum):
    SHARED = "shared"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

class VerificationStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING = "pending"

class ProposalStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_HUMAN = "needs_human"

class IndexingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Models
class Tenant(BaseModel):
    tenant_id: str
    name: str
    plan: Plan
    billing_contact: str
    active_repos: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RepoAnalysisRequest(BaseModel):
    tenant_id: str
    repo_url: str
    branch: Optional[str] = None
    commit: Optional[str] = None

class RepoAnalysisResponse(BaseModel):
    job_id: str
    repo_id: str
    status: IndexingStatus

class RequirementExtractRequest(BaseModel):
    tenant_id: str
    repo_id: Optional[str] = None
    text: str
    source: str

class RequirementExtractResponse(BaseModel):
    requirements: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RequirementMatchRequest(BaseModel):
    tenant_id: str
    top_k: int = 10

class RequirementMatchResponse(BaseModel):
    candidates: List[Dict[str, Any]]

class RequirementVerifyRequest(BaseModel):
    tenant_id: str
    user_id: str
    function_id: str
    status: VerificationStatus
    note: Optional[str] = None

class RequirementVerifyResponse(BaseModel):
    verification_id: str

class ActionProposalRequest(BaseModel):
    tenant_id: str
    repo_id: str
    proposer_id: Optional[str] = None
    patch_s3: str
    rationale: str
    tests: List[str] = []

class ActionProposalResponse(BaseModel):
    proposal_id: str
    status: ProposalStatus

class ActionApprovalRequest(BaseModel):
    approver_id: str
    note: Optional[str] = None

class UsageMetrics(BaseModel):
    active_repos: int
    vector_count: int
    storage_bytes: int
    api_requests: int
    limits: Dict[str, Any]

# Import dependencies from core
from app.core.dependencies import (
    get_neo4j, get_parser, get_vector, get_requirement, get_symbol,
    get_security, get_action, get_audit, authenticate, require_permissions,
    get_tenant_id, get_db, process_repository_analysis
)

# FastAPI App
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting RepoLens API")
    
    # Connect to Redis
    try:
        await session_manager.connect()
        logger.info("Redis session manager connected")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
    
    # Create default tenant
    default_tenant = Tenant(
        tenant_id="tenant_123",
        name="Default Tenant",
        plan=Plan.PRO,
        billing_contact="admin@example.com"
    )
    
    # Get database service and create default tenant
    db_service = await get_db()
    await db_service.create_tenant(default_tenant)
    
    yield
    
    # Shutdown
    logger.info("Shutting down RepoLens API")
    
    # Disconnect from Redis
    try:
        await session_manager.disconnect()
        logger.info("Redis session manager disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting from Redis: {e}")

app = FastAPI(
    title="RepoLens API",
    description="AI-powered codebase analysis with requirement mapping",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,  # Use configured origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(repository.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(repositories.router, prefix="/api/v1")
app.include_router(requirements.router, prefix="/api/v1")
app.include_router(action_proposals.router, prefix="/api/v1")
app.include_router(security.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")

# Background task
async def process_repository_analysis(repo_data: Dict[str, Any], repo_url: str, 
                                    neo4j: Neo4jService, parser: ParserService, 
                                    audit: AuditService):
    """Process repository analysis with enterprise services"""
    logger.info(f"Starting analysis for repository {repo_data['repo_id']}")
    
    try:
        # Step 1: Parse repository
        parsed_files = parser.parse_repository(repo_url)
        
        # Step 2: Index into Neo4j
        graph_service = GraphService(neo4j)
        index_result = graph_service.index_repository(repo_data, parsed_files)
        
        # Step 3: Log completion
        audit.log_repository_operation(
            tenant_id=repo_data['tenant_id'],
            repo_id=repo_data['repo_id'],
            actor_id='system',
            operation='index',
            details={
                'files_processed': len(parsed_files),
                'functions_indexed': index_result['functions_indexed'],
                'classes_indexed': index_result['classes_indexed']
            }
        )
        
        logger.info(f"Completed analysis for repository {repo_data['repo_id']}")
        
    except Exception as e:
        logger.error(f"Repository analysis failed: {e}")
        audit.log_repository_operation(
            tenant_id=repo_data['tenant_id'],
            repo_id=repo_data['repo_id'],
            actor_id='system',
            operation='index',
            details={'error': str(e), 'status': 'failed'}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)