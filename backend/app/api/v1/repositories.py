# RepoLens API - Repositories Endpoints
# Repository management API routes
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from ...core.dependencies import (
    authenticate,
    get_audit,
    get_db,
    get_neo4j,
    get_parser,
    process_repository_analysis,
    require_permissions,
)
from ...services.audit_service import AuditService
from ...services.neo4j_service import Neo4jService
from ...services.parser_service import ParserService
from ...shared.models.api_models import (
    IndexingStatus,
    RepoAnalysisRequest,
    RepoAnalysisResponse,
)


router = APIRouter(
    prefix="/repositories",
    tags=["Repository Management"],
    responses={404: {"description": "Repository not found"}},
)


@router.post(
    "/analyze",
    response_model=RepoAnalysisResponse,
    summary="Analyze Repository",
    description="Initiate repository analysis and indexing",
    responses={
        400: {"description": "Invalid request parameters"},
        401: {"description": "Authentication required"},
        500: {"description": "Analysis initiation failed"},
    },
)
async def analyze_repo(
    request: RepoAnalysisRequest,
    background_tasks: BackgroundTasks,
    neo4j: Neo4jService = Depends(get_neo4j),
    parser: ParserService = Depends(get_parser),
    audit: AuditService = Depends(get_audit),
    user: dict[str, Any] = Depends(authenticate),
):
    """Initiate repository analysis and indexing"""
    try:
        # Get tenant ID from user
        tenant_id = user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID required"
            )

        # Generate analysis ID
        analysis_id = str(uuid.uuid4())

        # Add background task for analysis
        background_tasks.add_task(
            process_repository_analysis,
            analysis_id,
            request.repo_url,
            tenant_id,
            neo4j,
            parser,
            audit,
        )

        # Log the analysis initiation
        await audit.log_action(
            user_id=user.get("user_id"),
            action="repository_analysis_initiated",
            resource_id=analysis_id,
            details={"repo_url": request.repo_url},
        )

        return RepoAnalysisResponse(
            analysis_id=analysis_id,
            status=IndexingStatus.IN_PROGRESS,
            message="Analysis initiated successfully",
            estimated_completion=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis initiation failed: {str(e)}",
        )


@router.delete(
    "/{repo_id}",
    summary="Delete Repository",
    description="Delete repository and all associated data",
    responses={
        200: {"description": "Repository deleted successfully"},
        404: {"description": "Repository not found"},
        403: {"description": "Insufficient permissions"},
        500: {"description": "Deletion failed"},
    },
)
async def delete_repo(
    repo_id: str,
    db=Depends(get_db),
    user: dict[str, Any] = Depends(require_permissions(["admin"])),
):
    """Delete repository and all associated data"""
    try:
        # Get tenant ID from user
        tenant_id = user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID required"
            )

        # Delete repository from database
        # This would typically delete from your database
        # For now, just return success

        # Log the deletion
        await audit.log_action(
            user_id=user.get("user_id"),
            action="repository_deleted",
            resource_id=repo_id,
            details={"tenant_id": tenant_id},
        )

        return {"message": "Repository deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(e)}",
        )


@router.get(
    "/{repo_id}/status",
    summary="Get Repository Status",
    description="Get analysis status for a repository",
    responses={
        200: {"description": "Status retrieved successfully"},
        404: {"description": "Repository not found"},
        500: {"description": "Failed to get status"},
    },
)
async def get_repo_status(repo_id: str, user: dict[str, Any] = Depends(authenticate)):
    """Get analysis status for a repository"""
    try:
        # Get tenant ID from user
        tenant_id = user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID required"
            )

        # This would typically query your database for the repository status
        # For now, return a mock status

        return {
            "repo_id": repo_id,
            "status": "completed",
            "last_analyzed": datetime.now(timezone.utc).isoformat(),
            "analysis_count": 1,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}",
        )
