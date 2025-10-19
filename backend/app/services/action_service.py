# RepoLens Action Proposal Service
# AI-generated code changes with human approval workflow

import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


try:
    import openai
except ImportError:
    raise ImportError("openai not installed. Run: pip install openai")

logger = logging.getLogger(__name__)


class ProposalStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_HUMAN = "needs_human"


@dataclass
class ActionProposal:
    id: str
    tenant_id: str
    project_id: str
    analysis_id: str
    title: str
    description: str
    proposed_changes: list[dict[str, Any]]
    status: ProposalStatus
    confidence_score: float
    reasoning: str
    created_at: datetime
    updated_at: datetime
    approved_by: Optional[str] = None
    rejected_reason: Optional[str] = None


class ActionService:
    def __init__(self, neo4j_service=None, s3_service=None):
        self.neo4j_service = neo4j_service
        self.s3_service = s3_service
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate_proposal(
        self, analysis_id: str, tenant_id: str, project_id: str
    ) -> ActionProposal:
        """Generate AI proposal based on analysis results"""
        try:
            # Get analysis results
            analysis_results = await self._get_analysis_results(analysis_id)

            # Generate proposal using AI
            proposal_data = await self._generate_ai_proposal(analysis_results)

            # Create proposal object
            proposal = ActionProposal(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                project_id=project_id,
                analysis_id=analysis_id,
                title=proposal_data.get("title", "Code Improvement Proposal"),
                description=proposal_data.get("description", ""),
                proposed_changes=proposal_data.get("changes", []),
                status=ProposalStatus.DRAFT,
                confidence_score=proposal_data.get("confidence", 0.0),
                reasoning=proposal_data.get("reasoning", ""),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            # Save to database
            await self._save_proposal(proposal)

            return proposal

        except Exception as e:
            logger.error(f"Failed to generate proposal: {e}")
            raise

    async def _get_analysis_results(self, analysis_id: str) -> dict[str, Any]:
        """Get analysis results from database"""
        # This would typically query your analysis results
        # For now, return mock data
        return {"issues": [], "metrics": {}, "recommendations": []}

    async def _generate_ai_proposal(
        self, analysis_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate proposal using OpenAI"""
        try:
            prompt = f"""
            Based on the following code analysis results, generate a proposal for code improvements:

            Analysis Results:
            {json.dumps(analysis_results, indent=2)}

            Please provide:
            1. A clear title for the proposal
            2. A detailed description of the proposed changes
            3. Specific code changes with file paths and line numbers
            4. Reasoning for each change
            5. Confidence score (0.0 to 1.0)

            Return the response as JSON.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer and refactoring specialist.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            logger.error(f"AI proposal generation failed: {e}")
            return {
                "title": "Code Improvement Proposal",
                "description": "AI-generated improvements based on analysis",
                "changes": [],
                "confidence": 0.5,
                "reasoning": "Generated based on code analysis",
            }

    async def _save_proposal(self, proposal: ActionProposal) -> None:
        """Save proposal to database"""
        try:
            if self.neo4j_service:
                cypher = """
                CREATE (p:ActionProposal {
                    id: $id,
                    tenant_id: $tenant_id,
                    project_id: $project_id,
                    analysis_id: $analysis_id,
                    title: $title,
                    description: $description,
                    proposed_changes: $proposed_changes,
                    status: $status,
                    confidence_score: $confidence_score,
                    reasoning: $reasoning,
                    created_at: $created_at,
                    updated_at: $updated_at
                })
                """

                with self.neo4j_service.driver.session() as session:
                    session.run(
                        cypher,
                        {
                            "id": proposal.id,
                            "tenant_id": proposal.tenant_id,
                            "project_id": proposal.project_id,
                            "analysis_id": proposal.analysis_id,
                            "title": proposal.title,
                            "description": proposal.description,
                            "proposed_changes": proposal.proposed_changes,
                            "status": proposal.status.value,
                            "confidence_score": proposal.confidence_score,
                            "reasoning": proposal.reasoning,
                            "created_at": proposal.created_at.isoformat(),
                            "updated_at": proposal.updated_at.isoformat(),
                        },
                    )

        except Exception as e:
            logger.error(f"Failed to save proposal: {e}")
            raise

    async def get_proposal(self, proposal_id: str) -> Optional[ActionProposal]:
        """Get proposal by ID"""
        try:
            if self.neo4j_service:
                cypher = """
                MATCH (p:ActionProposal {id: $proposal_id})
                RETURN p
                """

                with self.neo4j_service.driver.session() as session:
                    result = session.run(cypher, {"proposal_id": proposal_id})
                    record = result.single()

                    if record:
                        data = record["p"]
                        return ActionProposal(
                            id=data["id"],
                            tenant_id=data["tenant_id"],
                            project_id=data["project_id"],
                            analysis_id=data["analysis_id"],
                            title=data["title"],
                            description=data["description"],
                            proposed_changes=data["proposed_changes"],
                            status=ProposalStatus(data["status"]),
                            confidence_score=data["confidence_score"],
                            reasoning=data["reasoning"],
                            created_at=datetime.fromisoformat(data["created_at"]),
                            updated_at=datetime.fromisoformat(data["updated_at"]),
                            approved_by=data.get("approved_by"),
                            rejected_reason=data.get("rejected_reason"),
                        )

                return None

        except Exception as e:
            logger.error(f"Failed to get proposal: {e}")
            return None

    async def approve_proposal(self, proposal_id: str, approved_by: str) -> bool:
        """Approve a proposal"""
        try:
            if self.neo4j_service:
                cypher = """
                MATCH (p:ActionProposal {id: $proposal_id})
                SET p.status = $status,
                    p.approved_by = $approved_by,
                    p.updated_at = $updated_at
                """

                with self.neo4j_service.driver.session() as session:
                    session.run(
                        cypher,
                        {
                            "proposal_id": proposal_id,
                            "status": ProposalStatus.APPROVED.value,
                            "approved_by": approved_by,
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                return True

        except Exception as e:
            logger.error(f"Failed to approve proposal: {e}")
            return False

    async def reject_proposal(self, proposal_id: str, rejected_reason: str) -> bool:
        """Reject a proposal"""
        try:
            if self.neo4j_service:
                cypher = """
                MATCH (p:ActionProposal {id: $proposal_id})
                SET p.status = $status,
                    p.rejected_reason = $rejected_reason,
                    p.updated_at = $updated_at
                """

                with self.neo4j_service.driver.session() as session:
                    session.run(
                        cypher,
                        {
                            "proposal_id": proposal_id,
                            "status": ProposalStatus.REJECTED.value,
                            "rejected_reason": rejected_reason,
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                return True

        except Exception as e:
            logger.error(f"Failed to reject proposal: {e}")
            return False

    async def list_proposals(
        self, tenant_id: str, project_id: str = None, status: str = None
    ) -> list[ActionProposal]:
        """List proposals with filters"""
        try:
            proposals = []

            if self.neo4j_service:
                cypher = """
                MATCH (p:ActionProposal {tenant_id: $tenant_id})
                WHERE ($project_id IS NULL OR p.project_id = $project_id)
                AND ($status IS NULL OR p.status = $status)
                RETURN p
                ORDER BY p.created_at DESC
                """

                with self.neo4j_service.driver.session() as session:
                    result = session.run(
                        cypher,
                        {
                            "tenant_id": tenant_id,
                            "project_id": project_id,
                            "status": status,
                        },
                    )

                    for record in result:
                        data = record["p"]
                        proposal = ActionProposal(
                            id=data["id"],
                            tenant_id=data["tenant_id"],
                            project_id=data["project_id"],
                            analysis_id=data["analysis_id"],
                            title=data["title"],
                            description=data["description"],
                            proposed_changes=data["proposed_changes"],
                            status=ProposalStatus(data["status"]),
                            confidence_score=data["confidence_score"],
                            reasoning=data["reasoning"],
                            created_at=datetime.fromisoformat(data["created_at"]),
                            updated_at=datetime.fromisoformat(data["updated_at"]),
                            approved_by=data.get("approved_by"),
                            rejected_reason=data.get("rejected_reason"),
                        )
                        proposals.append(proposal)

                return proposals

        except Exception as e:
            logger.error(f"Failed to list proposals: {e}")
            return []
