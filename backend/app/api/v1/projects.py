# RepoLens API - Projects Endpoints
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

# Project Management API Routes
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.models.project_models import (
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse,
    ProjectListResponse, ProjectAnalysisRequest, ProjectAnalysisResponse,
    UserSettingsRequest, UserSettingsResponse, EnvironmentConfig
)
from ...services.project_service import ProjectService

from ...core.dependencies import get_tenant_id, get_db_session, authenticate, require_permissions, get_project

router = APIRouter(
    prefix="/projects",
    tags=["📁 Project Management"],
    responses={404: {"description": "Project not found"}}
)

@router.post(
    "",
    response_model=ProjectResponse,
    summary="➕ Create New Project",
    description="""
    **Create a new project for code analysis**
    
    This endpoint allows users to create projects from:
    - 📁 **Local Path**: Clone from local filesystem
    - 🌐 **GitHub Repo**: Clone from GitHub repository
    - ☁️ **Cloud Storage**: Store in S3 bucket
    
    **Perfect for**: Setting up new codebases, importing existing projects,
    and organizing analysis work by project.
    """,
    responses={
        201: {"description": "Project created successfully"},
        400: {"description": "Invalid project data"},
        401: {"description": "Authentication required"},
        500: {"description": "Project creation failed"}
    }
)
async def create_project(
    request: ProjectCreateRequest,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new project"""
    
    if request.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant mismatch"
        )
    
    try:
        # Use the real ProjectService to create the project
        project = await project_service.create_project(request, db, user["user_id"])
        return project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get(
    "",
    response_model=ProjectListResponse,
    summary="📋 List Projects",
    description="""
    **Get list of projects for the tenant**
    
    This endpoint returns:
    - 📁 **All Projects**: Complete project list
    - 🔍 **Filtered Results**: By status, type, etc.
    - 📊 **Pagination**: Page-based navigation
    - 📈 **Metadata**: Counts, sizes, last analyzed
    
    **Perfect for**: Project dashboard, navigation sidebar,
    and project management interfaces.
    """,
    responses={
        200: {"description": "Projects retrieved successfully"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to retrieve projects"}
    }
)
async def list_projects(
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str = Query(None, description="Filter by status"),
    project_type: str = Query(None, description="Filter by storage type"),
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session)
):
    """List projects for tenant"""
    
    try:
        # Use the real ProjectService to list projects
        result = await project_service.list_projects(db, tenant_id, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="🔍 Get Project Details",
    description="""
    **Get detailed information about a specific project**
    
    This endpoint returns:
    - 📊 **Project Metadata**: Name, description, status
    - 💾 **Storage Info**: Location, type, size
    - 📈 **Analysis History**: Count, last analyzed
    - 🔧 **Configuration**: Storage settings
    
    **Perfect for**: Project details view, analysis setup,
    and project management.
    """,
    responses={
        200: {"description": "Project details retrieved"},
        404: {"description": "Project not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"}
    }
)
async def get_project(
    project_id: str,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session)
):
    """Get project by ID"""
    
    try:
        # Use the real ProjectService to get the project
        project = await project_service.get_project(db, project_id, tenant_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )

@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="✏️ Update Project",
    description="""
    **Update project information**
    
    This endpoint allows updating:
    - 📝 **Basic Info**: Name, description
    - 💾 **Storage Config**: Change storage settings
    - 🔧 **Settings**: Project-specific configuration
    
    **Perfect for**: Project management, configuration updates,
    and maintenance tasks.
    """,
    responses={
        200: {"description": "Project updated successfully"},
        404: {"description": "Project not found"},
        400: {"description": "Invalid update data"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"}
    }
)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate),
    db: AsyncSession = Depends(get_db_session)
):
    """Update project"""
    
    try:
        # Use the real ProjectService to update the project
        project = await project_service.update_project(db, project_id, tenant_id, request)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )

@router.delete(
    "/{project_id}",
    summary="🗑️ Delete Project",
    description="""
    **Delete a project and all associated data**
    
    This endpoint handles:
    - 🗑️ **Project Deletion**: Remove project record
    - 💾 **Storage Cleanup**: Delete files from storage
    - 📊 **Data Cleanup**: Remove analysis data
    - 🔒 **Access Control**: Verify permissions
    
    **Perfect for**: Project cleanup, storage management,
    and data retention policies.
    """,
    responses={
        200: {"description": "Project deleted successfully"},
        404: {"description": "Project not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"}
    }
)
async def delete_project(
    project_id: str,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(require_permissions(["delete"])),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete project"""
    
    try:
        # Use the real ProjectService to delete the project
        success = await project_service.delete_project(db, project_id, tenant_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )

@router.post(
    "/{project_id}/analyze",
    response_model=ProjectAnalysisResponse,
    summary="🔍 Analyze Project",
    description="""
    **Start analysis of a project**
    
    This endpoint initiates:
    - 🔍 **Code Analysis**: Parse and analyze codebase
    - 📋 **Requirements Extraction**: Find requirements
    - 🔗 **Mapping**: Map requirements to code
    - 📊 **Reports**: Generate analysis reports
    
    **Perfect for**: Starting analysis workflows, generating insights,
    and requirement mapping.
    """,
    responses={
        200: {"description": "Analysis started successfully"},
        404: {"description": "Project not found"},
        400: {"description": "Invalid analysis request"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"}
    }
)
async def analyze_project(
    project_id: str,
    request: ProjectAnalysisRequest,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Analyze project"""
    
    try:
        # Use the real ProjectService to start analysis
        result = project_service.start_project_analysis(
            project_id, 
            tenant_id, 
            request.analysis_type, 
            request.force_refresh
        )
        return ProjectAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis: {str(e)}"
        )

@router.get(
    "/{project_id}/analyses",
    summary="📊 Get Project Analyses",
    description="""
    **Get analysis history for a project**
    
    This endpoint returns:
    - 📈 **Analysis History**: All past analyses
    - 📊 **Status Information**: Current and completed analyses
    - 🔍 **Results**: Analysis outcomes and reports
    - 📅 **Timestamps**: When analyses were run
    
    **Perfect for**: Analysis tracking, result comparison,
    and progress monitoring.
    """,
    responses={
        200: {"description": "Analyses retrieved successfully"},
        404: {"description": "Project not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"}
    }
)
async def get_project_analyses(
    project_id: str,
    tenant_id: str = Depends(get_tenant_id),
    project_service: ProjectService = Depends(get_project),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Get project analyses"""
    
    try:
        # First check if project exists
        project = project_service.get_project(project_id, tenant_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # TODO: Implement actual analysis history retrieval
        # For now, return empty list
        return {"analyses": [], "total": 0}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analyses: {str(e)}"
        )
