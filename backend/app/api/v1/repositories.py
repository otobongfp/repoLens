# Repository management API routes
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, Any
from datetime import datetime, timezone
import uuid

from ...services.neo4j_service import Neo4jService
from ...services.parser_service import ParserService
from ...services.audit_service import AuditService
from ...shared.models.api_models import RepoAnalysisRequest, RepoAnalysisResponse, IndexingStatus

from ...core.dependencies import get_neo4j, get_parser, get_audit, authenticate, process_repository_analysis

router = APIRouter(
    prefix="/repositories",
    tags=["📁 Repository Management"],
    responses={404: {"description": "Repository not found"}}
)

@router.post(
    "/analyze",
    response_model=RepoAnalysisResponse,
    summary="🔍 Analyze Repository",
    description="""
    **Analyze a repository using enterprise services**
    
    This endpoint initiates comprehensive repository analysis including:
    - 📁 File structure parsing
    - 🔧 Code analysis and indexing
    - 🔗 Dependency mapping
    - 📊 Metrics collection
    - 🔒 Security assessment
    
    **Perfect for**: Repository onboarding, code analysis, 
    dependency tracking, and security scanning.
    """,
    responses={
        200: {"description": "Repository analysis initiated successfully"},
        400: {"description": "Invalid request parameters"},
        401: {"description": "Authentication required"},
        500: {"description": "Analysis initiation failed"}
    }
)
async def analyze_repo(
    request: RepoAnalysisRequest,
    background_tasks: BackgroundTasks,
    neo4j: Neo4jService = Depends(get_neo4j),
    parser: ParserService = Depends(get_parser),
    audit: AuditService = Depends(get_audit),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Analyze a repository using enterprise services"""
    
    job_id = str(uuid.uuid4())
    repo_id = str(uuid.uuid4())
    
    # Create repository data
    repo_data = {
        'tenant_id': request.tenant_id,
        'repo_id': repo_id,
        'url': request.repo_url,
        'branch': request.branch,
        'commit': request.commit,
        'created_at': datetime.now(timezone.utc)
    }
    
    # Log audit event
    audit.log_repository_operation(
        tenant_id=request.tenant_id,
        repo_id=repo_id,
        actor_id=user["user_id"],
        operation="analyze",
        details={"url": request.repo_url, "job_id": job_id}
    )
    
    # Start background analysis
    background_tasks.add_task(
        process_repository_analysis,
        repo_data,
        request.repo_url,
        neo4j,
        parser,
        audit
    )
    
    return RepoAnalysisResponse(
        job_id=job_id,
        repo_id=repo_id,
        status=IndexingStatus.PENDING
    )

@router.delete(
    "/{repo_id}",
    summary="🗑️ Delete Repository",
    description="""
    **Delete a repository and all associated data**
    
    This endpoint removes:
    - 📁 Repository metadata
    - 🔧 Analysis results
    - 🔗 Dependency graphs
    - 📊 Metrics and statistics
    - 🔒 Security scan results
    
    **Perfect for**: Repository cleanup, data management, 
    tenant maintenance, and compliance.
    """,
    responses={
        200: {"description": "Repository deleted successfully"},
        404: {"description": "Repository not found"},
        403: {"description": "Insufficient permissions"},
        500: {"description": "Deletion failed"}
    }
)
async def delete_repo(
    repo_id: str,
    db = Depends(get_db),  # Will need to import this
    user: Dict[str, Any] = Depends(require_permissions(["admin"]))  # Will need to import this
):
    """Delete repository"""
    
    if repo_id not in db.repos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    repo_data = db.repos[repo_id]
    tenant_id = repo_data["tenant_id"]
    
    await db.decrement_repos(tenant_id)
    del db.repos[repo_id]
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="delete_repo",
        target_ids=[repo_id],
        details={"tenant_id": tenant_id}
    )
    
    return {"message": "Repository deleted"}

@router.get(
    "/{repo_id}/status",
    summary="📊 Repository Status",
    description="""
    **Get current status of repository analysis**
    
    This endpoint provides:
    - 📈 Analysis progress
    - 🔧 Current processing stage
    - 📊 Completion metrics
    - ⚠️ Error information
    - 🕒 Last update timestamp
    
    **Perfect for**: Progress monitoring, status checks, 
    debugging analysis issues, and user feedback.
    """,
    responses={
        200: {"description": "Repository status retrieved successfully"},
        404: {"description": "Repository not found"},
        403: {"description": "Access denied"},
        500: {"description": "Status retrieval failed"}
    }
)
async def get_repo_status(
    repo_id: str,
    tenant_id: str = Depends(get_tenant_id),  # Will need to import this
    db = Depends(get_db)  # Will need to import this
):
    """Get repository status"""
    
    if repo_id not in db.repos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    repo_data = db.repos[repo_id]
    if repo_data["tenant_id"] != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "repo_id": repo_id,
        "status": repo_data["status"],
        "commit": repo_data["commit"],
        "created_at": repo_data["created_at"]
    }
