# RepoLens Advanced Analysis Service
# Complete codebase analysis with real-time progress, background processing, and AI insights

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from app.features.ai_analysis.services.ai_analyzer_service import AIAnalyzerService
from app.services.neo4j_service import Neo4jService
from app.services.parser_service import ParserService
from app.services.project_service import ProjectService, StorageManager
from app.services.session_manager import session_manager


logger = logging.getLogger(__name__)


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    STORING = "storing"
    AI_ANALYSIS = "ai_analysis"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AnalysisProgress:
    """Analysis progress tracking"""

    analysis_id: str
    project_id: str
    status: AnalysisStatus
    progress_percentage: float
    current_step: str
    total_files: int = 0
    parsed_files: int = 0
    total_functions: int = 0
    analyzed_functions: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AdvancedAnalysisService:
    """Advanced analysis service with real-time progress and AI insights"""

    def __init__(self):
        self.parser_service = ParserService()
        self.storage_manager = StorageManager()
        self.ai_service = AIAnalyzerService()
        self.neo4j_service: Optional[Neo4jService] = None

        # Redis-based progress tracking
        self.analysis_prefix = "analysis:"
        self.progress_callbacks: Dict[str, Callable] = {}

    def set_neo4j_service(self, neo4j_service: Neo4jService):
        """Inject Neo4j service"""
        self.neo4j_service = neo4j_service

    def register_progress_callback(
        self, analysis_id: str, callback: Callable[[AnalysisProgress], None]
    ):
        """Register callback for progress updates"""
        self.progress_callbacks[analysis_id] = callback

    async def _store_progress_in_redis(
        self, analysis_id: str, progress: AnalysisProgress
    ):
        """Store analysis progress in Redis"""
        try:
            analysis_key = f"{self.analysis_prefix}{analysis_id}"

            # Convert progress to dict for JSON serialization
            progress_dict = {
                "analysis_id": progress.analysis_id,
                "project_id": progress.project_id,
                "status": progress.status.value,
                "progress_percentage": progress.progress_percentage,
                "current_step": progress.current_step,
                "total_files": progress.total_files,
                "parsed_files": progress.parsed_files,
                "total_functions": progress.total_functions,
                "analyzed_functions": progress.analyzed_functions,
                "error_message": progress.error_message,
                "started_at": (
                    progress.started_at.isoformat() if progress.started_at else None
                ),
                "completed_at": (
                    progress.completed_at.isoformat() if progress.completed_at else None
                ),
            }

            # Store in Redis with 24-hour expiration
            await session_manager.redis_client.setex(
                analysis_key, 24 * 60 * 60, json.dumps(progress_dict)  # 24 hours
            )

        except Exception as e:
            logger.error(f"Failed to store progress in Redis: {e}")

    async def _get_progress_from_redis(
        self, analysis_id: str
    ) -> Optional[AnalysisProgress]:
        """Get analysis progress from Redis"""
        try:
            analysis_key = f"{self.analysis_prefix}{analysis_id}"
            progress_data = await session_manager.redis_client.get(analysis_key)

            if progress_data:
                progress_dict = json.loads(progress_data)

                return AnalysisProgress(
                    analysis_id=progress_dict["analysis_id"],
                    project_id=progress_dict["project_id"],
                    status=AnalysisStatus(progress_dict["status"]),
                    progress_percentage=progress_dict["progress_percentage"],
                    current_step=progress_dict["current_step"],
                    total_files=progress_dict["total_files"],
                    parsed_files=progress_dict["parsed_files"],
                    total_functions=progress_dict["total_functions"],
                    analyzed_functions=progress_dict["analyzed_functions"],
                    error_message=progress_dict["error_message"],
                    started_at=(
                        datetime.fromisoformat(progress_dict["started_at"])
                        if progress_dict["started_at"]
                        else None
                    ),
                    completed_at=(
                        datetime.fromisoformat(progress_dict["completed_at"])
                        if progress_dict["completed_at"]
                        else None
                    ),
                )

        except Exception as e:
            logger.error(f"Failed to get progress from Redis: {e}")

        return None

    async def _update_progress(self, analysis_id: str, **updates):
        """Update analysis progress in Redis and notify callbacks"""
        try:
            # Get current progress from Redis
            progress = await self._get_progress_from_redis(analysis_id)

            if progress:
                # Update progress fields
                for key, value in updates.items():
                    setattr(progress, key, value)

                # Store updated progress in Redis
                await self._store_progress_in_redis(analysis_id, progress)

                # Notify callback if registered
                if analysis_id in self.progress_callbacks:
                    try:
                        self.progress_callbacks[analysis_id](progress)
                    except Exception as e:
                        logger.error(f"Progress callback failed: {e}")
            else:
                logger.warning(f"Analysis {analysis_id} not found in Redis")

        except Exception as e:
            logger.error(f"Failed to update progress: {e}")

    async def analyze_project_async(
        self,
        project_id: str,
        tenant_id: str,
        analysis_type: str = "full",
        force_refresh: bool = False,
    ) -> str:
        """Start background analysis and return analysis ID"""
        analysis_id = str(uuid.uuid4())

        logger.info(f"Starting analysis {analysis_id} for project {project_id}")

        # Initialize progress tracking
        progress = AnalysisProgress(
            analysis_id=analysis_id,
            project_id=project_id,
            status=AnalysisStatus.STARTED,
            progress_percentage=0.0,
            current_step="Initializing analysis",
            started_at=datetime.now(timezone.utc),
        )

            # Store initial progress in Redis
            await self._store_progress_in_redis(analysis_id, progress)

            # Start background task
            asyncio.create_task(
                self._run_analysis_background(
                    analysis_id, project_id, tenant_id, analysis_type, force_refresh
                )
            )
        return analysis_id

    async def _run_analysis_background(
        self,
        analysis_id: str,
        project_id: str,
        tenant_id: str,
        analysis_type: str,
        force_refresh: bool,
    ):
        """Run analysis in background with progress tracking"""
        try:

            # Step 1: Project Discovery
            await self._update_progress(
                analysis_id,
                status=AnalysisStatus.PARSING,
                current_step="Discovering project files",
                progress_percentage=5.0,
            )

            project_path = self.storage_manager.get_project_path(project_id)
            if not project_path.exists():
                raise ValueError(
                    f"Project path not found: {project_path}. Please ensure the project has been cloned first."
                )

            # Step 2: File Discovery
            files_to_parse = await self._discover_files(project_path)
            await self._update_progress(
                analysis_id,
                total_files=len(files_to_parse),
                current_step=f"Found {len(files_to_parse)} files to analyze",
                progress_percentage=10.0,
            )

            # Step 3: Parse Files with Progress
            parsed_files = await self._parse_files_with_progress(
                analysis_id, files_to_parse
            )

            # Step 4: Advanced Call Graph Analysis
            await self._update_progress(
                analysis_id,
                status=AnalysisStatus.ANALYZING,
                current_step="Analyzing function call graphs",
                progress_percentage=60.0,
            )

            call_graph = await self._analyze_call_graphs(parsed_files)

            # Step 5: Create Comprehensive Graph
            await self._update_progress(
                analysis_id,
                current_step="Creating comprehensive graph representation",
                progress_percentage=70.0,
            )

            graph_data = await self._create_comprehensive_graph(
                project_id, tenant_id, parsed_files, call_graph
            )

            # Step 6: Store in Neo4j
            await self._update_progress(
                analysis_id,
                status=AnalysisStatus.STORING,
                current_step="Storing graph in Neo4j",
                progress_percentage=80.0,
            )

            if self.neo4j_service:
                await self._store_comprehensive_graph(project_id, tenant_id, graph_data)

            # Step 7: AI Analysis
            await self._update_progress(
                analysis_id,
                status=AnalysisStatus.AI_ANALYSIS,
                current_step="Running AI-powered insights",
                progress_percentage=90.0,
            )

            ai_insights = await self._generate_ai_insights(graph_data)

            # Step 8: Complete
            await self._update_progress(
                analysis_id,
                status=AnalysisStatus.COMPLETED,
                current_step="Analysis completed successfully",
                progress_percentage=100.0,
                completed_at=datetime.now(timezone.utc),
            )

            # Step 9: Update project analysis count and last analyzed timestamp
            await self._update_project_analysis_stats(project_id, tenant_id)


        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}")
            await self._update_progress(
                analysis_id,
                status=AnalysisStatus.ERROR,
                current_step=f"Analysis failed: {str(e)}",
                error_message=str(e),
                completed_at=datetime.now(timezone.utc),
            )

    async def _discover_files(self, project_path: Path) -> List[Path]:
        """Discover all files to parse"""
        supported_extensions = set()
        for lang_config in self.parser_service.supported_languages.values():
            supported_extensions.update(lang_config["extensions"])

        files_to_parse = []
        for ext in supported_extensions:
            files_to_parse.extend(project_path.rglob(f"*{ext}"))

        return files_to_parse

    async def _parse_files_with_progress(
        self, analysis_id: str, files: List[Path]
    ) -> Dict[str, Any]:
        """Parse files with progress tracking"""
        parsed_files = {}
        total_files = len(files)

        for i, file_path in enumerate(files):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

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

                # Update progress
                progress_percentage = 10.0 + (i / total_files) * 50.0
                await self._update_progress(
                    analysis_id,
                    parsed_files=i + 1,
                    current_step=f"Parsed {i + 1}/{total_files} files",
                    progress_percentage=progress_percentage,
                )

            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                continue

        return parsed_files

    async def _analyze_call_graphs(
        self, parsed_files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Advanced call graph analysis"""
        call_graph = {
            "function_calls": [],
            "class_inheritance": [],
            "module_dependencies": [],
            "cross_file_calls": [],
        }

        # Analyze function calls within files
        for file_path, file_data in parsed_files.items():
            functions = file_data["functions"]

            for func in functions:
                func_id = f"func_{hash(f'{file_path}_{func['name']}') % 1000000:06d}"

                # Find function calls in the function body (simplified)
                calls = self._extract_function_calls(func["signature"], functions)
                for called_func in calls:
                    called_func_id = (
                        f"func_{hash(f'{file_path}_{called_func}') % 1000000:06d}"
                    )
                    call_graph["function_calls"].append(
                        {
                            "from": func_id,
                            "to": called_func_id,
                            "file": file_path,
                            "confidence": 0.8,
                        }
                    )

        # Analyze cross-file calls
        call_graph["cross_file_calls"] = await self._analyze_cross_file_calls(
            parsed_files
        )

        return call_graph

    def _extract_function_calls(
        self, signature: str, functions: List[Dict]
    ) -> List[str]:
        """Extract function calls from function signature (simplified)"""
        calls = []
        for func in functions:
            if func["name"] != signature and func["name"].lower() in signature.lower():
                calls.append(func["name"])
        return calls

    async def _analyze_cross_file_calls(
        self, parsed_files: Dict[str, Any]
    ) -> List[Dict]:
        """Analyze function calls across files"""
        cross_file_calls = []

        # Create function registry
        function_registry = {}
        for file_path, file_data in parsed_files.items():
            for func in file_data["functions"]:
                func_id = f"func_{hash(f'{file_path}_{func['name']}') % 1000000:06d}"
                function_registry[func["name"]] = {
                    "id": func_id,
                    "file": file_path,
                    "signature": func["signature"],
                }

        # Find cross-file calls
        for file_path, file_data in parsed_files.items():
            for func in file_data["functions"]:
                func_id = f"func_{hash(f'{file_path}_{func['name']}') % 1000000:06d}"

                # Look for calls to functions defined in other files
                for func_name, func_info in function_registry.items():
                    if func_info["file"] != file_path:
                        if func_name.lower() in func["signature"].lower():
                            cross_file_calls.append(
                                {
                                    "from": func_id,
                                    "to": func_info["id"],
                                    "from_file": file_path,
                                    "to_file": func_info["file"],
                                    "function_name": func_name,
                                    "confidence": 0.7,
                                }
                            )

        return cross_file_calls

    async def _create_comprehensive_graph(
        self,
        project_id: str,
        tenant_id: str,
        parsed_files: Dict[str, Any],
        call_graph: Dict[str, Any],
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

            # Create function nodes
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

                edges.append(
                    {
                        "from": file_id,
                        "to": func_id,
                        "type": "contains",
                        "relationship": "file_contains_function",
                    }
                )

            # Create class nodes
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

                edges.append(
                    {
                        "from": file_id,
                        "to": class_id,
                        "type": "contains",
                        "relationship": "file_contains_class",
                    }
                )

        # Add call graph edges
        for call in call_graph["function_calls"]:
            edges.append(
                {
                    "from": call["from"],
                    "to": call["to"],
                    "type": "calls",
                    "relationship": "function_calls_function",
                    "confidence": call["confidence"],
                }
            )

        for cross_call in call_graph["cross_file_calls"]:
            edges.append(
                {
                    "from": cross_call["from"],
                    "to": cross_call["to"],
                    "type": "cross_file_calls",
                    "relationship": "function_calls_function",
                    "confidence": cross_call["confidence"],
                    "from_file": cross_call["from_file"],
                    "to_file": cross_call["to_file"],
                }
            )

        return {
            "nodes": nodes,
            "edges": edges,
            "call_graph": call_graph,
            "statistics": self._calculate_comprehensive_statistics(
                parsed_files, nodes, edges
            ),
        }

    def _calculate_comprehensive_statistics(
        self, parsed_files: Dict[str, Any], nodes: List[Dict], edges: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate comprehensive analysis statistics"""
        total_files = len(parsed_files)
        total_functions = sum(len(f["functions"]) for f in parsed_files.values())
        total_classes = sum(len(f["classes"]) for f in parsed_files.values())
        total_lines = sum(f["lines_of_code"] for f in parsed_files.values())

        languages = {}
        for file_data in parsed_files.values():
            lang = file_data["language"]
            languages[lang] = languages.get(lang, 0) + 1

        # Calculate complexity metrics
        complexity_scores = [f["complexity_score"] for f in parsed_files.values()]
        avg_complexity = sum(complexity_scores) / max(len(complexity_scores), 1)

        # Calculate coupling metrics
        cross_file_calls = len(
            [e for e in edges if e.get("type") == "cross_file_calls"]
        )
        coupling_ratio = cross_file_calls / max(total_functions, 1)

        return {
            "total_files": total_files,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_lines_of_code": total_lines,
            "languages": languages,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "average_complexity": avg_complexity,
            "cross_file_calls": cross_file_calls,
            "coupling_ratio": coupling_ratio,
            "architecture_score": self._calculate_architecture_score(
                parsed_files, edges
            ),
        }

    def _calculate_architecture_score(
        self, parsed_files: Dict[str, Any], edges: List[Dict]
    ) -> float:
        """Calculate architecture quality score (0-10)"""
        score = 10.0

        # Penalize high coupling
        cross_file_calls = len(
            [e for e in edges if e.get("type") == "cross_file_calls"]
        )
        total_functions = sum(len(f["functions"]) for f in parsed_files.values())
        if total_functions > 0:
            coupling_ratio = cross_file_calls / total_functions
            if coupling_ratio > 0.3:
                score -= 2.0
            elif coupling_ratio > 0.1:
                score -= 1.0

        # Penalize high complexity
        avg_complexity = sum(
            f["complexity_score"] for f in parsed_files.values()
        ) / max(len(parsed_files), 1)
        if avg_complexity > 5:
            score -= 2.0
        elif avg_complexity > 3:
            score -= 1.0

        # Reward good organization
        languages = {}
        for file_data in parsed_files.values():
            lang = file_data["language"]
            languages[lang] = languages.get(lang, 0) + 1

        if len(languages) == 1:
            score += 1.0  # Single language is often better

        return max(0.0, min(10.0, score))

    async def _store_comprehensive_graph(
        self, project_id: str, tenant_id: str, graph_data: Dict[str, Any]
    ):
        """Store comprehensive graph in Neo4j"""
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
                f"Stored comprehensive graph: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges"
            )

        except Exception as e:
            logger.error(f"Failed to store comprehensive graph in Neo4j: {e}")

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

    async def _generate_ai_insights(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights"""
        try:
            # Prepare data for AI analysis
            ai_data = {
                "nodes": graph_data["nodes"],
                "edges": graph_data["edges"],
                "statistics": graph_data["statistics"],
                "call_graph": graph_data.get("call_graph", {}),
            }

            # Get AI insights
            insights = await self.ai_service.analyze_codebase(ai_data)

            return {
                "ai_insights": insights,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")
            return {
                "ai_insights": {"error": str(e)},
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

    def get_analysis_progress(self, analysis_id: str) -> Optional[AnalysisProgress]:
        """Get current analysis progress from Redis"""
        # This method needs to be async to work with Redis
        # We'll update the API endpoint to handle this
        return None

    async def get_analysis_progress_async(
        self, analysis_id: str
    ) -> Optional[AnalysisProgress]:
        """Get current analysis progress from Redis (async version)"""
        return await self._get_progress_from_redis(analysis_id)

    def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis result if completed"""
        # This method needs to be async to work with Redis
        # We'll update the API endpoint to handle this
        return None

    async def get_analysis_result_async(
        self, analysis_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get analysis result if completed (async version)"""
        progress = await self._get_progress_from_redis(analysis_id)
        if progress and progress.status == AnalysisStatus.COMPLETED:
            return {
                "analysis_id": analysis_id,
                "project_id": progress.project_id,
                "status": progress.status.value,
                "started_at": (
                    progress.started_at.isoformat() if progress.started_at else None
                ),
                "completed_at": (
                    progress.completed_at.isoformat() if progress.completed_at else None
                ),
                "statistics": {
                    "total_files": progress.total_files,
                    "parsed_files": progress.parsed_files,
                    "total_functions": progress.total_functions,
                    "analyzed_functions": progress.analyzed_functions,
                    "progress_percentage": progress.progress_percentage,
                },
            }
        return None

    async def _update_project_analysis_stats(self, project_id: str, tenant_id: str):
        """Update project analysis count and last analyzed timestamp"""
        try:
            from app.database.connection import get_db
            from app.database.models.project import Project
            from sqlalchemy import update
            
            async for db in get_db():
                # Update analysis count and last analyzed timestamp
                await db.execute(
                    update(Project)
                    .where(Project.id == project_id)
                    .where(Project.tenant_id == tenant_id)
                    .values(
                        analysis_count=Project.analysis_count + 1,
                        last_analyzed_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                )
                await db.commit()
                break
                
        except Exception as e:
            logger.error(f"Failed to update project analysis stats: {e}")

    async def get_incremental_updates(
        self, project_id: str, last_analysis_time: datetime
    ) -> Dict[str, Any]:
        """Get incremental analysis updates since last analysis"""
        # This would implement incremental analysis by:
        # 1. Checking git commits since last_analysis_time
        # 2. Only parsing changed files
        # 3. Updating the graph incrementally

        return {
            "incremental": True,
            "changed_files": [],
            "updated_functions": [],
            "new_dependencies": [],
            "analysis_time": datetime.now(timezone.utc).isoformat(),
        }
