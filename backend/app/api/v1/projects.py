# RepoLens API - Projects Endpoints
# Project Management API Routes
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from ...core.dependencies import (
    authenticate,
    get_db_session,
    get_project_service,
    get_tenant_id,
    require_permissions,
)
from ...services.advanced_analysis_service import AdvancedAnalysisService
from ...services.project_service import ProjectService
from ...shared.models.project_models import (
    ProjectAnalysisRequest,
    ProjectAnalysisResponse,
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)


router = APIRouter(
    prefix="/projects",
    tags=["Project Management"],
    responses={404: {"description": "Project not found"}},
)


@router.post(
    "",
    response_model=ProjectResponse,
    summary="Create New Project",
    description="Create a new project",
    responses={
        201: {"description": "Project created successfully"},
        400: {"description": "Invalid project data"},
        401: {"description": "Authentication required"},
        500: {"description": "Project creation failed"},
    },
)
async def create_project(
    request: ProjectCreateRequest,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project_service),
    user: dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new project"""
    try:
        user_id = user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID required"
            )

        project = await project_service.create_project(
            db=db, request=request, tenant_id=tenant_id, user_id=user_id
        )

        if not project:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project",
            )

        return project

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Project creation failed: {str(e)}",
        )


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List Projects",
    description="Get list of projects for tenant",
    responses={
        200: {"description": "Projects retrieved successfully"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to retrieve projects"},
    },
)
async def list_projects(
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str = Query(None, description="Filter by status"),
    project_type: str = Query(None, description="Filter by storage type"),
    project_service: ProjectService = Depends(get_project_service),
    user: dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session),
):
    """Get list of projects for tenant"""
    try:
        projects = await project_service.list_projects(db=db, tenant_id=tenant_id)

        return ProjectListResponse(
            projects=projects, total=len(projects), page=page, page_size=page_size
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve projects: {str(e)}",
        )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get Project",
    description="Get project by ID",
    responses={
        200: {"description": "Project retrieved successfully"},
        404: {"description": "Project not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def get_project(
    project_id: str,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project_service),
    user: dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session),
):
    """Get project by ID"""
    try:
        project = await project_service.get_project(
            db=db, project_id=project_id, tenant_id=tenant_id
        )

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        return project

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project: {str(e)}",
        )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update Project",
    description="Update project details",
    responses={
        200: {"description": "Project updated successfully"},
        404: {"description": "Project not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
        500: {"description": "Project update failed"},
    },
)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project_service),
    user: dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session),
):
    """Update project details"""
    try:
        project = await project_service.update_project(
            db=db, project_id=project_id, tenant_id=tenant_id, request=request
        )

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        return project

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Project update failed: {str(e)}",
        )


@router.delete(
    "/{project_id}",
    summary="Delete Project",
    description="Delete project and all associated data",
    responses={
        200: {"description": "Project deleted successfully"},
        404: {"description": "Project not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
        500: {"description": "Project deletion failed"},
    },
)
async def delete_project(
    project_id: str,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project_service),
    user: dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete project and all associated data"""
    try:
        # Check if user owns the project
        project = await project_service.get_project(db, project_id, tenant_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Check if user is the owner of the project
        if project.owner_id != user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own projects",
            )

        success = await project_service.delete_project(
            db=db, project_id=project_id, tenant_id=tenant_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        return {"message": "Project deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Project deletion failed: {str(e)}",
        )


@router.post(
    "/{project_id}/analyze",
    response_model=ProjectAnalysisResponse,
    summary="Analyze Project",
    description="Start analysis for a specific project",
    responses={
        200: {"description": "Analysis started successfully"},
        404: {"description": "Project not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
        500: {"description": "Analysis initiation failed"},
    },
)
async def analyze_project(
    project_id: str,
    request: ProjectAnalysisRequest,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project_service),
    user: dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session),
):
    """Start analysis for a specific project"""
    try:
        # Check if project exists and user owns it
        project = await project_service.get_project(db, project_id, tenant_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Check if user is the owner of the project
        if project.owner_id != user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only analyze your own projects",
            )

        # Start advanced analysis with background processing
        analysis_service = AdvancedAnalysisService()

        # Inject Neo4j service if available
        try:
            from ...core.dependencies import get_neo4j

            neo4j_service = await get_neo4j()
            analysis_service.set_neo4j_service(neo4j_service)
        except Exception as e:
            logger.warning(f"Neo4j service not available: {e}")

        # Start background analysis
        analysis_id = await analysis_service.analyze_project_async(
            project_id=project_id,
            tenant_id=tenant_id,
            analysis_type=request.analysis_type,
            force_refresh=request.force_refresh,
        )

        return ProjectAnalysisResponse(
            analysis_id=analysis_id,
            project_id=project_id,
            status="started",
            started_at=datetime.now(timezone.utc).isoformat(),
            estimated_completion=None,
            progress={
                "message": "Analysis started in background",
                "analysis_id": analysis_id,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis initiation failed: {str(e)}",
        )


@router.get(
    "/{project_id}/analysis/{analysis_id}/progress",
    summary="Get Analysis Progress",
    description="Get real-time progress of analysis",
    responses={
        200: {"description": "Progress retrieved successfully"},
        404: {"description": "Analysis not found"},
        401: {"description": "Authentication required"},
    },
)
async def get_analysis_progress(
    project_id: str,
    analysis_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session),
):
    """Get real-time analysis progress"""
        try:
            # Check if project exists and user owns it
            project_service = ProjectService()
            project = await project_service.get_project(db, project_id, tenant_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )

            if project.owner_id != user["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own project analysis",
                )

            # Get analysis progress from Redis
            analysis_service = AdvancedAnalysisService()
            progress = await analysis_service.get_analysis_progress_async(analysis_id)

            if not progress:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found"
                )
        return {
            "analysis_id": analysis_id,
            "project_id": project_id,
            "status": progress.status.value,
            "progress_percentage": progress.progress_percentage,
            "current_step": progress.current_step,
            "total_files": progress.total_files,
            "parsed_files": progress.parsed_files,
            "total_functions": progress.total_functions,
            "analyzed_functions": progress.analyzed_functions,
            "error_message": progress.error_message,
            "started_at": (
                progress.started_at.isoformat() if progress.started_at else None
            ),
            "completed_at": (
                progress.completed_at.isoformat() if progress.completed_at else None
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis progress: {str(e)}",
        )


@router.get(
    "/{project_id}/analysis/{analysis_id}/result",
    summary="Get Analysis Result",
    description="Get completed analysis results",
    responses={
        200: {"description": "Results retrieved successfully"},
        404: {"description": "Analysis not found or not completed"},
        401: {"description": "Authentication required"},
    },
)
async def get_analysis_result(
    project_id: str,
    analysis_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session),
):
    """Get completed analysis results"""
    try:
        # Check if project exists and user owns it
        project_service = ProjectService()
        project = await project_service.get_project(db, project_id, tenant_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        if project.owner_id != user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own project analysis",
            )

        # Get analysis result from Redis
        analysis_service = AdvancedAnalysisService()
        result = await analysis_service.get_analysis_result_async(analysis_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found or not completed",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis result: {str(e)}",
        )
