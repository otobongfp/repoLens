# RepoLens Audit Logging Service
# Comprehensive audit trail for compliance and security

import os
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    # Repository actions
    REPO_ANALYZE = "repo_analyze"
    REPO_DELETE = "repo_delete"
    REPO_INDEX = "repo_index"

    # Requirement actions
    REQUIREMENT_EXTRACT = "requirement_extract"
    REQUIREMENT_MATCH = "requirement_match"
    REQUIREMENT_VERIFY = "requirement_verify"

    # Action proposal actions
    PROPOSAL_CREATE = "proposal_create"
    PROPOSAL_APPROVE = "proposal_approve"
    PROPOSAL_REJECT = "proposal_reject"

    # Security actions
    SECURITY_SCAN = "security_scan"
    CVE_SCAN = "cve_scan"
    SAST_SCAN = "sast_scan"

    # Admin actions
    TENANT_CREATE = "tenant_create"
    TENANT_UPDATE = "tenant_update"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"

    # System actions
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_ERROR = "system_error"


@dataclass
class AuditEvent:
    """Audit event representation"""

    event_id: str
    actor_id: str  # user_id or agent_id
    action: AuditAction
    target_ids: Dict[str, str]  # e.g., {"repo_id": "xyz", "function_id": "abc"}
    details: Dict[str, Any]
    timestamp: datetime
    tenant_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None


class AuditLogger:
    """Audit logging service"""

    def __init__(self, neo4j_service):
        self.neo4j_service = neo4j_service
        self._create_audit_schema()

    def _create_audit_schema(self):
        """Create audit schema in Neo4j"""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS audit_event_unique FOR (a:AuditEvent) REQUIRE a.event_id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS audit_event_actor FOR (a:AuditEvent) ON (a.actor_id)",
            "CREATE INDEX IF NOT EXISTS audit_event_action FOR (a:AuditEvent) ON (a.action)",
            "CREATE INDEX IF NOT EXISTS audit_event_tenant FOR (a:AuditEvent) ON (a.tenant_id)",
            "CREATE INDEX IF NOT EXISTS audit_event_timestamp FOR (a:AuditEvent) ON (a.timestamp)",
        ]

        try:
            with self.neo4j_service.driver.session() as session:
                for constraint in constraints:
                    session.run(constraint)
            logger.info("Created audit schema")

        except Exception as e:
            logger.error(f"Failed to create audit schema: {e}")

    def log_event(self, event: AuditEvent) -> bool:
        """Log audit event"""
        try:
            cypher = """
            CREATE (a:AuditEvent {
                event_id: $event_id,
                actor_id: $actor_id,
                action: $action,
                target_ids: $target_ids,
                details: $details,
                timestamp: datetime($timestamp),
                tenant_id: $tenant_id,
                ip_address: $ip_address,
                user_agent: $user_agent,
                session_id: $session_id
            })
            """

            with self.neo4j_service.driver.session() as session:
                session.run(
                    cypher,
                    {
                        "event_id": event.event_id,
                        "actor_id": event.actor_id,
                        "action": event.action.value,
                        "target_ids": event.target_ids,
                        "details": event.details,
                        "timestamp": event.timestamp.isoformat(),
                        "tenant_id": event.tenant_id,
                        "ip_address": event.ip_address,
                        "user_agent": event.user_agent,
                        "session_id": event.session_id,
                    },
                )

            logger.info(f"Logged audit event: {event.action.value} by {event.actor_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return False

    def log_repository_analysis(
        self, tenant_id: str, repo_id: str, actor_id: str, details: Dict[str, Any]
    ) -> bool:
        """Log repository analysis event"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            actor_id=actor_id,
            action=AuditAction.REPO_ANALYZE,
            target_ids={"repo_id": repo_id},
            details=details,
            timestamp=datetime.now(timezone.utc),
            tenant_id=tenant_id,
        )
        return self.log_event(event)

    def log_requirement_extraction(
        self, tenant_id: str, req_id: str, actor_id: str, details: Dict[str, Any]
    ) -> bool:
        """Log requirement extraction event"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            actor_id=actor_id,
            action=AuditAction.REQUIREMENT_EXTRACT,
            target_ids={"req_id": req_id},
            details=details,
            timestamp=datetime.now(timezone.utc),
            tenant_id=tenant_id,
        )
        return self.log_event(event)

    def log_requirement_verification(
        self,
        tenant_id: str,
        req_id: str,
        function_id: str,
        actor_id: str,
        verdict: str,
        details: Dict[str, Any],
    ) -> bool:
        """Log requirement verification event"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            actor_id=actor_id,
            action=AuditAction.REQUIREMENT_VERIFY,
            target_ids={"req_id": req_id, "function_id": function_id},
            details={**details, "verdict": verdict},
            timestamp=datetime.now(timezone.utc),
            tenant_id=tenant_id,
        )
        return self.log_event(event)

    def log_proposal_approval(
        self,
        tenant_id: str,
        proposal_id: str,
        actor_id: str,
        verdict: str,
        details: Dict[str, Any],
    ) -> bool:
        """Log proposal approval event"""
        action = (
            AuditAction.PROPOSAL_APPROVE
            if verdict == "approved"
            else AuditAction.PROPOSAL_REJECT
        )

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            actor_id=actor_id,
            action=action,
            target_ids={"proposal_id": proposal_id},
            details={**details, "verdict": verdict},
            timestamp=datetime.now(timezone.utc),
            tenant_id=tenant_id,
        )
        return self.log_event(event)

    def log_security_scan(
        self,
        tenant_id: str,
        repo_id: str,
        actor_id: str,
        scan_type: str,
        details: Dict[str, Any],
    ) -> bool:
        """Log security scan event"""
        action = AuditAction.CVE_SCAN if scan_type == "cve" else AuditAction.SAST_SCAN

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            actor_id=actor_id,
            action=action,
            target_ids={"repo_id": repo_id},
            details={**details, "scan_type": scan_type},
            timestamp=datetime.now(timezone.utc),
            tenant_id=tenant_id,
        )
        return self.log_event(event)

    def log_user_action(
        self,
        tenant_id: str,
        user_id: str,
        action: AuditAction,
        target_ids: Dict[str, str],
        details: Dict[str, Any],
        ip_address: str = None,
        user_agent: str = None,
        session_id: str = None,
    ) -> bool:
        """Log user action event"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            actor_id=user_id,
            action=action,
            target_ids=target_ids,
            details=details,
            timestamp=datetime.now(timezone.utc),
            tenant_id=tenant_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
        )
        return self.log_event(event)

    def log_system_event(self, action: AuditAction, details: Dict[str, Any]) -> bool:
        """Log system event"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            actor_id="system",
            action=action,
            target_ids={},
            details=details,
            timestamp=datetime.now(timezone.utc),
            tenant_id="system",
        )
        return self.log_event(event)

    def get_audit_trail(
        self,
        tenant_id: str,
        start_date: datetime = None,
        end_date: datetime = None,
        action: AuditAction = None,
        actor_id: str = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Get audit trail with filters"""
        try:
            cypher = """
            MATCH (a:AuditEvent {tenant_id: $tenant_id})
            WHERE ($start_date IS NULL OR a.timestamp >= datetime($start_date))
            AND ($end_date IS NULL OR a.timestamp <= datetime($end_date))
            AND ($action IS NULL OR a.action = $action)
            AND ($actor_id IS NULL OR a.actor_id = $actor_id)
            RETURN a.event_id as event_id,
                   a.actor_id as actor_id,
                   a.action as action,
                   a.target_ids as target_ids,
                   a.details as details,
                   a.timestamp as timestamp,
                   a.tenant_id as tenant_id,
                   a.ip_address as ip_address,
                   a.user_agent as user_agent,
                   a.session_id as session_id
            ORDER BY a.timestamp DESC
            LIMIT $limit
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                        "action": action.value if action else None,
                        "actor_id": actor_id,
                        "limit": limit,
                    },
                )

                events = []
                for record in result:
                    event = AuditEvent(
                        event_id=record["event_id"],
                        actor_id=record["actor_id"],
                        action=AuditAction(record["action"]),
                        target_ids=record["target_ids"],
                        details=record["details"],
                        timestamp=record["timestamp"],
                        tenant_id=record["tenant_id"],
                        ip_address=record["ip_address"],
                        user_agent=record["user_agent"],
                        session_id=record["session_id"],
                    )
                    events.append(event)

                return events

        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            return []

    def get_audit_summary(
        self, tenant_id: str, start_date: datetime = None, end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get audit summary statistics"""
        try:
            cypher = """
            MATCH (a:AuditEvent {tenant_id: $tenant_id})
            WHERE ($start_date IS NULL OR a.timestamp >= datetime($start_date))
            AND ($end_date IS NULL OR a.timestamp <= datetime($end_date))
            RETURN count(a) as total_events,
                   count(DISTINCT a.actor_id) as unique_actors,
                   count(DISTINCT a.action) as unique_actions,
                   collect(DISTINCT a.action) as actions
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                    },
                )

                record = result.single()
                if record:
                    return {
                        "total_events": record["total_events"],
                        "unique_actors": record["unique_actors"],
                        "unique_actions": record["unique_actions"],
                        "actions": record["actions"],
                    }

                return {
                    "total_events": 0,
                    "unique_actors": 0,
                    "unique_actions": 0,
                    "actions": [],
                }

        except Exception as e:
            logger.error(f"Failed to get audit summary: {e}")
            return {
                "total_events": 0,
                "unique_actors": 0,
                "unique_actions": 0,
                "actions": [],
            }

    def export_audit_log(
        self,
        tenant_id: str,
        start_date: datetime = None,
        end_date: datetime = None,
        format: str = "json",
    ) -> str:
        """Export audit log in specified format"""
        try:
            events = self.get_audit_trail(tenant_id, start_date, end_date, limit=10000)

            if format == "json":
                return json.dumps(
                    [
                        {
                            "event_id": event.event_id,
                            "actor_id": event.actor_id,
                            "action": event.action.value,
                            "target_ids": event.target_ids,
                            "details": event.details,
                            "timestamp": event.timestamp.isoformat(),
                            "tenant_id": event.tenant_id,
                            "ip_address": event.ip_address,
                            "user_agent": event.user_agent,
                            "session_id": event.session_id,
                        }
                        for event in events
                    ],
                    indent=2,
                )

            elif format == "csv":
                import csv
                import io

                output = io.StringIO()
                writer = csv.writer(output)

                # Write header
                writer.writerow(
                    [
                        "event_id",
                        "actor_id",
                        "action",
                        "target_ids",
                        "details",
                        "timestamp",
                        "tenant_id",
                        "ip_address",
                        "user_agent",
                        "session_id",
                    ]
                )

                # Write data
                for event in events:
                    writer.writerow(
                        [
                            event.event_id,
                            event.actor_id,
                            event.action.value,
                            json.dumps(event.target_ids),
                            json.dumps(event.details),
                            event.timestamp.isoformat(),
                            event.tenant_id,
                            event.ip_address,
                            event.user_agent,
                            event.session_id,
                        ]
                    )

                return output.getvalue()

            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Failed to export audit log: {e}")
            return ""


class AuditService:
    """High-level audit service"""

    def __init__(self, neo4j_service):
        self.logger = AuditLogger(neo4j_service)
        self.neo4j_service = neo4j_service

    def log_repository_operation(
        self,
        tenant_id: str,
        repo_id: str,
        actor_id: str,
        operation: str,
        details: Dict[str, Any],
    ) -> bool:
        """Log repository operation"""
        if operation == "analyze":
            return self.logger.log_repository_analysis(
                tenant_id, repo_id, actor_id, details
            )
        elif operation == "delete":
            return self.logger.log_user_action(
                tenant_id,
                actor_id,
                AuditAction.REPO_DELETE,
                {"repo_id": repo_id},
                details,
            )
        else:
            return False

    def log_requirement_operation(
        self,
        tenant_id: str,
        req_id: str,
        actor_id: str,
        operation: str,
        details: Dict[str, Any],
    ) -> bool:
        """Log requirement operation"""
        if operation == "extract":
            return self.logger.log_requirement_extraction(
                tenant_id, req_id, actor_id, details
            )
        elif operation == "verify":
            function_id = details.get("function_id", "")
            verdict = details.get("verdict", "unknown")
            return self.logger.log_requirement_verification(
                tenant_id, req_id, function_id, actor_id, verdict, details
            )
        else:
            return False

    def log_proposal_operation(
        self,
        tenant_id: str,
        proposal_id: str,
        actor_id: str,
        operation: str,
        details: Dict[str, Any],
    ) -> bool:
        """Log proposal operation"""
        if operation == "create":
            return self.logger.log_user_action(
                tenant_id,
                actor_id,
                AuditAction.PROPOSAL_CREATE,
                {"proposal_id": proposal_id},
                details,
            )
        elif operation in ["approve", "reject"]:
            return self.logger.log_proposal_approval(
                tenant_id, proposal_id, actor_id, operation, details
            )
        else:
            return False

    def log_security_operation(
        self,
        tenant_id: str,
        repo_id: str,
        actor_id: str,
        scan_type: str,
        details: Dict[str, Any],
    ) -> bool:
        """Log security operation"""
        return self.logger.log_security_scan(
            tenant_id, repo_id, actor_id, scan_type, details
        )

    def get_compliance_report(
        self, tenant_id: str, start_date: datetime = None, end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get compliance report"""
        summary = self.logger.get_audit_summary(tenant_id, start_date, end_date)
        events = self.logger.get_audit_trail(
            tenant_id, start_date, end_date, limit=1000
        )

        # Analyze events for compliance
        compliance_metrics = {
            "total_events": summary["total_events"],
            "unique_users": summary["unique_actors"],
            "data_access_events": len([e for e in events if "repo_id" in e.target_ids]),
            "security_events": len(
                [
                    e
                    for e in events
                    if e.action in [AuditAction.CVE_SCAN, AuditAction.SAST_SCAN]
                ]
            ),
            "approval_events": len(
                [
                    e
                    for e in events
                    if e.action
                    in [AuditAction.PROPOSAL_APPROVE, AuditAction.PROPOSAL_REJECT]
                ]
            ),
            "verification_events": len(
                [e for e in events if e.action == AuditAction.REQUIREMENT_VERIFY]
            ),
        }

        return {
            "summary": summary,
            "compliance_metrics": compliance_metrics,
            "export_available": True,
        }


if __name__ == "__main__":
    # Test audit service
    from neo4j import GraphDatabase

    neo4j_service = Neo4jService(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password"),
    )

    audit_service = AuditService(neo4j_service)

    # Test audit logging
    success = audit_service.log_repository_operation(
        tenant_id="tenant_123",
        repo_id="repo_123",
        actor_id="user_123",
        operation="analyze",
        details={"files_processed": 150, "functions_found": 300},
    )

    print(f"Audit logging success: {success}")

    # Test compliance report
    report = audit_service.get_compliance_report("tenant_123")
    print(f"Compliance report: {report}")

    neo4j_service.close()
