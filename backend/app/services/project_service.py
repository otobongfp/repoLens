# Project Management Service
import asyncio
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import git
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.project import Project

from ..shared.models.project_models import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectStatus,
    ProjectUpdateRequest,
    SourceConfig,
    SourceType,
)


logger = logging.getLogger(__name__)


class StorageManager:
    def __init__(self):
        self.local_storage_path = Path("storage")
        self.local_storage_path.mkdir(exist_ok=True)

    def get_project_path(self, project_id: str) -> Path:
        """Get local project storage path"""
        return self.local_storage_path / project_id

    def ensure_project_directory(self, project_id: str) -> Path:
        """Ensure project directory exists"""
        project_path = self.get_project_path(project_id)
        project_path.mkdir(parents=True, exist_ok=True)
        return project_path

    def delete_project_directory(self, project_id: str) -> bool:
        """Delete project directory"""
        try:
            project_path = self.get_project_path(project_id)
            if project_path.exists():
                shutil.rmtree(project_path)
            return True
        except Exception as e:
            logger.error(f"Failed to delete project directory: {e}")
            return False


class ProjectService:
    def __init__(self):
        self.storage_manager = StorageManager()

    async def create_project(
        self,
        db: AsyncSession,
        request: ProjectCreateRequest,
        tenant_id: str,
        user_id: str,
    ) -> Optional[ProjectResponse]:
        """Create new project"""
        try:
            project_id = str(uuid.uuid4())

            # Create project record
            project_record = Project(
                id=project_id,
                tenant_id=tenant_id,
                owner_id=user_id,
                name=request.name,
                description=request.description,
                source_type=request.source_config.type.value,
                source_url=request.source_config.github_url,
                source_path=request.source_config.local_path,
                status="created",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                file_count=0,  # Set initial values
                size_bytes=0,
            )

            db.add(project_record)
            await db.commit()
            await db.refresh(project_record)

            # Clone the repository in the background
            try:
                await self._clone_repository(
                    str(project_record.id), request.source_config
                )

                # Update file count and size after cloning
                file_count = await self._count_files(
                    str(project_record.id), request.source_config
                )
                size_bytes = await self._calculate_size(
                    str(project_record.id), request.source_config
                )

                # Update the project record with actual values
                project_record.file_count = file_count
                project_record.size_bytes = size_bytes
                project_record.status = "ready"
                await db.commit()
                await db.refresh(project_record)

            except Exception as e:
                logger.warning(
                    f"Failed to clone repository for project {project_record.id}: {e}"
                )
                # Don't fail the project creation, just log the warning

            return ProjectResponse(
                project_id=str(project_record.id),
                name=project_record.name,
                description=project_record.description,
                source_config=request.source_config,
                status=project_record.status,
                tenant_id=str(project_record.tenant_id),
                owner_id=str(project_record.owner_id),
                created_at=project_record.created_at.isoformat(),
                updated_at=project_record.updated_at.isoformat(),
                last_analyzed=None,
                analysis_count=0,
                file_count=project_record.file_count,
                size_bytes=project_record.size_bytes,
            )

        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            await db.rollback()
            return None

    async def get_project(
        self, db: AsyncSession, project_id: str, tenant_id: str
    ) -> Optional[ProjectResponse]:
        """Get project by ID"""
        try:
            result = await db.execute(
                select(Project).where(
                    Project.id == project_id, Project.tenant_id == tenant_id
                )
            )
            project_record = result.scalar_one_or_none()

            if not project_record:
                return None

            # Reconstruct source_config
            source_config_data = {
                "type": project_record.source_type,
                "github_url": (
                    project_record.source_url
                    if project_record.source_type == "github"
                    else None
                ),
                "git_url": (
                    project_record.source_url
                    if project_record.source_type == "git"
                    else None
                ),
                "local_path": (
                    project_record.source_path
                    if project_record.source_type == "local"
                    else None
                ),
            }
            source_config = SourceConfig(**source_config_data)

            return ProjectResponse(
                project_id=str(project_record.id),
                name=project_record.name,
                description=project_record.description,
                source_config=source_config,
                status=ProjectStatus(project_record.status),
                tenant_id=str(project_record.tenant_id),
                owner_id=str(project_record.owner_id),
                created_at=(
                    project_record.created_at.isoformat()
                    if project_record.created_at
                    else None
                ),
                updated_at=(
                    project_record.updated_at.isoformat()
                    if project_record.updated_at
                    else None
                ),
                last_analyzed=(
                    project_record.last_analyzed_at.isoformat()
                    if project_record.last_analyzed_at
                    else None
                ),
                analysis_count=project_record.analysis_count or 0,
                file_count=project_record.file_count,
                size_bytes=project_record.size_bytes,
            )

        except Exception as e:
            logger.error(f"Failed to get project: {e}")
            return None

    async def list_projects(
        self, db: AsyncSession, tenant_id: str
    ) -> list[ProjectResponse]:
        """List all projects for tenant"""
        try:
            result = await db.execute(
                select(Project)
                .where(Project.tenant_id == tenant_id)
                .order_by(Project.created_at.desc())
            )
            project_records = result.scalars().all()

            projects = []
            for project_record in project_records:
                # Reconstruct source_config
                source_config_data = {
                    "type": project_record.source_type,
                    "github_url": (
                        project_record.source_url
                        if project_record.source_type == "github"
                        else None
                    ),
                    "git_url": (
                        project_record.source_url
                        if project_record.source_type == "git"
                        else None
                    ),
                    "local_path": (
                        project_record.source_path
                        if project_record.source_type == "local"
                        else None
                    ),
                }
                source_config = SourceConfig(**source_config_data)

                projects.append(
                    ProjectResponse(
                        project_id=str(project_record.id),
                        name=project_record.name,
                        description=project_record.description,
                        source_config=source_config,
                        status=ProjectStatus(project_record.status),
                        tenant_id=str(project_record.tenant_id),
                        owner_id=str(project_record.owner_id),
                        created_at=(
                            project_record.created_at.isoformat()
                            if project_record.created_at
                            else None
                        ),
                        updated_at=(
                            project_record.updated_at.isoformat()
                            if project_record.updated_at
                            else None
                        ),
                        last_analyzed=(
                            project_record.last_analyzed_at.isoformat()
                            if project_record.last_analyzed_at
                            else None
                        ),
                        analysis_count=project_record.analysis_count or 0,
                        file_count=project_record.file_count,
                        size_bytes=project_record.size_bytes,
                    )
                )

            return projects

        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []

    async def update_project(
        self,
        db: AsyncSession,
        project_id: str,
        tenant_id: str,
        request: ProjectUpdateRequest,
    ) -> Optional[ProjectResponse]:
        """Update project"""
        try:
            result = await db.execute(
                select(Project).where(
                    Project.id == project_id, Project.tenant_id == tenant_id
                )
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
                project_record.source_url = request.source_config.github_url
                project_record.source_path = request.source_config.local_path

            project_record.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(project_record)

            # Reconstruct source_config
            source_config_data = {
                "type": project_record.source_type,
                "github_url": (
                    project_record.source_url
                    if project_record.source_type == "github"
                    else None
                ),
                "git_url": (
                    project_record.source_url
                    if project_record.source_type == "git"
                    else None
                ),
                "local_path": (
                    project_record.source_path
                    if project_record.source_type == "local"
                    else None
                ),
            }
            source_config = SourceConfig(**source_config_data)

            return ProjectResponse(
                project_id=str(project_record.id),
                name=project_record.name,
                description=project_record.description,
                source_config=source_config,
                status=ProjectStatus(project_record.status),
                tenant_id=str(project_record.tenant_id),
                owner_id=str(project_record.owner_id),
                created_at=(
                    project_record.created_at.isoformat()
                    if project_record.created_at
                    else None
                ),
                updated_at=(
                    project_record.updated_at.isoformat()
                    if project_record.updated_at
                    else None
                ),
                last_analyzed=(
                    project_record.last_analyzed_at.isoformat()
                    if project_record.last_analyzed_at
                    else None
                ),
                analysis_count=project_record.analysis_count or 0,
                file_count=project_record.file_count,
                size_bytes=project_record.size_bytes,
            )

        except Exception as e:
            logger.error(f"Failed to update project: {e}")
            await db.rollback()
            return None

    async def delete_project(
        self, db: AsyncSession, project_id: str, tenant_id: str
    ) -> bool:
        """Delete project"""
        try:
            # Get project info first
            result = await db.execute(
                select(Project).where(
                    Project.id == project_id, Project.tenant_id == tenant_id
                )
            )
            project_record = result.scalar_one_or_none()

            if not project_record:
                return False

            # Reconstruct source_config for storage deletion
            source_config_data = {
                "type": project_record.source_type,
                "github_url": (
                    project_record.source_url
                    if project_record.source_type == "github"
                    else None
                ),
                "git_url": (
                    project_record.source_url
                    if project_record.source_type == "git"
                    else None
                ),
                "local_path": (
                    project_record.source_path
                    if project_record.source_type == "local"
                    else None
                ),
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

    async def _clone_repository(self, project_id: str, source_config: SourceConfig):
        """Clone repository to local storage"""
        try:
            project_path = self.storage_manager.ensure_project_directory(project_id)

            if source_config.type == SourceType.GITHUB:
                repo_url = source_config.github_url
                if not repo_url.endswith(".git"):
                    repo_url += ".git"

                # Use asyncio to run git clone in a thread pool to avoid async issues
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: git.Repo.clone_from(repo_url, project_path)
                )
                logger.info(f"Cloned repository to {project_path}")
            else:
                return

        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")

    async def _count_files(self, project_id: str, source_config: SourceConfig) -> int:
        """Count files in project"""
        try:
            if source_config.type == SourceType.LOCAL:

                def count_local_files():
                    return sum(
                        1
                        for _ in Path(source_config.local_path).rglob("*")
                        if _.is_file()
                    )

                return await asyncio.get_event_loop().run_in_executor(
                    None, count_local_files
                )
            elif source_config.type == SourceType.GITHUB:

                def count_github_files():
                    project_path = self.storage_manager.get_project_path(project_id)
                    if project_path.exists():
                        return sum(1 for _ in project_path.rglob("*") if _.is_file())
                    return 0

                return await asyncio.get_event_loop().run_in_executor(
                    None, count_github_files
                )
            return 0
        except Exception as e:
            logger.error(f"Failed to count files: {e}")
            return 0

    async def _calculate_size(
        self, project_id: str, source_config: SourceConfig
    ) -> int:
        """Calculate project size in bytes"""
        try:
            if source_config.type == SourceType.LOCAL:

                def calculate_local_size():
                    return sum(
                        f.stat().st_size
                        for f in Path(source_config.local_path).rglob("*")
                        if f.is_file()
                    )

                return await asyncio.get_event_loop().run_in_executor(
                    None, calculate_local_size
                )
            elif source_config.type == SourceType.GITHUB:

                def calculate_github_size():
                    project_path = self.storage_manager.get_project_path(project_id)
                    if project_path.exists():
                        return sum(
                            f.stat().st_size
                            for f in project_path.rglob("*")
                            if f.is_file()
                        )
                    return 0

                return await asyncio.get_event_loop().run_in_executor(
                    None, calculate_github_size
                )
            return 0
        except Exception as e:
            logger.error(f"Failed to calculate size: {e}")
            return 0

    def _delete_project_storage(self, project_id: str, source_config: SourceConfig):
        """Delete project from local workspace"""
        try:
            if source_config.type in [
                SourceType.LOCAL,
                SourceType.GITHUB,
                SourceType.GITHUB,
            ]:
                self.storage_manager.delete_project_directory(project_id)
        except Exception as e:
            logger.error(f"Failed to delete project storage: {e}")
