# RepoLens Neo4j Service
# Production-grade graph database operations with bulk-upsert capabilities

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import uuid
from dataclasses import dataclass, asdict
import json

try:
    from neo4j import GraphDatabase, Driver, Session
except ImportError:
    raise ImportError("neo4j driver not installed. Run: pip install neo4j")

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Graph node representation"""

    node_id: str
    labels: List[str]
    properties: Dict[str, Any]
    tenant_id: str


@dataclass
class GraphEdge:
    """Graph edge representation"""

    from_node: str
    to_node: str
    relationship_type: str
    properties: Dict[str, Any]
    tenant_id: str


@dataclass
class BulkOperation:
    """Bulk operation result"""

    operation_id: str
    nodes_created: int
    nodes_updated: int
    edges_created: int
    edges_updated: int
    errors: List[str]
    duration_ms: int


class Neo4jService:
    """Neo4j service with bulk operations and enterprise features"""

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Driver] = None
        self._connected = False

    def _ensure_connected(self):
        """Ensure connection to Neo4j database"""
        if not self._connected or self.driver is None:
            self._connect()
            self._create_constraints()

    def _connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_timeout=30,
            )

            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()

            self._connected = True
            logger.info(f"Connected to Neo4j at {self.uri}")

        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self._connected = False
            raise

    def _create_constraints(self):
        """Create database constraints"""
        constraints = [
            # Tenant constraints
            "CREATE CONSTRAINT IF NOT EXISTS tenant_unique FOR (t:Tenant) REQUIRE t.tenant_id IS UNIQUE",
            # Repository constraints
            "CREATE CONSTRAINT IF NOT EXISTS repo_unique FOR (r:Repo) REQUIRE (r.tenant_id, r.repo_id) IS UNIQUE",
            # File constraints
            "CREATE CONSTRAINT IF NOT EXISTS file_unique FOR (f:File) REQUIRE (f.tenant_id, f.repo_id, f.path) IS UNIQUE",
            # Function constraints
            "CREATE CONSTRAINT IF NOT EXISTS function_unique FOR (func:Function) REQUIRE (func.tenant_id, func.repo_id, func.qualified_name) IS UNIQUE",
            # Class constraints
            "CREATE CONSTRAINT IF NOT EXISTS class_unique FOR (c:Class) REQUIRE (c.tenant_id, c.repo_id, c.qualified_name) IS UNIQUE",
            # Symbol constraints
            "CREATE CONSTRAINT IF NOT EXISTS symbol_unique FOR (s:Symbol) REQUIRE (s.tenant_id, s.symbol_id) IS UNIQUE",
            # Requirement constraints
            "CREATE CONSTRAINT IF NOT EXISTS requirement_unique FOR (req:Requirement) REQUIRE (req.tenant_id, req.req_id) IS UNIQUE",
            # Action proposal constraints
            "CREATE CONSTRAINT IF NOT EXISTS proposal_unique FOR (p:ActionProposal) REQUIRE (p.tenant_id, p.proposal_id) IS UNIQUE",
            # Verification constraints
            "CREATE CONSTRAINT IF NOT EXISTS verification_unique FOR (v:Verification) REQUIRE (v.tenant_id, v.verification_id) IS UNIQUE",
            # Audit event constraints
            "CREATE CONSTRAINT IF NOT EXISTS audit_unique FOR (a:AuditEvent) REQUIRE a.event_id IS UNIQUE",
        ]

        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(
                        f"Created constraint: {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}"
                    )
                except Exception as e:
                    logger.warning(f"Constraint may already exist: {e}")

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")

    def bulk_upsert_functions(
        self, functions: List[Dict[str, Any]], tenant_id: str
    ) -> BulkOperation:
        """Bulk upsert functions using UNWIND pattern"""
        self._ensure_connected()
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()

        cypher = """
        UNWIND $functions AS fn
        MERGE (file:File {tenant_id: fn.tenant_id, repo_id: fn.repo_id, path: fn.file_path})
          ON CREATE SET file.lang = fn.language, 
                        file.file_hash = fn.file_hash, 
                        file.parse_status = 'parsed',
                        file.created_at = datetime()
          ON MATCH SET file.last_indexed_at = datetime()
        
        MERGE (func:Function {tenant_id: fn.tenant_id, repo_id: fn.repo_id, qualified_name: fn.qualified_name})
          ON CREATE SET func.name = fn.name,
                        func.signature = fn.signature,
                        func.start_line = fn.start_line,
                        func.end_line = fn.end_line,
                        func.code_hash = fn.code_hash,
                        func.snippet_s3_path = fn.snippet_s3_path,
                        func.summary_det = fn.summary_det,
                        func.complexity_score = fn.complexity_score,
                        func.created_at = datetime()
          ON MATCH SET func.last_indexed_at = datetime(),
                        func.code_hash = fn.code_hash,
                        func.snippet_s3_path = fn.snippet_s3_path
        
        MERGE (file)-[:CONTAINS]->(func)
        """

        try:
            with self.driver.session() as session:
                result = session.run(cypher, functions=functions)
                result.consume()

                duration = (datetime.now() - start_time).total_seconds() * 1000

                return BulkOperation(
                    operation_id=operation_id,
                    nodes_created=len(functions),
                    nodes_updated=0,
                    edges_created=len(functions),
                    edges_updated=0,
                    errors=[],
                    duration_ms=int(duration),
                )

        except Exception as e:
            logger.error(f"Bulk upsert functions failed: {e}")
            return BulkOperation(
                operation_id=operation_id,
                nodes_created=0,
                nodes_updated=0,
                edges_created=0,
                edges_updated=0,
                errors=[str(e)],
                duration_ms=0,
            )

    def bulk_upsert_classes(
        self, classes: List[Dict[str, Any]], tenant_id: str
    ) -> BulkOperation:
        """Bulk upsert classes"""
        self._ensure_connected()
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()

        cypher = """
        UNWIND $classes AS cls
        MERGE (file:File {tenant_id: cls.tenant_id, repo_id: cls.repo_id, path: cls.file_path})
          ON CREATE SET file.lang = cls.language,
                        file.file_hash = cls.file_hash,
                        file.parse_status = 'parsed',
                        file.created_at = datetime()
        
        MERGE (class:Class {tenant_id: cls.tenant_id, repo_id: cls.repo_id, qualified_name: cls.qualified_name})
          ON CREATE SET class.name = cls.name,
                        class.start_line = cls.start_line,
                        class.end_line = cls.end_line,
                        class.base_classes = cls.base_classes,
                        class.docstring = cls.docstring,
                        class.created_at = datetime()
          ON MATCH SET class.last_indexed_at = datetime()
        
        MERGE (file)-[:CONTAINS]->(class)
        """

        try:
            with self.driver.session() as session:
                result = session.run(cypher, classes=classes)
                result.consume()

                duration = (datetime.now() - start_time).total_seconds() * 1000

                return BulkOperation(
                    operation_id=operation_id,
                    nodes_created=len(classes),
                    nodes_updated=0,
                    edges_created=len(classes),
                    edges_updated=0,
                    errors=[],
                    duration_ms=int(duration),
                )

        except Exception as e:
            logger.error(f"Bulk upsert classes failed: {e}")
            return BulkOperation(
                operation_id=operation_id,
                nodes_created=0,
                nodes_updated=0,
                edges_created=0,
                edges_updated=0,
                errors=[str(e)],
                duration_ms=0,
            )

    def create_implemented_by_edge(
        self,
        req_id: str,
        function_id: str,
        tenant_id: str,
        confidence: float,
        evidence_s3: str,
        method: str,
    ) -> bool:
        """Create IMPLEMENTED_BY edge between requirement and function"""
        cypher = """
        MATCH (r:Requirement {req_id: $req_id, tenant_id: $tenant_id})
        MATCH (f:Function {function_id: $function_id, tenant_id: $tenant_id})
        MERGE (r)-[e:IMPLEMENTED_BY]->(f)
        SET e.confidence = $confidence,
            e.evidence_snippet_s3 = $evidence_s3,
            e.match_method = $method,
            e.last_checked_at = datetime()
        RETURN e
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "req_id": req_id,
                        "function_id": function_id,
                        "tenant_id": tenant_id,
                        "confidence": confidence,
                        "evidence_s3": evidence_s3,
                        "method": method,
                    },
                )

                return result.single() is not None

        except Exception as e:
            logger.error(f"Failed to create IMPLEMENTED_BY edge: {e}")
            return False

    def create_call_edges(
        self, calls: List[Dict[str, Any]], tenant_id: str
    ) -> BulkOperation:
        """Create CALLS edges between functions"""
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()

        cypher = """
        UNWIND $calls AS call
        MATCH (from:Function {function_id: call.from_function_id, tenant_id: $tenant_id})
        MATCH (to:Function {function_id: call.to_function_id, tenant_id: $tenant_id})
        MERGE (from)-[e:CALLS]->(to)
        SET e.kind = call.kind,
            e.line = call.line,
            e.snippet_s3 = call.snippet_s3,
            e.confidence = call.confidence,
            e.created_at = datetime()
        """

        try:
            with self.driver.session() as session:
                result = session.run(cypher, calls=calls, tenant_id=tenant_id)
                result.consume()

                duration = (datetime.now() - start_time).total_seconds() * 1000

                return BulkOperation(
                    operation_id=operation_id,
                    nodes_created=0,
                    nodes_updated=0,
                    edges_created=len(calls),
                    edges_updated=0,
                    errors=[],
                    duration_ms=int(duration),
                )

        except Exception as e:
            logger.error(f"Bulk create call edges failed: {e}")
            return BulkOperation(
                operation_id=operation_id,
                nodes_created=0,
                nodes_updated=0,
                edges_created=0,
                edges_updated=0,
                errors=[str(e)],
                duration_ms=0,
            )

    def create_import_edges(
        self, imports: List[Dict[str, Any]], tenant_id: str
    ) -> BulkOperation:
        """Create IMPORT edges"""
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()

        cypher = """
        UNWIND $imports AS imp
        MATCH (file:File {file_id: imp.file_id, tenant_id: $tenant_id})
        MERGE (module:ExternalModule {name: imp.module_name, tenant_id: $tenant_id})
          ON CREATE SET module.version = imp.version,
                        module.purl = imp.purl,
                        module.created_at = datetime()
        
        MERGE (file)-[e:IMPORTS]->(module)
        SET e.line = imp.line,
            e.snippet_s3 = imp.snippet_s3,
            e.resolution_confidence = imp.resolution_confidence,
            e.created_at = datetime()
        """

        try:
            with self.driver.session() as session:
                result = session.run(cypher, imports=imports, tenant_id=tenant_id)
                result.consume()

                duration = (datetime.now() - start_time).total_seconds() * 1000

                return BulkOperation(
                    operation_id=operation_id,
                    nodes_created=len(imports),
                    nodes_updated=0,
                    edges_created=len(imports),
                    edges_updated=0,
                    errors=[],
                    duration_ms=int(duration),
                )

        except Exception as e:
            logger.error(f"Bulk create import edges failed: {e}")
            return BulkOperation(
                operation_id=operation_id,
                nodes_created=0,
                nodes_updated=0,
                edges_created=0,
                edges_updated=0,
                errors=[str(e)],
                duration_ms=0,
            )

    def search_functions(
        self, query: str, tenant_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search functions by name or signature"""
        cypher = """
        MATCH (f:Function {tenant_id: $tenant_id})
        WHERE f.name CONTAINS $query OR f.signature CONTAINS $query
        RETURN f.function_id as function_id,
               f.name as name,
               f.signature as signature,
               f.start_line as start_line,
               f.end_line as end_line,
               f.complexity_score as complexity_score
        ORDER BY f.name
        LIMIT $limit
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    cypher, query=query, tenant_id=tenant_id, limit=limit
                )
                return [dict(record) for record in result]

        except Exception as e:
            logger.error(f"Function search failed: {e}")
            return []

    def get_function_call_graph(
        self, function_id: str, tenant_id: str, depth: int = 2
    ) -> Dict[str, Any]:
        """Get call graph for a function"""
        cypher = """
        MATCH (f:Function {function_id: $function_id, tenant_id: $tenant_id})
        MATCH path = (f)-[:CALLS*1..$depth]->(called:Function)
        RETURN f, called, path
        ORDER BY length(path)
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    cypher, function_id=function_id, tenant_id=tenant_id, depth=depth
                )

                nodes = set()
                edges = []

                for record in result:
                    f = record["f"]
                    called = record["called"]
                    path = record["path"]

                    nodes.add((f["function_id"], f["name"], "function"))
                    nodes.add((called["function_id"], called["name"], "function"))

                    for rel in path.relationships:
                        edges.append(
                            {
                                "from": rel.start_node["function_id"],
                                "to": rel.end_node["function_id"],
                                "type": rel.type,
                                "confidence": rel.get("confidence", 0.0),
                            }
                        )

                return {
                    "nodes": [{"id": n[0], "name": n[1], "type": n[2]} for n in nodes],
                    "edges": edges,
                }

        except Exception as e:
            logger.error(f"Call graph query failed: {e}")
            return {"nodes": [], "edges": []}

    def get_repository_stats(self, repo_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get repository statistics"""
        cypher = """
        MATCH (r:Repo {repo_id: $repo_id, tenant_id: $tenant_id})
        OPTIONAL MATCH (r)-[:CONTAINS]->(f:File)
        OPTIONAL MATCH (f)-[:CONTAINS]->(func:Function)
        OPTIONAL MATCH (f)-[:CONTAINS]->(c:Class)
        OPTIONAL MATCH (f)-[:IMPORTS]->(m:ExternalModule)
        
        RETURN count(DISTINCT f) as file_count,
               count(DISTINCT func) as function_count,
               count(DISTINCT c) as class_count,
               count(DISTINCT m) as module_count,
               avg(func.complexity_score) as avg_complexity
        """

        try:
            with self.driver.session() as session:
                result = session.run(cypher, repo_id=repo_id, tenant_id=tenant_id)
                record = result.single()

                if record:
                    return {
                        "file_count": record["file_count"],
                        "function_count": record["function_count"],
                        "class_count": record["class_count"],
                        "module_count": record["module_count"],
                        "avg_complexity": record["avg_complexity"] or 0,
                    }
                else:
                    return {
                        "file_count": 0,
                        "function_count": 0,
                        "class_count": 0,
                        "module_count": 0,
                        "avg_complexity": 0,
                    }

        except Exception as e:
            logger.error(f"Repository stats query failed: {e}")
            return {
                "file_count": 0,
                "function_count": 0,
                "class_count": 0,
                "module_count": 0,
                "avg_complexity": 0,
            }

    def delete_repository(self, repo_id: str, tenant_id: str) -> bool:
        """Delete repository and all related data"""
        cypher = """
        MATCH (r:Repo {repo_id: $repo_id, tenant_id: $tenant_id})
        DETACH DELETE r
        
        MATCH (f:File {repo_id: $repo_id, tenant_id: $tenant_id})
        DETACH DELETE f
        
        MATCH (func:Function {repo_id: $repo_id, tenant_id: $tenant_id})
        DETACH DELETE func
        
        MATCH (c:Class {repo_id: $repo_id, tenant_id: $tenant_id})
        DETACH DELETE c
        
        MATCH (s:Symbol {repo_id: $repo_id, tenant_id: $tenant_id})
        DETACH DELETE s
        """

        try:
            with self.driver.session() as session:
                result = session.run(cypher, repo_id=repo_id, tenant_id=tenant_id)
                result.consume()
                return True

        except Exception as e:
            logger.error(f"Repository deletion failed: {e}")
            return False

    def create_audit_event(self, event: Dict[str, Any]) -> bool:
        """Create audit event"""
        cypher = """
        CREATE (a:AuditEvent {
            event_id: $event_id,
            actor_id: $actor_id,
            action: $action,
            target_ids: $target_ids,
            details: $details,
            timestamp: datetime($timestamp)
        })
        """

        try:
            with self.driver.session() as session:
                session.run(cypher, **event)
                return True

        except Exception as e:
            logger.error(f"Audit event creation failed: {e}")
            return False


class GraphService:
    """High-level graph service for RepoLens operations"""

    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def index_repository(
        self, repo_data: Dict[str, Any], parsed_files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Index entire repository into graph"""
        tenant_id = repo_data["tenant_id"]
        repo_id = repo_data["repo_id"]

        # Create repository node
        repo_cypher = """
        MERGE (r:Repo {tenant_id: $tenant_id, repo_id: $repo_id})
        SET r.url = $url,
            r.default_branch = $branch,
            r.last_indexed_commit = $commit,
            r.created_at = datetime(),
            r.last_indexed_at = datetime()
        """

        with self.neo4j.driver.session() as session:
            session.run(repo_cypher, **repo_data)

        # Bulk upsert files and functions
        functions = []
        classes = []

        for file_path, parsed_file in parsed_files.items():
            if parsed_file["status"] == "parsed":
                # Prepare function data
                for func in parsed_file["functions"]:
                    functions.append(
                        {
                            "tenant_id": tenant_id,
                            "repo_id": repo_id,
                            "file_path": file_path,
                            "language": parsed_file["language"],
                            "file_hash": parsed_file["file_hash"],
                            "qualified_name": func["qualified_name"],
                            "name": func["name"],
                            "signature": func["signature"],
                            "start_line": func["start_line"],
                            "end_line": func["end_line"],
                            "code_hash": func["code_hash"],
                            "snippet_s3_path": func["snippet_s3_path"],
                            "summary_det": func["summary_det"],
                            "complexity_score": func["complexity_score"],
                        }
                    )

                # Prepare class data
                for cls in parsed_file["classes"]:
                    classes.append(
                        {
                            "tenant_id": tenant_id,
                            "repo_id": repo_id,
                            "file_path": file_path,
                            "language": parsed_file["language"],
                            "file_hash": parsed_file["file_hash"],
                            "qualified_name": cls["qualified_name"],
                            "name": cls["name"],
                            "start_line": cls["start_line"],
                            "end_line": cls["end_line"],
                            "base_classes": cls["base_classes"],
                            "docstring": cls["docstring"],
                        }
                    )

        # Execute bulk operations
        func_result = self.neo4j.bulk_upsert_functions(functions, tenant_id)
        class_result = self.neo4j.bulk_upsert_classes(classes, tenant_id)

        return {
            "repository_id": repo_id,
            "functions_indexed": func_result.nodes_created,
            "classes_indexed": class_result.nodes_created,
            "total_operations": func_result.duration_ms + class_result.duration_ms,
            "errors": func_result.errors + class_result.errors,
        }


if __name__ == "__main__":
    # Test Neo4j service
    neo4j_service = Neo4jService(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password"),
    )

    # Test bulk upsert
    test_functions = [
        {
            "tenant_id": "test_tenant",
            "repo_id": "test_repo",
            "file_path": "src/main.py",
            "language": "python",
            "file_hash": "abc123",
            "qualified_name": "main.hello",
            "name": "hello",
            "signature": "def hello(name: str) -> str:",
            "start_line": 1,
            "end_line": 5,
            "code_hash": "def123",
            "snippet_s3_path": "s3://bucket/snippet.json",
            "summary_det": "Hello function",
            "complexity_score": 1,
        }
    ]

    result = neo4j_service.bulk_upsert_functions(test_functions, "test_tenant")
    print(f"Bulk upsert result: {result}")

    neo4j_service.close()
