# RepoLens Backend - Api_Models
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

# Shared API models
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime, timezone

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
    requirements: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RequirementMatchRequest(BaseModel):
    tenant_id: str
    top_k: int = 10

class RequirementMatchResponse(BaseModel):
    candidates: List[Dict[str, Any]]

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
    tests: List[str] = []

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
    limits: Dict[str, Any]
