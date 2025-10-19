# RepoLens Analysis Service
# Complete codebase analysis with Tree-sitter + Neo4j integration

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.neo4j_service import Neo4jService
from app.services.parser_service import ParserService
from app.services.project_service import ProjectService, StorageManager


logger = logging.getLogger(__name__)


class AnalysisService:
    """Complete codebase analysis service"""

    def __init__(self):
        self.parser_service = ParserService()
        self.storage_manager = StorageManager()
        # Neo4j service will be injected
        self.neo4j_service: Optional[Neo4jService] = None

    async def analyze_project(
        self,
        project_id: str,
        tenant_id: str,
        analysis_type: str = "full",
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Perform complete project analysis"""
        try:
            logger.info(f"Starting analysis for project {project_id}")

            # Get project path
            project_path = self.storage_manager.get_project_path(project_id)
            if not project_path.exists():
                raise ValueError(f"Project path not found: {project_path}")

            # Parse all files in the project
            parsed_files = await self._parse_project_files(project_path)

            # Create Neo4j graph representation
            graph_data = await self._create_graph_representation(
                project_id, tenant_id, parsed_files
            )

            # Store in Neo4j
            if self.neo4j_service:
                await self._store_in_neo4j(project_id, tenant_id, graph_data)

            # Generate analysis summary
            analysis_summary = self._generate_analysis_summary(parsed_files, graph_data)

            logger.info(f"Analysis completed for project {project_id}")

            return {
                "analysis_id": str(uuid.uuid4()),
                "project_id": project_id,
                "status": "completed",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "summary": analysis_summary,
                "graph_data": graph_data,
            }

        except Exception as e:
            logger.error(f"Analysis failed for project {project_id}: {e}")
            return {
                "analysis_id": str(uuid.uuid4()),
                "project_id": project_id,
                "status": "error",
                "error": str(e),
                "started_at": datetime.now(timezone.utc).isoformat(),
            }

    async def _parse_project_files(self, project_path: Path) -> Dict[str, Any]:
        """Parse all files in the project using Tree-sitter"""
        parsed_files = {}

        # Get all supported files
        supported_extensions = set()
        for lang_config in self.parser_service.supported_languages.values():
            supported_extensions.update(lang_config["extensions"])

        # Find all files
        files_to_parse = []
        for ext in supported_extensions:
            files_to_parse.extend(project_path.rglob(f"*{ext}"))

        logger.info(f"Found {len(files_to_parse)} files to parse")

        # Parse each file
        for file_path in files_to_parse:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse using Tree-sitter
                parsed = self.parser_service.parse_file(str(file_path), content)

                parsed_files[str(file_path)] = {
                    "path": str(file_path),
                    "language": parsed.language,
                    "functions": parsed.functions,
                    "classes": parsed.classes,
                    "imports": parsed.imports,
                    "complexity_score": parsed.complexity_score,
                    "lines_of_code": parsed.lines_of_code,
                    "docstring": parsed.docstring,
                }

            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                continue

        return parsed_files

    async def _create_graph_representation(
        self, project_id: str, tenant_id: str, parsed_files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comprehensive graph representation"""
        nodes = []
        edges = []

        # Create file nodes
        for file_path, file_data in parsed_files.items():
            file_id = f"file_{uuid.uuid4().hex[:8]}"

            nodes.append(
                {
                    "id": file_id,
                    "type": "file",
                    "name": Path(file_path).name,
                    "path": file_path,
                    "language": file_data["language"],
                    "lines_of_code": file_data["lines_of_code"],
                    "complexity_score": file_data["complexity_score"],
                    "project_id": project_id,
                    "tenant_id": tenant_id,
                }
            )

            # Create function nodes and edges
            for func in file_data["functions"]:
                func_id = f"func_{uuid.uuid4().hex[:8]}"

                nodes.append(
                    {
                        "id": func_id,
                        "type": "function",
                        "name": func["name"],
                        "signature": func["signature"],
                        "complexity": func["complexity"],
                        "line_start": func["line_start"],
                        "line_end": func["line_end"],
                        "file_id": file_id,
                        "project_id": project_id,
                        "tenant_id": tenant_id,
                    }
                )

                # File contains function
                edges.append(
                    {
                        "from": file_id,
                        "to": func_id,
                        "type": "contains",
                        "relationship": "file_contains_function",
                    }
                )

            # Create class nodes and edges
            for cls in file_data["classes"]:
                class_id = f"class_{uuid.uuid4().hex[:8]}"

                nodes.append(
                    {
                        "id": class_id,
                        "type": "class",
                        "name": cls["name"],
                        "line_start": cls["line_start"],
                        "line_end": cls["line_end"],
                        "file_id": file_id,
                        "project_id": project_id,
                        "tenant_id": tenant_id,
                    }
                )

                # File contains class
                edges.append(
                    {
                        "from": file_id,
                        "to": class_id,
                        "type": "contains",
                        "relationship": "file_contains_class",
                    }
                )

            # Create import edges
            for import_path in file_data["imports"]:
                # Find target file if it exists in the project
                target_file_id = self._find_target_file(import_path, parsed_files)
                if target_file_id:
                    edges.append(
                        {
                            "from": file_id,
                            "to": target_file_id,
                            "type": "imports",
                            "relationship": "file_imports_file",
                            "import_path": import_path,
                        }
                    )

        # Create function call edges (simplified - would need more sophisticated analysis)
        edges.extend(self._analyze_function_calls(parsed_files))

        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": self._calculate_statistics(parsed_files, nodes, edges),
        }

    def _find_target_file(
        self, import_path: str, parsed_files: Dict[str, Any]
    ) -> Optional[str]:
        """Find target file for an import (simplified)"""
        # This would need more sophisticated module resolution
        for file_path, file_data in parsed_files.items():
            if import_path in file_path:
                return f"file_{hash(file_path) % 1000000:06d}"
        return None

    def _analyze_function_calls(
        self, parsed_files: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze function calls between functions (simplified)"""
        edges = []

        # This is a simplified version - real implementation would need
        # sophisticated call graph analysis using Tree-sitter AST traversal

        for file_path, file_data in parsed_files.items():
            file_functions = {f["name"]: f for f in file_data["functions"]}

            # Look for function calls within the same file
            for func_name, func_data in file_functions.items():
                func_id = f"func_{hash(f'{file_path}_{func_name}') % 1000000:06d}"

                # Check if this function calls other functions in the same file
                for other_func_name in file_functions:
                    if other_func_name != func_name:
                        # Simple heuristic: if function names appear in signature
                        if other_func_name.lower() in func_data["signature"].lower():
                            other_func_id = f"func_{hash(f'{file_path}_{other_func_name}') % 1000000:06d}"
                            edges.append(
                                {
                                    "from": func_id,
                                    "to": other_func_id,
                                    "type": "calls",
                                    "relationship": "function_calls_function",
                                    "confidence": 0.7,  # Simplified confidence score
                                }
                            )

        return edges

    def _calculate_statistics(
        self, parsed_files: Dict[str, Any], nodes: List[Dict], edges: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate analysis statistics"""
        total_files = len(parsed_files)
        total_functions = sum(len(f["functions"]) for f in parsed_files.values())
        total_classes = sum(len(f["classes"]) for f in parsed_files.values())
        total_lines = sum(f["lines_of_code"] for f in parsed_files.values())

        languages = {}
        for file_data in parsed_files.values():
            lang = file_data["language"]
            languages[lang] = languages.get(lang, 0) + 1

        return {
            "total_files": total_files,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_lines_of_code": total_lines,
            "languages": languages,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "average_complexity": sum(
                f["complexity_score"] for f in parsed_files.values()
            )
            / max(total_files, 1),
        }

    def _generate_analysis_summary(
        self, parsed_files: Dict[str, Any], graph_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate human-readable analysis summary"""
        stats = graph_data["statistics"]

        return {
            "overview": f"Analyzed {stats['total_files']} files with {stats['total_functions']} functions and {stats['total_classes']} classes",
            "codebase_size": f"{stats['total_lines_of_code']:,} lines of code",
            "language_distribution": stats["languages"],
            "complexity": f"Average complexity score: {stats['average_complexity']:.1f}",
            "architecture": f"Graph contains {stats['total_nodes']} nodes and {stats['total_edges']} relationships",
        }

    async def _store_in_neo4j(
        self, project_id: str, tenant_id: str, graph_data: Dict[str, Any]
    ):
        """Store graph data in Neo4j"""
        if not self.neo4j_service:
            logger.warning("Neo4j service not available, skipping graph storage")
            return

        try:
            # Store nodes
            for node in graph_data["nodes"]:
                await self._store_node(node)

            # Store edges
            for edge in graph_data["edges"]:
                await self._store_edge(edge)

            logger.info(
                f"Stored {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges in Neo4j"
            )

        except Exception as e:
            logger.error(f"Failed to store graph in Neo4j: {e}")

    async def _store_node(self, node: Dict[str, Any]):
        """Store a single node in Neo4j"""
        cypher = f"""
        MERGE (n:{node['type'].title()} {{id: $id, tenant_id: $tenant_id}})
        SET n += $properties
        """

        properties = {k: v for k, v in node.items() if k not in ["id", "type"]}

        with self.neo4j_service.driver.session() as session:
            session.run(
                cypher,
                id=node["id"],
                tenant_id=node["tenant_id"],
                properties=properties,
            )

    async def _store_edge(self, edge: Dict[str, Any]):
        """Store a single edge in Neo4j"""
        cypher = f"""
        MATCH (from {{id: $from_id, tenant_id: $tenant_id}})
        MATCH (to {{id: $to_id, tenant_id: $tenant_id}})
        MERGE (from)-[r:{edge['type'].upper()}]->(to)
        SET r += $properties
        """

        properties = {k: v for k, v in edge.items() if k not in ["from", "to", "type"]}

        with self.neo4j_service.driver.session() as session:
            session.run(
                cypher,
                from_id=edge["from"],
                to_id=edge["to"],
                tenant_id=edge.get("tenant_id", ""),
                properties=properties,
            )
