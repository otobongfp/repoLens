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
from .neo4j_service import Neo4jService

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
    
    def __init__(self, neo4j_service, storage_manager: StorageManager):
        self.neo4j_service = neo4j_service
        self.storage_manager = storage_manager
    
    def create_project(self, request: ProjectCreateRequest) -> ProjectResponse:
        """Create a new project"""
        try:
            project_id = str(uuid.uuid4())
            
            # Clone repository
            storage_info = self.storage_manager.clone_repository(project_id, request.source_config)
            
            # Create project record
            project_data = {
                "project_id": project_id,
                "name": request.name,
                "description": request.description,
                "source_config": request.source_config.dict(),
                "status": ProjectStatus.READY,
                "tenant_id": request.tenant_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "storage_info": storage_info
            }
            
            # Store in Neo4j
            self._store_project(project_data)
            
            return ProjectResponse(
                project_id=project_id,
                name=request.name,
                description=request.description,
                source_config=request.source_config,
                status=ProjectStatus.READY,
                tenant_id=request.tenant_id,
                created_at=project_data["created_at"],
                updated_at=project_data["updated_at"],
                file_count=self._count_files(project_id, request.source_config),
                size_bytes=storage_info.get("size_bytes")
            )
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise
    
    def get_project(self, project_id: str, tenant_id: str) -> Optional[ProjectResponse]:
        """Get project by ID"""
        try:
            cypher = """
            MATCH (p:Project {project_id: $project_id, tenant_id: $tenant_id})
            RETURN p.project_id as project_id,
                   p.name as name,
                   p.description as description,
                   p.source_config as source_config,
                   p.status as status,
                   p.tenant_id as tenant_id,
                   p.created_at as created_at,
                   p.updated_at as updated_at,
                   p.last_analyzed as last_analyzed,
                   p.analysis_count as analysis_count,
                   p.file_count as file_count,
                   p.size_bytes as size_bytes
            """
            
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, {
                    'project_id': project_id,
                    'tenant_id': tenant_id
                })
                
                record = result.single()
                if record:
                    source_config = SourceConfig(**record['source_config'])
                    return ProjectResponse(
                        project_id=record['project_id'],
                        name=record['name'],
                        description=record['description'],
                        source_config=source_config,
                        status=ProjectStatus(record['status']),
                        tenant_id=record['tenant_id'],
                        created_at=record['created_at'],
                        updated_at=record['updated_at'],
                        last_analyzed=record['last_analyzed'],
                        analysis_count=record['analysis_count'] or 0,
                        file_count=record['file_count'],
                        size_bytes=record['size_bytes']
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get project: {e}")
            return None
    
    def list_projects(self, tenant_id: str, page: int = 1, page_size: int = 20) -> List[ProjectResponse]:
        """List projects for tenant"""
        try:
            skip = (page - 1) * page_size
            
            cypher = """
            MATCH (p:Project {tenant_id: $tenant_id})
            RETURN p.project_id as project_id,
                   p.name as name,
                   p.description as description,
                   p.source_config as source_config,
                   p.status as status,
                   p.tenant_id as tenant_id,
                   p.created_at as created_at,
                   p.updated_at as updated_at,
                   p.last_analyzed as last_analyzed,
                   p.analysis_count as analysis_count,
                   p.file_count as file_count,
                   p.size_bytes as size_bytes
            ORDER BY p.updated_at DESC
            SKIP $skip
            LIMIT $limit
            """
            
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, {
                    'tenant_id': tenant_id,
                    'skip': skip,
                    'limit': page_size
                })
                
                projects = []
                for record in result:
                    source_config = SourceConfig(**record['source_config'])
                    project = ProjectResponse(
                        project_id=record['project_id'],
                        name=record['name'],
                        description=record['description'],
                        source_config=source_config,
                        status=ProjectStatus(record['status']),
                        tenant_id=record['tenant_id'],
                        created_at=record['created_at'],
                        updated_at=record['updated_at'],
                        last_analyzed=record['last_analyzed'],
                        analysis_count=record['analysis_count'] or 0,
                        file_count=record['file_count'],
                        size_bytes=record['size_bytes']
                    )
                    projects.append(project)
                
                return projects
                
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []
    
    def update_project(self, project_id: str, tenant_id: str, request: ProjectUpdateRequest) -> Optional[ProjectResponse]:
        """Update project"""
        try:
            update_fields = []
            params = {'project_id': project_id, 'tenant_id': tenant_id}
            
            if request.name:
                update_fields.append("p.name = $name")
                params['name'] = request.name
            
            if request.description is not None:
                update_fields.append("p.description = $description")
                params['description'] = request.description
            
            if request.source_config:
                update_fields.append("p.source_config = $source_config")
                params['source_config'] = request.source_config.dict()
            
            if not update_fields:
                return self.get_project(project_id, tenant_id)
            
            update_fields.append("p.updated_at = datetime()")
            
            cypher = f"""
            MATCH (p:Project {{project_id: $project_id, tenant_id: $tenant_id}})
            SET {', '.join(update_fields)}
            RETURN p.project_id as project_id,
                   p.name as name,
                   p.description as description,
                   p.source_config as source_config,
                   p.status as status,
                   p.tenant_id as tenant_id,
                   p.created_at as created_at,
                   p.updated_at as updated_at,
                   p.last_analyzed as last_analyzed,
                   p.analysis_count as analysis_count,
                   p.file_count as file_count,
                   p.size_bytes as size_bytes
            """
            
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, params)
                record = result.single()
                
                if record:
                    source_config = SourceConfig(**record['source_config'])
                    return ProjectResponse(
                        project_id=record['project_id'],
                        name=record['name'],
                        description=record['description'],
                        source_config=source_config,
                        status=ProjectStatus(record['status']),
                        tenant_id=record['tenant_id'],
                        created_at=record['created_at'],
                        updated_at=record['updated_at'],
                        last_analyzed=record['last_analyzed'],
                        analysis_count=record['analysis_count'] or 0,
                        file_count=record['file_count'],
                        size_bytes=record['size_bytes']
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to update project: {e}")
            return None
    
    def delete_project(self, project_id: str, tenant_id: str) -> bool:
        """Delete project"""
        try:
            # Get project info first
            project = self.get_project(project_id, tenant_id)
            if not project:
                return False
            
            # Delete from storage
            self._delete_project_storage(project_id, project.source_config)
            
            # Delete from Neo4j
            cypher = """
            MATCH (p:Project {project_id: $project_id, tenant_id: $tenant_id})
            DETACH DELETE p
            """
            
            with self.neo4j_service.driver.session() as session:
                session.run(cypher, {
                    'project_id': project_id,
                    'tenant_id': tenant_id
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            return False
    
    def _store_project(self, project_data: Dict[str, Any]):
        """Store project in Neo4j"""
        cypher = """
        CREATE (p:Project {
            project_id: $project_id,
            name: $name,
            description: $description,
            source_config: $source_config,
            status: $status,
            tenant_id: $tenant_id,
            created_at: datetime(),
            updated_at: datetime(),
            analysis_count: 0,
            file_count: 0,
            size_bytes: 0
        })
        
        MERGE (t:Tenant {tenant_id: $tenant_id})
        MERGE (t)-[:OWNS]->(p)
        """
        
        with self.neo4j_service.driver.session() as session:
            session.run(cypher, {
                'project_id': project_data['project_id'],
                'name': project_data['name'],
                'description': project_data['description'],
                'source_config': project_data['source_config'],
                'status': project_data['status'].value,
                'tenant_id': project_data['tenant_id']
            })
    
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
