# Project Management Models
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class SourceType(str, Enum):
    """Source code location types"""
    LOCAL = "local"      # Local file path
    GITHUB = "github"    # GitHub repository

class ProjectStatus(str, Enum):
    """Project analysis status"""
    CREATED = "created"
    CLONING = "cloning"
    READY = "ready"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    ERROR = "error"

class SourceConfig(BaseModel):
    """Source code configuration - where the code comes from"""
    type: SourceType
    local_path: Optional[str] = None      # Path to local code
    github_url: Optional[str] = None       # GitHub repository URL
    branch: Optional[str] = "main"         # Git branch to analyze

class StorageConfig(BaseModel):
    """Storage configuration for analysis results (S3, etc.)"""
    use_s3: bool = False
    s3_bucket: Optional[str] = None
    s3_prefix: Optional[str] = None
    local_cache_path: Optional[str] = None  # Where to cache analysis results locally

class ProjectCreateRequest(BaseModel):
    """Request to create a new project"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    source_config: SourceConfig
    tenant_id: str

class ProjectUpdateRequest(BaseModel):
    """Request to update a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    source_config: Optional[SourceConfig] = None

class ProjectResponse(BaseModel):
    """Project response model"""
    project_id: str
    name: str
    description: Optional[str]
    source_config: SourceConfig
    storage_config: Optional[StorageConfig] = None
    status: ProjectStatus
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    last_analyzed: Optional[datetime] = None
    analysis_count: int = 0
    file_count: Optional[int] = None
    size_bytes: Optional[int] = None

class ProjectListResponse(BaseModel):
    """List of projects response"""
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int

class ProjectAnalysisRequest(BaseModel):
    """Request to analyze a project"""
    project_id: str
    tenant_id: str
    analysis_type: str = "full"  # full, incremental, requirements_only
    force_refresh: bool = False

class ProjectAnalysisResponse(BaseModel):
    """Project analysis response"""
    analysis_id: str
    project_id: str
    status: str
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    progress: Dict[str, Any] = {}

class EnvironmentConfig(BaseModel):
    """Environment configuration for user settings"""
    openai_api_key: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None
    s3_bucket: Optional[str] = None
    neo4j_uri: Optional[str] = None
    neo4j_user: Optional[str] = None
    neo4j_password: Optional[str] = None
    use_local_backend: bool = True
    backend_url: Optional[str] = None

class UserSettingsRequest(BaseModel):
    """Request to update user settings"""
    environment_config: EnvironmentConfig
    tenant_id: str

class UserSettingsResponse(BaseModel):
    """User settings response"""
    environment_config: EnvironmentConfig
    tenant_id: str
    updated_at: datetime
