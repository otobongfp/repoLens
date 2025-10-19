# Shared API models
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# Enums
class Plan(str, Enum):
    SHARED = "shared"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class VerificationStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING = "pending"


class ProposalStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_HUMAN = "needs_human"


class IndexingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# Repository Models
class RepoAnalysisRequest(BaseModel):
    tenant_id: str
    repo_url: str
    branch: Optional[str] = None
    commit: Optional[str] = None


class RepoAnalysisResponse(BaseModel):
    job_id: str
    repo_id: str
    status: IndexingStatus


# Requirement Models
class RequirementExtractRequest(BaseModel):
    tenant_id: str
    repo_id: Optional[str] = None
    text: str
    source: str


class RequirementExtractResponse(BaseModel):
    requirements: list[dict[str, Any]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RequirementMatchRequest(BaseModel):
    tenant_id: str
    top_k: int = 10


class RequirementMatchResponse(BaseModel):
    candidates: list[dict[str, Any]]


class RequirementVerifyRequest(BaseModel):
    tenant_id: str
    user_id: str
    function_id: str
    status: VerificationStatus
    note: Optional[str] = None


class RequirementVerifyResponse(BaseModel):
    verification_id: str


# Action Proposal Models
class ActionProposalRequest(BaseModel):
    tenant_id: str
    repo_id: str
    proposer_id: Optional[str] = None
    patch_s3: str
    rationale: str
    tests: list[str] = []


class ActionProposalResponse(BaseModel):
    proposal_id: str
    status: ProposalStatus


class ActionApprovalRequest(BaseModel):
    approver_id: str
    note: Optional[str] = None


# Admin Models
class UsageMetrics(BaseModel):
    active_repos: int
    vector_count: int
    storage_bytes: int
    api_requests: int
    limits: dict[str, Any]
