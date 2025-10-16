# RepoLens Service - Project_Service Business Logic
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

# Project Management Service
import os
import shutil
import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import git
import boto3
from pathlib import Path

from ..shared.models.project_models import (
    ProjectResponse, ProjectCreateRequest, ProjectUpdateRequest,
    ProjectStatus, SourceType, SourceConfig, StorageConfig, EnvironmentConfig
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models.tenant import Project, Tenant
from app.database.models.user import User
import json

logger = logging.getLogger(__name__)

class StorageManager:
    """Handles different storage backends"""
    
    def __init__(self, config: EnvironmentConfig):
        self.config = config
        self.local_storage_path = Path("storage")
        self.local_storage_path.mkdir(exist_ok=True)
        
        # Initialize S3 client if configured
        self.s3_client = None
        if config.aws_access_key_id and config.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key,
                region_name=config.aws_region or 'us-east-1'
            )
    
    def clone_repository(self, project_id: str, source_config: SourceConfig) -> Dict[str, Any]:
        """Handle repository based on backend mode"""
        try:
            if source_config.type == SourceType.LOCAL:
                return self._handle_local_source(project_id, source_config)
            elif source_config.type == SourceType.GITHUB:
                return self._handle_github_source(project_id, source_config)
            else:
                raise ValueError(f"Unsupported source type: {source_config.type}")
                
        except Exception as e:
            logger.error(f"Failed to handle repository: {e}")
            raise
    
    def _handle_local_source(self, project_id: str, source_config: SourceConfig) -> Dict[str, Any]:
        """Handle local source - read directly, no copying needed"""
        if not source_config.local_path:
            raise ValueError("Local path required for local source")
        
        if not os.path.exists(source_config.local_path):
            raise FileNotFoundError(f"Local path not found: {source_config.local_path}")
        
        # For local backend: just validate and return the path
        # No copying needed - we'll read directly from user's path
        return {
            "source_type": "local",
            "path": source_config.local_path,  # Direct path, no copying
            "size_bytes": self._get_directory_size(Path(source_config.local_path))
        }
    
    def _handle_github_source(self, project_id: str, source_config: SourceConfig) -> Dict[str, Any]:
        """Handle GitHub source - clone to workspace"""
        if not source_config.github_url:
            raise ValueError("GitHub URL required for GitHub source")
        
        project_path = self.local_storage_path / project_id
        project_path.mkdir(exist_ok=True)
        
        try:
            repo = git.Repo.clone_from(
                source_config.github_url,
                project_path,
                branch=source_config.branch or "main"
            )
            return {
                "source_type": "github",
                "path": str(project_path),
                "url": source_config.github_url,
                "branch": source_config.branch or "main",
                "size_bytes": self._get_directory_size(project_path)
            }
        except git.GitError as e:
            raise ValueError(f"Failed to clone GitHub repository: {e}")
    
    def _upload_directory_to_s3(self, local_path: Path, bucket: str, prefix: str):
        """Upload directory to S3"""
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file = Path(root) / file
                relative_path = local_file.relative_to(local_path)
                s3_key = f"{prefix}/{relative_path}".replace("\\", "/")
                
                self.s3_client.upload_file(
                    str(local_file),
                    bucket,
                    s3_key
                )
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def get_project_path(self, project_id: str, source_config: SourceConfig) -> str:
        """Get the path to project files"""
        if source_config.type in [SourceType.LOCAL, SourceType.GITHUB, SourceType.GIT]:
            return str(self.local_storage_path / project_id)
        else:
            raise ValueError(f"Unsupported source type: {source_config.type}")

class ProjectService:
    """Project management service"""
    
    def __init__(self, storage_manager: StorageManager):
        self.storage_manager = storage_manager
        self.db_url = os.getenv("PGVECTOR_DB_URL")
        if not self.db_url:
            raise ValueError("PGVECTOR_DB_URL environment variable is required")
    
    async def create_project(self, request: ProjectCreateRequest, db: AsyncSession, user_id: str) -> ProjectResponse:
        """Create a new project using SQLAlchemy"""
        try:
            project_id = str(uuid.uuid4())
            
            # Clone repository
            storage_info = self.storage_manager.clone_repository(project_id, request.source_config)
            
            # Create project record using SQLAlchemy
            project = Project(
                id=project_id,
                name=request.name,
                description=request.description,
                source_type=request.source_config.type.value,
                source_url=request.source_config.github_url or request.source_config.git_url,
                source_path=request.source_config.local_path,
                status=ProjectStatus.READY,
                tenant_id=request.tenant_id,
                owner_id=user_id,
                file_count=storage_info.get("file_count", 0),
                size_bytes=storage_info.get("size_bytes", 0),
                analysis_count=0
            )
            
            db.add(project)
            await db.commit()
            await db.refresh(project)
            
            logger.info(f"Created project {project_id} in database")
            
            return ProjectResponse(
                project_id=project_id,
                name=request.name,
                description=request.description,
                source_config=request.source_config,
                status=ProjectStatus.READY,
                tenant_id=request.tenant_id,
                created_at=project.created_at,
                updated_at=project.updated_at,
                file_count=storage_info.get("file_count", 0),
                size_bytes=storage_info.get("size_bytes", 0)
            )
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            await db.rollback()
            raise
    
    async def get_project(self, db: AsyncSession, project_id: str, tenant_id: str) -> Optional[ProjectResponse]:
        """Get project by ID using SQLAlchemy"""
        try:
            result = await db.execute(
                select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
            )
            project_record = result.scalar_one_or_none()
            
            if project_record:
                # Reconstruct source_config from separate columns
                source_config_data = {
                    "type": project_record.source_type,
                    "github_url": project_record.source_url if project_record.source_type == "github" else None,
                    "git_url": project_record.source_url if project_record.source_type == "git" else None,
                    "local_path": project_record.source_path if project_record.source_type == "local" else None
                }
                source_config = SourceConfig(**source_config_data)
                
                return ProjectResponse(
                    project_id=str(project_record.id),
                    name=project_record.name,
                    description=project_record.description,
                    source_config=source_config,
                    status=ProjectStatus(project_record.status),
                    tenant_id=str(project_record.tenant_id),
                    created_at=project_record.created_at.isoformat() if project_record.created_at else None,
                    updated_at=project_record.updated_at.isoformat() if project_record.updated_at else None,
                    last_analyzed=project_record.last_analyzed_at.isoformat() if project_record.last_analyzed_at else None,
                    analysis_count=project_record.analysis_count or 0,
                    file_count=project_record.file_count,
                    size_bytes=project_record.size_bytes
                )
            
            return None
                
        except Exception as e:
            logger.error(f"Failed to get project: {e}")
            return None
    
    async def list_projects(self, db: AsyncSession, tenant_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """List projects for tenant using SQLAlchemy"""
        try:
            from sqlalchemy import func
            
            # Get total count
            count_result = await db.execute(select(func.count(Project.id)).where(Project.tenant_id == tenant_id))
            total = count_result.scalar()
            
            # Get paginated projects
            offset = (page - 1) * page_size
            result = await db.execute(
                select(Project)
                .where(Project.tenant_id == tenant_id)
                .order_by(Project.updated_at.desc())
                .limit(page_size)
                .offset(offset)
            )
            projects_records = result.scalars().all()
            
            projects = []
            for project_record in projects_records:
                # Reconstruct source_config from separate columns
                source_config_data = {
                    "type": project_record.source_type,
                    "github_url": project_record.source_url if project_record.source_type == "github" else None,
                    "git_url": project_record.source_url if project_record.source_type == "git" else None,
                    "local_path": project_record.source_path if project_record.source_type == "local" else None
                }
                source_config = SourceConfig(**source_config_data)
                
                project = ProjectResponse(
                    project_id=str(project_record.id),
                    name=project_record.name,
                    description=project_record.description,
                    source_config=source_config,
                    status=ProjectStatus(project_record.status),
                    tenant_id=str(project_record.tenant_id),
                    created_at=project_record.created_at.isoformat() if project_record.created_at else None,
                    updated_at=project_record.updated_at.isoformat() if project_record.updated_at else None,
                    last_analyzed=project_record.last_analyzed_at.isoformat() if project_record.last_analyzed_at else None,
                    analysis_count=project_record.analysis_count or 0,
                    file_count=project_record.file_count,
                    size_bytes=project_record.size_bytes
                )
                projects.append(project)
            
            return {
                "projects": projects,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
                
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return {"projects": [], "total": 0, "page": page, "page_size": page_size}
    
    async def update_project(self, db: AsyncSession, project_id: str, tenant_id: str, request: ProjectUpdateRequest) -> Optional[ProjectResponse]:
        """Update project using SQLAlchemy"""
        try:
            result = await db.execute(
                select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
            )
            project_record = result.scalar_one_or_none()
            
            if not project_record:
                return None
            
            # Update fields
            if request.name:
                project_record.name = request.name
            
            if request.description is not None:
                project_record.description = request.description
            
            if request.source_config:
                project_record.source_type = request.source_config.type.value
                project_record.source_url = request.source_config.github_url or request.source_config.git_url
                project_record.source_path = request.source_config.local_path
            
            project_record.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(project_record)
            
            # Reconstruct source_config from separate columns
            source_config_data = {
                "type": project_record.source_type,
                "github_url": project_record.source_url if project_record.source_type == "github" else None,
                "git_url": project_record.source_url if project_record.source_type == "git" else None,
                "local_path": project_record.source_path if project_record.source_type == "local" else None
            }
            source_config = SourceConfig(**source_config_data)
            
            return ProjectResponse(
                project_id=str(project_record.id),
                name=project_record.name,
                description=project_record.description,
                source_config=source_config,
                status=ProjectStatus(project_record.status),
                tenant_id=str(project_record.tenant_id),
                created_at=project_record.created_at.isoformat() if project_record.created_at else None,
                updated_at=project_record.updated_at.isoformat() if project_record.updated_at else None,
                last_analyzed=project_record.last_analyzed_at.isoformat() if project_record.last_analyzed_at else None,
                analysis_count=project_record.analysis_count or 0,
                file_count=project_record.file_count,
                size_bytes=project_record.size_bytes
            )
                
        except Exception as e:
            logger.error(f"Failed to update project: {e}")
            await db.rollback()
            return None
    
    async def delete_project(self, db: AsyncSession, project_id: str, tenant_id: str) -> bool:
        """Delete project using SQLAlchemy"""
        try:
            # Get project info first
            result = await db.execute(
                select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
            )
            project_record = result.scalar_one_or_none()
            
            if not project_record:
                return False
            
            # Reconstruct source_config for storage deletion
            source_config_data = {
                "type": project_record.source_type,
                "github_url": project_record.source_url if project_record.source_type == "github" else None,
                "git_url": project_record.source_url if project_record.source_type == "git" else None,
                "local_path": project_record.source_path if project_record.source_type == "local" else None
            }
            source_config = SourceConfig(**source_config_data)
            
            # Delete from storage
            self._delete_project_storage(project_id, source_config)
            
            # Delete from database
            await db.delete(project_record)
            await db.commit()
            
            logger.info(f"Deleted project {project_id} from database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            await db.rollback()
            return False
    
    
    def _delete_project_storage(self, project_id: str, source_config: SourceConfig):
        """Delete project from local workspace"""
        try:
            if source_config.type in [SourceType.LOCAL, SourceType.GITHUB, SourceType.GIT]:
                project_path = Path("storage") / project_id
                if project_path.exists():
                    shutil.rmtree(project_path)
            # Note: S3 storage is for analysis results, not source code
        except Exception as e:
            logger.error(f"Failed to delete project storage: {e}")
    
    def _count_files(self, project_id: str, source_config: SourceConfig) -> int:
        """Count files in project"""
        try:
            if source_config.type == SourceType.LOCAL:
                # For local source, count files directly from the path
                return sum(1 for _ in Path(source_config.local_path).rglob('*') if _.is_file())
            elif source_config.type == SourceType.GITHUB:
                # For cloned repos, count files in workspace
                project_path = Path("storage") / project_id
                if project_path.exists():
                    return sum(1 for _ in project_path.rglob('*') if _.is_file())
            return 0
        except Exception as e:
            logger.error(f"Failed to count files: {e}")
            return 0
