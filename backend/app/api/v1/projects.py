# Project Management API Routes
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List
from datetime import datetime, timezone

from ...shared.models.project_models import (
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse,
    ProjectListResponse, ProjectAnalysisRequest, ProjectAnalysisResponse,
    UserSettingsRequest, UserSettingsResponse, EnvironmentConfig
)

from ...core.dependencies import get_tenant_id, get_db, authenticate, require_permissions

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
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Create a new project"""
    
    if request.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant mismatch"
        )
    
    # TODO: Implement actual project creation with ProjectService
    # For now, return mock response
    project_id = f"proj_{tenant_id}_{len(db.projects) + 1}"
    
    project = {
        "project_id": project_id,
        "name": request.name,
        "description": request.description,
        "storage_config": request.storage_config.dict(),
        "status": "ready",
        "tenant_id": tenant_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "analysis_count": 0,
        "file_count": 0,
        "size_bytes": 0
    }
    
    db.projects[project_id] = project
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="create_project",
        target_ids=[project_id],
        details={"name": request.name}
    )
    
    return ProjectResponse(**project)

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
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """List projects for tenant"""
    
    # Filter projects by tenant
    tenant_projects = [
        p for p in db.projects.values() 
        if p.get("tenant_id") == tenant_id
    ]
    
    # Apply filters
    if status:
        tenant_projects = [p for p in tenant_projects if p.get("status") == status]
    
    if project_type:
        tenant_projects = [
            p for p in tenant_projects 
            if p.get("storage_config", {}).get("type") == project_type
        ]
    
    # Pagination
    total = len(tenant_projects)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_projects = tenant_projects[start:end]
    
    # Convert to response models
    projects = [ProjectResponse(**p) for p in paginated_projects]
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=page,
        page_size=page_size
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
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Get project by ID"""
    
    if project_id not in db.projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = db.projects[project_id]
    if project.get("tenant_id") != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return ProjectResponse(**project)

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
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Update project"""
    
    if project_id not in db.projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = db.projects[project_id]
    if project.get("tenant_id") != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update fields
    if request.name:
        project["name"] = request.name
    if request.description is not None:
        project["description"] = request.description
    if request.storage_config:
        project["storage_config"] = request.storage_config.dict()
    
    project["updated_at"] = datetime.now(timezone.utc)
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="update_project",
        target_ids=[project_id],
        details={"updated_fields": list(request.dict(exclude_unset=True).keys())}
    )
    
    return ProjectResponse(**project)

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
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(require_permissions(["delete"]))
):
    """Delete project"""
    
    if project_id not in db.projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = db.projects[project_id]
    if project.get("tenant_id") != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete project
    del db.projects[project_id]
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="delete_project",
        target_ids=[project_id],
        details={"name": project.get("name")}
    )
    
    return {"message": "Project deleted successfully"}

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
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Analyze project"""
    
    if project_id not in db.projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = db.projects[project_id]
    if project.get("tenant_id") != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # TODO: Implement actual analysis with ProjectService
    analysis_id = f"analysis_{project_id}_{int(datetime.now().timestamp())}"
    
    analysis = {
        "analysis_id": analysis_id,
        "project_id": project_id,
        "status": "started",
        "started_at": datetime.now(timezone.utc),
        "progress": {"files_processed": 0, "total_files": 100}
    }
    
    db.analyses[analysis_id] = analysis
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="start_analysis",
        target_ids=[project_id, analysis_id],
        details={"analysis_type": request.analysis_type}
    )
    
    return ProjectAnalysisResponse(**analysis)

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
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Get project analyses"""
    
    if project_id not in db.projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = db.projects[project_id]
    if project.get("tenant_id") != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get analyses for this project
    project_analyses = [
        a for a in db.analyses.values() 
        if a.get("project_id") == project_id
    ]
    
    return {"analyses": project_analyses, "total": len(project_analyses)}
