# RepoLens API - Projects Endpoints
# Project Management API Routes
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.models.project_models import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse,
    ProjectAnalysisRequest,
    ProjectAnalysisResponse,
    UserSettingsRequest,
    UserSettingsResponse,
    EnvironmentConfig,
)
from ...services.project_service import ProjectService

from ...core.dependencies import (
    get_tenant_id,
    get_db_session,
    authenticate,
    require_permissions,
    get_project,
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
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate),
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
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate),
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
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate),
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
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate),
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
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(require_permissions(["admin", "owner"])),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete project and all associated data"""
    try:
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
