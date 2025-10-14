# RepoLens Action Proposal Service
# AI-generated code changes with human approval workflow

import os
import logging
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from dataclasses import dataclass
from enum import Enum

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
    """Action proposal with metadata"""
    proposal_id: str
    tenant_id: str
    repo_id: str
    proposer_id: str
    patch_s3_path: str
    rationale: str
    tests_to_run: List[str]
    estimated_risk: float
    status: ProposalStatus
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

@dataclass
class CodeChange:
    """Code change representation"""
    file_path: str
    change_type: str  # 'add', 'modify', 'delete'
    old_content: Optional[str]
    new_content: Optional[str]
    line_number: int
    context: str

class ActionGenerator:
    """AI-powered action generator"""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        
        # Exact prompt from directive
        self.action_prompt = """
SYSTEM: You are a deterministic code change generator. Given a requirement and a code snippet, generate a minimal, safe diff patch. Do not hallucinate. Only modify the provided snippet. Output must be ONLY valid JSON.

USER: 
Requirement: <<REQUIREMENT_TEXT>>
Code Snippet: <<CODE_SNIPPET>>
File Path: <<FILE_PATH>>

ACTION JSON FORMAT:
{
  "file_path": "<file_path>",
  "change_type": "add|modify|delete",
  "old_content": "<original content>",
  "new_content": "<modified content>",
  "line_number": <line_number>,
  "context": "<explanation>",
  "rationale": "<why this change>",
  "tests_to_run": ["<test1>", "<test2>"],
  "estimated_risk": 0.0-1.0
}
"""
    
    def generate_action(self, requirement: str, code_snippet: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Generate action proposal for requirement"""
        try:
            # Replace placeholders in prompt
            prompt = self.action_prompt.replace("<<REQUIREMENT_TEXT>>", requirement)
            prompt = prompt.replace("<<CODE_SNIPPET>>", code_snippet)
            prompt = prompt.replace("<<FILE_PATH>>", file_path)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt.split("USER:")[0].strip()},
                    {"role": "user", "content": prompt.split("USER:")[1].strip()}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            action_data = json.loads(json_match.group())
            
            # Validate action data
            if not self._validate_action(action_data):
                raise ValueError("Invalid action data")
            
            return action_data
            
        except Exception as e:
            logger.error(f"Action generation failed: {e}")
            return None
    
    def _validate_action(self, action_data: Dict[str, Any]) -> bool:
        """Validate action data"""
        required_fields = ['file_path', 'change_type', 'rationale', 'estimated_risk']
        
        for field in required_fields:
            if field not in action_data:
                return False
        
        # Validate change_type
        if action_data['change_type'] not in ['add', 'modify', 'delete']:
            return False
        
        # Validate risk score
        risk = action_data['estimated_risk']
        if not isinstance(risk, (int, float)) or not 0.0 <= risk <= 1.0:
            return False
        
        return True

class PatchGenerator:
    """Patch generation and validation"""
    
    def __init__(self, s3_client):
        self.s3_client = s3_client
    
    def generate_patch(self, action_data: Dict[str, Any]) -> str:
        """Generate unified diff patch"""
        file_path = action_data['file_path']
        change_type = action_data['change_type']
        old_content = action_data.get('old_content', '')
        new_content = action_data.get('new_content', '')
        line_number = action_data.get('line_number', 1)
        
        # Generate patch header
        patch_lines = [
            f"--- a/{file_path}",
            f"+++ b/{file_path}",
            f"@@ -{line_number},1 +{line_number},1 @@"
        ]
        
        if change_type == 'add':
            patch_lines.append(f"+{new_content}")
        elif change_type == 'modify':
            patch_lines.append(f"-{old_content}")
            patch_lines.append(f"+{new_content}")
        elif change_type == 'delete':
            patch_lines.append(f"-{old_content}")
        
        return '\n'.join(patch_lines)
    
    def upload_patch(self, patch_content: str, proposal_id: str) -> str:
        """Upload patch to S3"""
        try:
            s3_key = f"patches/{proposal_id}.patch"
            self.s3_client.put_object(
                Bucket=os.getenv('S3_BUCKET', 'repolens'),
                Key=s3_key,
                Body=patch_content,
                ContentType='text/plain'
            )
            return f"s3://{os.getenv('S3_BUCKET', 'repolens')}/{s3_key}"
            
        except Exception as e:
            logger.error(f"Failed to upload patch: {e}")
            return f"mock_s3_path/{proposal_id}.patch"
    
    def validate_patch(self, patch_content: str) -> bool:
        """Validate patch format"""
        try:
            lines = patch_content.split('\n')
            
            # Check for patch header
            if not lines[0].startswith('--- ') or not lines[1].startswith('+++ '):
                return False
            
            # Check for hunk header
            if not lines[2].startswith('@@ '):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Patch validation failed: {e}")
            return False

class ActionService:
    """High-level action service"""
    
    def __init__(self, openai_api_key: str, neo4j_service, s3_client):
        self.generator = ActionGenerator(openai_api_key)
        self.patch_generator = PatchGenerator(s3_client)
        self.neo4j_service = neo4j_service
    
    def create_proposal(self, requirement: str, code_snippet: str, file_path: str, 
                       tenant_id: str, repo_id: str, proposer_id: str) -> Optional[ActionProposal]:
        """Create action proposal"""
        try:
            # Generate action
            action_data = self.generator.generate_action(requirement, code_snippet, file_path)
            if not action_data:
                return None
            
            # Generate patch
            patch_content = self.patch_generator.generate_patch(action_data)
            if not self.patch_generator.validate_patch(patch_content):
                return None
            
            # Create proposal
            proposal_id = str(uuid.uuid4())
            patch_s3_path = self.patch_generator.upload_patch(patch_content, proposal_id)
            
            proposal = ActionProposal(
                proposal_id=proposal_id,
                tenant_id=tenant_id,
                repo_id=repo_id,
                proposer_id=proposer_id,
                patch_s3_path=patch_s3_path,
                rationale=action_data['rationale'],
                tests_to_run=action_data.get('tests_to_run', []),
                estimated_risk=action_data['estimated_risk'],
                status=ProposalStatus.SUBMITTED,
                created_at=datetime.now(timezone.utc)
            )
            
            # Store in Neo4j
            self._store_proposal(proposal)
            
            return proposal
            
        except Exception as e:
            logger.error(f"Failed to create proposal: {e}")
            return None
    
    def approve_proposal(self, proposal_id: str, approver_id: str, note: str = None) -> bool:
        """Approve action proposal"""
        try:
            cypher = """
            MATCH (p:ActionProposal {proposal_id: $proposal_id})
            SET p.status = 'approved',
                p.approved_by = $approver_id,
                p.approved_at = datetime(),
                p.approval_note = $note
            RETURN p
            """
            
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, {
                    'proposal_id': proposal_id,
                    'approver_id': approver_id,
                    'note': note
                })
                
                return result.single() is not None
                
        except Exception as e:
            logger.error(f"Failed to approve proposal: {e}")
            return False
    
    def reject_proposal(self, proposal_id: str, approver_id: str, note: str = None) -> bool:
        """Reject action proposal"""
        try:
            cypher = """
            MATCH (p:ActionProposal {proposal_id: $proposal_id})
            SET p.status = 'rejected',
                p.rejected_by = $approver_id,
                p.rejected_at = datetime(),
                p.rejection_note = $note
            RETURN p
            """
            
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, {
                    'proposal_id': proposal_id,
                    'approver_id': approver_id,
                    'note': note
                })
                
                return result.single() is not None
                
        except Exception as e:
            logger.error(f"Failed to reject proposal: {e}")
            return False
    
    def get_proposal(self, proposal_id: str, tenant_id: str) -> Optional[ActionProposal]:
        """Get proposal by ID"""
        try:
            cypher = """
            MATCH (p:ActionProposal {proposal_id: $proposal_id, tenant_id: $tenant_id})
            RETURN p.proposal_id as proposal_id,
                   p.tenant_id as tenant_id,
                   p.repo_id as repo_id,
                   p.proposer_id as proposer_id,
                   p.patch_s3_path as patch_s3_path,
                   p.rationale as rationale,
                   p.tests_to_run as tests_to_run,
                   p.estimated_risk as estimated_risk,
                   p.status as status,
                   p.created_at as created_at,
                   p.approved_by as approved_by,
                   p.approved_at as approved_at
            """
            
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, {
                    'proposal_id': proposal_id,
                    'tenant_id': tenant_id
                })
                
                record = result.single()
                if record:
                    return ActionProposal(
                        proposal_id=record['proposal_id'],
                        tenant_id=record['tenant_id'],
                        repo_id=record['repo_id'],
                        proposer_id=record['proposer_id'],
                        patch_s3_path=record['patch_s3_path'],
                        rationale=record['rationale'],
                        tests_to_run=record['tests_to_run'],
                        estimated_risk=record['estimated_risk'],
                        status=ProposalStatus(record['status']),
                        created_at=record['created_at'],
                        approved_by=record['approved_by'],
                        approved_at=record['approved_at']
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get proposal: {e}")
            return None
    
    def list_proposals(self, tenant_id: str, repo_id: str = None, status: str = None) -> List[ActionProposal]:
        """List proposals with filters"""
        try:
            cypher = """
            MATCH (p:ActionProposal {tenant_id: $tenant_id})
            WHERE ($repo_id IS NULL OR p.repo_id = $repo_id)
            AND ($status IS NULL OR p.status = $status)
            RETURN p.proposal_id as proposal_id,
                   p.tenant_id as tenant_id,
                   p.repo_id as repo_id,
                   p.proposer_id as proposer_id,
                   p.patch_s3_path as patch_s3_path,
                   p.rationale as rationale,
                   p.tests_to_run as tests_to_run,
                   p.estimated_risk as estimated_risk,
                   p.status as status,
                   p.created_at as created_at,
                   p.approved_by as approved_by,
                   p.approved_at as approved_at
            ORDER BY p.created_at DESC
            """
            
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, {
                    'tenant_id': tenant_id,
                    'repo_id': repo_id,
                    'status': status
                })
                
                proposals = []
                for record in result:
                    proposal = ActionProposal(
                        proposal_id=record['proposal_id'],
                        tenant_id=record['tenant_id'],
                        repo_id=record['repo_id'],
                        proposer_id=record['proposer_id'],
                        patch_s3_path=record['patch_s3_path'],
                        rationale=record['rationale'],
                        tests_to_run=record['tests_to_run'],
                        estimated_risk=record['estimated_risk'],
                        status=ProposalStatus(record['status']),
                        created_at=record['created_at'],
                        approved_by=record['approved_by'],
                        approved_at=record['approved_at']
                    )
                    proposals.append(proposal)
                
                return proposals
                
        except Exception as e:
            logger.error(f"Failed to list proposals: {e}")
            return []
    
    def _store_proposal(self, proposal: ActionProposal):
        """Store proposal in Neo4j"""
        cypher = """
        CREATE (p:ActionProposal {
            proposal_id: $proposal_id,
            tenant_id: $tenant_id,
            repo_id: $repo_id,
            proposer_id: $proposer_id,
            patch_s3_path: $patch_s3_path,
            rationale: $rationale,
            tests_to_run: $tests_to_run,
            estimated_risk: $estimated_risk,
            status: $status,
            created_at: datetime()
        })
        
        MERGE (r:Repo {tenant_id: $tenant_id, repo_id: $repo_id})
        MERGE (r)-[:HAS_PROPOSAL]->(p)
        """
        
        try:
            with self.neo4j_service.driver.session() as session:
                session.run(cypher, {
                    'proposal_id': proposal.proposal_id,
                    'tenant_id': proposal.tenant_id,
                    'repo_id': proposal.repo_id,
                    'proposer_id': proposal.proposer_id,
                    'patch_s3_path': proposal.patch_s3_path,
                    'rationale': proposal.rationale,
                    'tests_to_run': proposal.tests_to_run,
                    'estimated_risk': proposal.estimated_risk,
                    'status': proposal.status.value,
                    'created_at': proposal.created_at
                })
                
        except Exception as e:
            logger.error(f"Failed to store proposal: {e}")

if __name__ == "__main__":
    # Test action service
    from neo4j import GraphDatabase
    import boto3
    
    neo4j_service = Neo4jService(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    s3_client = boto3.client('s3')
    
    action_service = ActionService(
        openai_api_key=os.getenv("OPENAI_API_KEY", "test-key"),
        neo4j_service=neo4j_service,
        s3_client=s3_client
    )
    
    # Test proposal creation
    proposal = action_service.create_proposal(
        requirement="Add input validation to the function",
        code_snippet="def process_data(data):\n    return data.upper()",
        file_path="src/utils.py",
        tenant_id="tenant_123",
        repo_id="repo_123",
        proposer_id="user_123"
    )
    
    if proposal:
        print(f"Created proposal: {proposal.proposal_id}")
        print(f"Rationale: {proposal.rationale}")
        print(f"Risk: {proposal.estimated_risk}")
    
    neo4j_service.close()
