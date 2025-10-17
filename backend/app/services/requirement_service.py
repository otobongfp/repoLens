# RepoLens Requirement Service
# LLM-based requirement extraction and matching with exact prompts

import os
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import uuid
from dataclasses import dataclass
import re

try:
    import openai
except ImportError:
    raise ImportError("openai not installed. Run: pip install openai")

logger = logging.getLogger(__name__)


@dataclass
class ExtractedRequirement:
    """Extracted requirement with metadata"""

    req_id: str
    title: str
    text: str
    acceptance_criteria: List[str]
    priority: str
    source: str
    confidence: float
    extraction_provenance: Dict[str, Any]


@dataclass
class RequirementMatch:
    """Requirement to code match"""

    function_id: str
    confidence: float
    evidence_snippet_s3: str
    match_method: str
    path: str
    signature: str
    call_graph_context: List[str]


@dataclass
class VerificationRecord:
    """Human verification record"""

    verification_id: str
    req_id: str
    function_id: str
    user_id: str
    verdict: str
    note: Optional[str]
    created_at: datetime


class RequirementExtractor:
    """LLM-based requirement extraction using exact prompts from directive"""

    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model

        # Exact prompt from directive
        self.extraction_prompt = """
SYSTEM: You are a strict JSON extractor. Convert the following DOCUMENT into a JSON array of Requirements. Do not add, remove, or invent requirements. If the document contains multiple requirements, split them. If a requirement is ambiguous, include "confidence": 0.5 and "notes" describing ambiguity. Output must be ONLY valid JSON.

USER: <<DOCUMENT_TEXT>>

REQUIREMENT JSON FORMAT:
[
  {
    "id": "<generated but deterministic id: SHA256(tenant_id + repo_id + first 64 chars of text)>",
    "title": "<short title, 6 words max>",
    "text": "<full requirement text>",
    "acceptance_criteria": ["..."], 
    "priority": "P1|P2|P3|unknown",
    "source": "<source identifier e.g., filename or URL>",
    "confidence": 0.0-1.0
  }
]
"""

    def extract_requirements(
        self, document_text: str, tenant_id: str, repo_id: str, source: str
    ) -> List[ExtractedRequirement]:
        """Extract requirements from document using exact prompt"""
        try:
            # Replace placeholder in prompt
            prompt = self.extraction_prompt.replace("<<DOCUMENT_TEXT>>", document_text)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt.split("USER:")[0].strip()},
                    {"role": "user", "content": prompt.split("USER:")[1].strip()},
                ],
                max_tokens=4000,
                temperature=0.1,
            )

            response_text = response.choices[0].message.content.strip()

            # Extract JSON from response
            json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON array found in response")

            requirements_data = json.loads(json_match.group())

            # Convert to ExtractedRequirement objects
            requirements = []
            for req_data in requirements_data:
                # Generate deterministic ID if not provided
                if "id" not in req_data:
                    req_data["id"] = self._generate_requirement_id(
                        tenant_id, repo_id, req_data["text"]
                    )

                requirement = ExtractedRequirement(
                    req_id=req_data["id"],
                    title=req_data.get("title", "Untitled Requirement"),
                    text=req_data["text"],
                    acceptance_criteria=req_data.get("acceptance_criteria", []),
                    priority=req_data.get("priority", "unknown"),
                    source=source,
                    confidence=req_data.get("confidence", 0.8),
                    extraction_provenance={
                        "model": self.model,
                        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "token_usage": response.usage.dict() if response.usage else {},
                        "extraction_method": "structured_extraction",
                    },
                )
                requirements.append(requirement)

            logger.info(f"Extracted {len(requirements)} requirements from {source}")
            return requirements

        except Exception as e:
            logger.error(f"Requirement extraction failed: {e}")
            return []

    def _generate_requirement_id(self, tenant_id: str, repo_id: str, text: str) -> str:
        """Generate deterministic requirement ID"""
        content = f"{tenant_id}:{repo_id}:{text[:64]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class RequirementMatcher:
    """Requirement to code matching with vector search and re-ranking"""

    def __init__(self, vector_service, neo4j_service):
        self.vector_service = vector_service
        self.neo4j_service = neo4j_service

        # Exact reranker prompt from directive
        self.reranker_prompt = """
SYSTEM: You are a deterministic re-ranker. Given 1 requirement and a list of candidate code snippets with metadata, output a JSON ranked array with fields {candidate_id, score (0-1), reason}. Do not hallucinate. Use only the provided snippets and metadata to form reasons.

USER:
Requirement: <<TEXT>>

Candidates:
[
  { "candidate_id": "...", "path": "...", "signature": "...", "summary_det": "...", "snippet": "..." },
  ...
]
"""

    def match_requirement_to_code(
        self, requirement: ExtractedRequirement, tenant_id: str, top_k: int = 10
    ) -> List[RequirementMatch]:
        """Match requirement to code using vector search and re-ranking"""
        try:
            # Step 1: Vector search for top-K candidates
            vector_candidates = self.vector_service.search_similar_functions(
                requirement.text, tenant_id, top_k=200
            )

            if not vector_candidates:
                return []

            # Step 2: Re-rank using structural features
            reranked_candidates = self._rerank_candidates(
                requirement, vector_candidates
            )

            # Step 3: Create RequirementMatch objects
            matches = []
            for candidate in reranked_candidates[:top_k]:
                match = RequirementMatch(
                    function_id=candidate["function_id"],
                    confidence=candidate["final_score"],
                    evidence_snippet_s3=candidate.get("snippet_s3_path", ""),
                    match_method="hybrid_vector_similarity",
                    path=candidate["path"],
                    signature=candidate["signature"],
                    call_graph_context=candidate.get("call_graph_context", []),
                )
                matches.append(match)

            return matches

        except Exception as e:
            logger.error(f"Requirement matching failed: {e}")
            return []

    def _rerank_candidates(
        self, requirement: ExtractedRequirement, candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Re-rank candidates using structural features"""
        reranked = []

        for candidate in candidates:
            # Calculate composite confidence score
            vector_similarity = candidate.get("similarity_score", 0.0)

            # Structural features
            same_repo_bonus = 0.10 if candidate.get("same_repo", False) else 0.0
            filename_overlap = self._calculate_filename_overlap(
                requirement.text, candidate["path"]
            )
            call_graph_closeness = self._calculate_call_graph_closeness(
                candidate["function_id"]
            )
            test_coverage_bonus = 0.20 if candidate.get("has_tests", False) else 0.0

            # Composite score
            final_score = (
                vector_similarity * 0.50
                + same_repo_bonus
                + filename_overlap * 0.08
                + call_graph_closeness * 0.12
                + test_coverage_bonus
            )

            # Normalize to [0, 1]
            final_score = max(0.0, min(1.0, final_score))

            candidate["final_score"] = final_score
            candidate["match_method"] = (
                "low_confidence" if final_score < 0.5 else "high_confidence"
            )
            candidate["requires_verification"] = final_score < 0.7

            reranked.append(candidate)

        # Sort by final score
        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        return reranked

    def _calculate_filename_overlap(
        self, requirement_text: str, file_path: str
    ) -> float:
        """Calculate filename token overlap with requirement"""
        req_tokens = set(requirement_text.lower().split())
        file_tokens = set(file_path.lower().split("/"))

        if not req_tokens or not file_tokens:
            return 0.0

        overlap = len(req_tokens.intersection(file_tokens))
        return overlap / len(req_tokens.union(file_tokens))

    def _calculate_call_graph_closeness(self, function_id: str) -> float:
        """Calculate call graph closeness score"""
        # TODO: Implement call graph analysis
        return 0.0


class RequirementVerifier:
    """Human verification workflow for requirement matches"""

    def __init__(self, neo4j_service):
        self.neo4j_service = neo4j_service

    def create_verification_task(
        self, req_id: str, function_id: str, tenant_id: str
    ) -> str:
        """Create verification task for human review"""
        verification_id = str(uuid.uuid4())

        verification = VerificationRecord(
            verification_id=verification_id,
            req_id=req_id,
            function_id=function_id,
            user_id="",  # Will be set when user verifies
            verdict="pending",
            note=None,
            created_at=datetime.now(timezone.utc),
        )

        # Store in Neo4j
        cypher = """
        MATCH (req:Requirement {req_id: $req_id, tenant_id: $tenant_id})
        MATCH (func:Function {function_id: $function_id, tenant_id: $tenant_id})
        CREATE (v:Verification {
            verification_id: $verification_id,
            req_id: $req_id,
            function_id: $function_id,
            verdict: 'pending',
            created_at: datetime()
        })
        CREATE (v)-[:VERIFIES]->(req)
        CREATE (v)-[:REFERENCES]->(func)
        """

        try:
            with self.neo4j_service.driver.session() as session:
                session.run(
                    cypher,
                    {
                        "verification_id": verification_id,
                        "req_id": req_id,
                        "function_id": function_id,
                        "tenant_id": tenant_id,
                    },
                )

            return verification_id

        except Exception as e:
            logger.error(f"Failed to create verification task: {e}")
            return ""

    def submit_verification(
        self, verification_id: str, user_id: str, verdict: str, note: str = None
    ) -> bool:
        """Submit human verification"""
        cypher = """
        MATCH (v:Verification {verification_id: $verification_id})
        SET v.user_id = $user_id,
            v.verdict = $verdict,
            v.note = $note,
            v.verified_at = datetime()
        
        // Update IMPLEMENTED_BY edge confidence
        MATCH (req:Requirement)-[e:IMPLEMENTED_BY]->(func:Function)
        WHERE req.req_id = v.req_id AND func.function_id = v.function_id
        SET e.verified_by = $user_id,
            e.verified_at = datetime(),
            e.confidence = CASE 
                WHEN $verdict = 'accepted' THEN min(1.0, e.confidence + 0.1)
                WHEN $verdict = 'rejected' THEN max(0.0, e.confidence - 0.2)
                ELSE e.confidence
            END
        """

        try:
            with self.neo4j_service.driver.session() as session:
                session.run(
                    cypher,
                    {
                        "verification_id": verification_id,
                        "user_id": user_id,
                        "verdict": verdict,
                        "note": note,
                    },
                )

            return True

        except Exception as e:
            logger.error(f"Failed to submit verification: {e}")
            return False

    def get_verification_context(self, verification_id: str) -> Dict[str, Any]:
        """Get verification context for human review"""
        cypher = """
        MATCH (v:Verification {verification_id: $verification_id})
        MATCH (req:Requirement {req_id: v.req_id})
        MATCH (func:Function {function_id: v.function_id})
        MATCH (file:File)-[:CONTAINS]->(func)
        
        OPTIONAL MATCH (func)-[:CALLS]->(called:Function)
        OPTIONAL MATCH (caller:Function)-[:CALLS]->(func)
        
        RETURN req.text as requirement_text,
               req.acceptance_criteria as acceptance_criteria,
               func.name as function_name,
               func.signature as function_signature,
               func.snippet_s3_path as snippet_s3_path,
               file.path as file_path,
               collect(DISTINCT called.name) as called_functions,
               collect(DISTINCT caller.name) as caller_functions
        """

        try:
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, verification_id=verification_id)
                record = result.single()

                if record:
                    return {
                        "requirement_text": record["requirement_text"],
                        "acceptance_criteria": record["acceptance_criteria"],
                        "function_name": record["function_name"],
                        "function_signature": record["function_signature"],
                        "snippet_s3_path": record["snippet_s3_path"],
                        "file_path": record["file_path"],
                        "called_functions": record["called_functions"],
                        "caller_functions": record["caller_functions"],
                    }
                else:
                    return {}

        except Exception as e:
            logger.error(f"Failed to get verification context: {e}")
            return {}


class RequirementService:
    """High-level requirement service orchestrating extraction, matching, and verification"""

    def __init__(self, openai_api_key: str, vector_service, neo4j_service):
        self.extractor = RequirementExtractor(openai_api_key)
        self.matcher = RequirementMatcher(vector_service, neo4j_service)
        self.verifier = RequirementVerifier(neo4j_service)
        self.neo4j_service = neo4j_service

    def process_requirement_document(
        self, document_text: str, tenant_id: str, repo_id: str, source: str
    ) -> Dict[str, Any]:
        """Process requirement document end-to-end"""
        # Step 1: Extract requirements
        requirements = self.extractor.extract_requirements(
            document_text, tenant_id, repo_id, source
        )

        # Step 2: Store requirements in Neo4j
        for req in requirements:
            self._store_requirement(req, tenant_id)

        # Step 3: Match requirements to code
        all_matches = []
        for req in requirements:
            matches = self.matcher.match_requirement_to_code(req, tenant_id)
            all_matches.extend(matches)

            # Create IMPLEMENTED_BY edges
            for match in matches:
                self.neo4j_service.create_implemented_by_edge(
                    req.req_id,
                    match.function_id,
                    tenant_id,
                    match.confidence,
                    match.evidence_snippet_s3,
                    match.match_method,
                )

        return {
            "requirements_extracted": len(requirements),
            "matches_found": len(all_matches),
            "high_confidence_matches": len(
                [m for m in all_matches if m.confidence >= 0.7]
            ),
            "verification_tasks_created": len(
                [m for m in all_matches if m.confidence < 0.7]
            ),
        }

    def _store_requirement(self, requirement: ExtractedRequirement, tenant_id: str):
        """Store requirement in Neo4j"""
        cypher = """
        MERGE (req:Requirement {tenant_id: $tenant_id, req_id: $req_id})
        SET req.title = $title,
            req.text = $text,
            req.acceptance_criteria = $acceptance_criteria,
            req.priority = $priority,
            req.source = $source,
            req.confidence = $confidence,
            req.extraction_provenance = $extraction_provenance,
            req.created_at = datetime()
        """

        try:
            with self.neo4j_service.driver.session() as session:
                session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "req_id": requirement.req_id,
                        "title": requirement.title,
                        "text": requirement.text,
                        "acceptance_criteria": requirement.acceptance_criteria,
                        "priority": requirement.priority,
                        "source": requirement.source,
                        "confidence": requirement.confidence,
                        "extraction_provenance": requirement.extraction_provenance,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store requirement: {e}")

    def get_requirement_matches(
        self, req_id: str, tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Get all matches for a requirement"""
        cypher = """
        MATCH (req:Requirement {req_id: $req_id, tenant_id: $tenant_id})
        MATCH (req)-[e:IMPLEMENTED_BY]->(func:Function)
        MATCH (file:File)-[:CONTAINS]->(func)
        
        RETURN func.function_id as function_id,
               func.name as function_name,
               func.signature as signature,
               file.path as file_path,
               e.confidence as confidence,
               e.match_method as match_method,
               e.evidence_snippet_s3 as evidence_s3,
               e.verified_by as verified_by
        ORDER BY e.confidence DESC
        """

        try:
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, req_id=req_id, tenant_id=tenant_id)
                return [dict(record) for record in result]

        except Exception as e:
            logger.error(f"Failed to get requirement matches: {e}")
            return []


if __name__ == "__main__":
    # Test requirement extraction
    extractor = RequirementExtractor(
        openai_api_key=os.getenv("OPENAI_API_KEY", "test-key"), model="gpt-4"
    )

    sample_document = """
    The system shall provide user authentication functionality.
    Users must be able to log in with username and password.
    The system shall validate credentials against the database.
    Failed login attempts shall be logged for security monitoring.
    """

    requirements = extractor.extract_requirements(
        sample_document, "tenant_123", "repo_123", "requirements.md"
    )

    print(f"Extracted {len(requirements)} requirements:")
    for req in requirements:
        print(f"  - {req.title}: {req.text[:50]}...")
        print(f"    Confidence: {req.confidence}")
        print(f"    Priority: {req.priority}")
