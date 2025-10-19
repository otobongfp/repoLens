# RepoLens Symbol Resolver Service
# Symbol resolution with heuristics and call graph analysis

import logging
import os
import re
import uuid
from dataclasses import dataclass
from typing import Any, Optional


logger = logging.getLogger(__name__)


@dataclass
class SymbolReference:
    """Symbol reference with context"""

    symbol_id: str
    symbol_name: str
    symbol_type: str  # 'function', 'class', 'variable', 'import'
    file_path: str
    line_number: int
    context: str
    confidence: float
    resolution_method: str


@dataclass
class SymbolDefinition:
    """Symbol definition"""

    symbol_id: str
    symbol_name: str
    symbol_type: str
    file_path: str
    line_number: int
    signature: Optional[str]
    docstring: Optional[str]
    parameters: list[str]
    return_type: Optional[str]


@dataclass
class ResolutionResult:
    """Symbol resolution result"""

    reference: SymbolReference
    definition: Optional[SymbolDefinition]
    confidence: float
    resolution_path: list[str]
    errors: list[str]


class SymbolResolver:
    """Symbol resolver with heuristics and call graph analysis"""

    def __init__(self, neo4j_service):
        self.neo4j_service = neo4j_service
        self.symbol_cache: dict[str, SymbolDefinition] = {}
        self.import_cache: dict[str, list[str]] = {}

        # Language-specific patterns
        self.patterns = {
            "python": {
                "function_call": r"(\w+)\s*\(",
                "method_call": r"(\w+)\.(\w+)\s*\(",
                "class_instantiation": r"(\w+)\s*\(",
                "import_statement": r"(?:from\s+(\S+)\s+)?import\s+(\S+)",
                "variable_assignment": r"(\w+)\s*=",
                "attribute_access": r"(\w+)\.(\w+)",
            },
            "javascript": {
                "function_call": r"(\w+)\s*\(",
                "method_call": r"(\w+)\.(\w+)\s*\(",
                "class_instantiation": r"new\s+(\w+)\s*\(",
                "import_statement": r'(?:import\s+.*?from\s+)?[\'"]([^\'"]+)[\'"]',
                "variable_assignment": r"(?:const|let|var)\s+(\w+)",
                "attribute_access": r"(\w+)\.(\w+)",
            },
            "typescript": {
                "function_call": r"(\w+)\s*\(",
                "method_call": r"(\w+)\.(\w+)\s*\(",
                "class_instantiation": r"new\s+(\w+)\s*\(",
                "import_statement": r'(?:import\s+.*?from\s+)?[\'"]([^\'"]+)[\'"]',
                "variable_assignment": r"(?:const|let|var)\s+(\w+)",
                "attribute_access": r"(\w+)\.(\w+)",
            },
        }

    def resolve_symbol(
        self,
        symbol_name: str,
        file_path: str,
        line_number: int,
        language: str,
        tenant_id: str,
        repo_id: str,
    ) -> ResolutionResult:
        """Resolve symbol to its definition"""
        reference = SymbolReference(
            symbol_id=str(uuid.uuid4()),
            symbol_name=symbol_name,
            symbol_type="unknown",
            file_path=file_path,
            line_number=line_number,
            context="",
            confidence=0.0,
            resolution_method="unknown",
        )

        try:
            # Step 1: Determine symbol type
            symbol_type = self._determine_symbol_type(
                symbol_name, file_path, line_number, language
            )
            reference.symbol_type = symbol_type

            # Step 2: Try different resolution methods
            definition = None
            confidence = 0.0
            resolution_path = []
            errors = []

            # Method 1: Local scope resolution
            definition, confidence = self._resolve_local_scope(
                symbol_name, file_path, language, tenant_id, repo_id
            )
            if definition:
                resolution_path.append("local_scope")
                reference.resolution_method = "local_scope"

            # Method 2: Import resolution
            if not definition:
                definition, confidence = self._resolve_import(
                    symbol_name, file_path, language, tenant_id, repo_id
                )
                if definition:
                    resolution_path.append("import")
                    reference.resolution_method = "import"

            # Method 3: Cross-file resolution
            if not definition:
                definition, confidence = self._resolve_cross_file(
                    symbol_name, file_path, language, tenant_id, repo_id
                )
                if definition:
                    resolution_path.append("cross_file")
                    reference.resolution_method = "cross_file"

            # Method 4: Call graph resolution
            if not definition:
                definition, confidence = self._resolve_call_graph(
                    symbol_name, file_path, tenant_id, repo_id
                )
                if definition:
                    resolution_path.append("call_graph")
                    reference.resolution_method = "call_graph"

            # Method 5: Heuristic resolution
            if not definition:
                definition, confidence = self._resolve_heuristic(
                    symbol_name, file_path, language, tenant_id, repo_id
                )
                if definition:
                    resolution_path.append("heuristic")
                    reference.resolution_method = "heuristic"

            reference.confidence = confidence

            return ResolutionResult(
                reference=reference,
                definition=definition,
                confidence=confidence,
                resolution_path=resolution_path,
                errors=errors,
            )

        except Exception as e:
            logger.error(f"Symbol resolution failed for {symbol_name}: {e}")
            return ResolutionResult(
                reference=reference,
                definition=None,
                confidence=0.0,
                resolution_path=[],
                errors=[str(e)],
            )

    def _determine_symbol_type(
        self, symbol_name: str, file_path: str, line_number: int, language: str
    ) -> str:
        """Determine symbol type from context"""
        try:
            # Read file content around the line
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            context_start = max(0, line_number - 5)
            context_end = min(len(lines), line_number + 5)
            context_lines = lines[context_start:context_end]
            context = "".join(context_lines)

            # Check for function call pattern
            if re.search(self.patterns[language]["function_call"], context):
                return "function"

            # Check for method call pattern
            if re.search(self.patterns[language]["method_call"], context):
                return "method"

            # Check for class instantiation
            if re.search(self.patterns[language]["class_instantiation"], context):
                return "class"

            # Check for variable assignment
            if re.search(self.patterns[language]["variable_assignment"], context):
                return "variable"

            # Check for attribute access
            if re.search(self.patterns[language]["attribute_access"], context):
                return "attribute"

            return "unknown"

        except Exception as e:
            logger.warning(f"Failed to determine symbol type: {e}")
            return "unknown"

    def _resolve_local_scope(
        self,
        symbol_name: str,
        file_path: str,
        language: str,
        tenant_id: str,
        repo_id: str,
    ) -> tuple[Optional[SymbolDefinition], float]:
        """Resolve symbol in local file scope"""
        try:
            # Query Neo4j for symbols in the same file
            cypher = """
            MATCH (f:File {tenant_id: $tenant_id, repo_id: $repo_id, path: $file_path})
            MATCH (f)-[:CONTAINS]->(func:Function {name: $symbol_name})
            RETURN func.function_id as symbol_id,
                   func.name as name,
                   func.signature as signature,
                   func.start_line as line_number,
                   func.docstring as docstring
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "repo_id": repo_id,
                        "file_path": file_path,
                        "symbol_name": symbol_name,
                    },
                )

                record = result.single()
                if record:
                    definition = SymbolDefinition(
                        symbol_id=record["symbol_id"],
                        symbol_name=record["name"],
                        symbol_type="function",
                        file_path=file_path,
                        line_number=record["line_number"],
                        signature=record["signature"],
                        docstring=record["docstring"],
                        parameters=[],
                        return_type=None,
                    )
                    return definition, 0.9

            return None, 0.0

        except Exception as e:
            logger.error(f"Local scope resolution failed: {e}")
            return None, 0.0

    def _resolve_import(
        self,
        symbol_name: str,
        file_path: str,
        language: str,
        tenant_id: str,
        repo_id: str,
    ) -> tuple[Optional[SymbolDefinition], float]:
        """Resolve symbol through import statements"""
        try:
            # Get imports for the file
            imports = self._get_file_imports(file_path, language)

            for import_info in imports:
                if import_info["symbol"] == symbol_name:
                    # Try to resolve the imported symbol
                    definition = self._resolve_imported_symbol(
                        import_info["module"], symbol_name, tenant_id, repo_id
                    )
                    if definition:
                        return definition, 0.8

            return None, 0.0

        except Exception as e:
            logger.error(f"Import resolution failed: {e}")
            return None, 0.0

    def _get_file_imports(self, file_path: str, language: str) -> list[dict[str, str]]:
        """Extract import statements from file"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            imports = []

            if language == "python":
                # Python import patterns
                patterns = [
                    r"from\s+(\S+)\s+import\s+(\w+)",
                    r"import\s+(\w+)",
                    r"from\s+(\S+)\s+import\s+\*",
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if len(match) == 2:
                            imports.append({"module": match[0], "symbol": match[1]})
                        else:
                            imports.append({"module": match[0], "symbol": "*"})

            elif language in ["javascript", "typescript"]:
                # JavaScript/TypeScript import patterns
                patterns = [
                    r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
                    r'import\s*\{\s*(\w+)\s*\}\s*from\s+[\'"]([^\'"]+)[\'"]',
                    r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if len(match) == 2:
                            imports.append({"module": match[1], "symbol": match[0]})

            return imports

        except Exception as e:
            logger.error(f"Failed to extract imports: {e}")
            return []

    def _resolve_imported_symbol(
        self, module_name: str, symbol_name: str, tenant_id: str, repo_id: str
    ) -> Optional[SymbolDefinition]:
        """Resolve symbol from imported module"""
        try:
            # Try to find the module file
            module_file = self._find_module_file(module_name, repo_id, tenant_id)
            if not module_file:
                return None

            # Query for the symbol in the module file
            cypher = """
            MATCH (f:File {tenant_id: $tenant_id, repo_id: $repo_id, path: $file_path})
            MATCH (f)-[:CONTAINS]->(func:Function {name: $symbol_name})
            RETURN func.function_id as symbol_id,
                   func.name as name,
                   func.signature as signature,
                   func.start_line as line_number,
                   func.docstring as docstring
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "repo_id": repo_id,
                        "file_path": module_file,
                        "symbol_name": symbol_name,
                    },
                )

                record = result.single()
                if record:
                    return SymbolDefinition(
                        symbol_id=record["symbol_id"],
                        symbol_name=record["name"],
                        symbol_type="function",
                        file_path=module_file,
                        line_number=record["line_number"],
                        signature=record["signature"],
                        docstring=record["docstring"],
                        parameters=[],
                        return_type=None,
                    )

            return None

        except Exception as e:
            logger.error(f"Failed to resolve imported symbol: {e}")
            return None

    def _find_module_file(
        self, module_name: str, repo_id: str, tenant_id: str
    ) -> Optional[str]:
        """Find file path for module"""
        try:
            # Convert module name to file path
            if module_name.endswith(".py"):
                file_path = module_name
            else:
                file_path = module_name.replace(".", "/") + ".py"

            # Query Neo4j for the file
            cypher = """
            MATCH (f:File {tenant_id: $tenant_id, repo_id: $repo_id, path: $file_path})
            RETURN f.path as path
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "repo_id": repo_id,
                        "file_path": file_path,
                    },
                )

                record = result.single()
                if record:
                    return record["path"]

            return None

        except Exception as e:
            logger.error(f"Failed to find module file: {e}")
            return None

    def _resolve_cross_file(
        self,
        symbol_name: str,
        file_path: str,
        language: str,
        tenant_id: str,
        repo_id: str,
    ) -> tuple[Optional[SymbolDefinition], float]:
        """Resolve symbol across files in the repository"""
        try:
            # Query Neo4j for symbols with the same name in other files
            cypher = """
            MATCH (f:File {tenant_id: $tenant_id, repo_id: $repo_id})
            WHERE f.path <> $file_path
            MATCH (f)-[:CONTAINS]->(func:Function {name: $symbol_name})
            RETURN func.function_id as symbol_id,
                   func.name as name,
                   func.signature as signature,
                   func.start_line as line_number,
                   func.docstring as docstring,
                   f.path as file_path
            ORDER BY func.name
            LIMIT 1
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "repo_id": repo_id,
                        "file_path": file_path,
                        "symbol_name": symbol_name,
                    },
                )

                record = result.single()
                if record:
                    definition = SymbolDefinition(
                        symbol_id=record["symbol_id"],
                        symbol_name=record["name"],
                        symbol_type="function",
                        file_path=record["file_path"],
                        line_number=record["line_number"],
                        signature=record["signature"],
                        docstring=record["docstring"],
                        parameters=[],
                        return_type=None,
                    )
                    return definition, 0.6

            return None, 0.0

        except Exception as e:
            logger.error(f"Cross-file resolution failed: {e}")
            return None, 0.0

    def _resolve_call_graph(
        self, symbol_name: str, file_path: str, tenant_id: str, repo_id: str
    ) -> tuple[Optional[SymbolDefinition], float]:
        """Resolve symbol using call graph analysis"""
        try:
            # Find functions that call this symbol
            cypher = """
            MATCH (caller:Function {tenant_id: $tenant_id, repo_id: $repo_id})
            MATCH (caller)-[:CALLS]->(callee:Function {name: $symbol_name})
            RETURN callee.function_id as symbol_id,
                   callee.name as name,
                   callee.signature as signature,
                   callee.start_line as line_number,
                   callee.docstring as docstring,
                   callee.file_path as file_path
            LIMIT 1
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "repo_id": repo_id,
                        "symbol_name": symbol_name,
                    },
                )

                record = result.single()
                if record:
                    definition = SymbolDefinition(
                        symbol_id=record["symbol_id"],
                        symbol_name=record["name"],
                        symbol_type="function",
                        file_path=record["file_path"],
                        line_number=record["line_number"],
                        signature=record["signature"],
                        docstring=record["docstring"],
                        parameters=[],
                        return_type=None,
                    )
                    return definition, 0.7

            return None, 0.0

        except Exception as e:
            logger.error(f"Call graph resolution failed: {e}")
            return None, 0.0

    def _resolve_heuristic(
        self,
        symbol_name: str,
        file_path: str,
        language: str,
        tenant_id: str,
        repo_id: str,
    ) -> tuple[Optional[SymbolDefinition], float]:
        """Resolve symbol using heuristics"""
        try:
            # Heuristic 1: Common naming patterns
            if symbol_name.startswith("get_") or symbol_name.startswith("set_"):
                # Try to find corresponding function
                base_name = symbol_name[4:]  # Remove 'get_' or 'set_'

                cypher = """
                MATCH (f:File {tenant_id: $tenant_id, repo_id: $repo_id})
                MATCH (f)-[:CONTAINS]->(func:Function)
                WHERE func.name CONTAINS $base_name
                RETURN func.function_id as symbol_id,
                       func.name as name,
                       func.signature as signature,
                       func.start_line as line_number,
                       func.docstring as docstring,
                       f.path as file_path
                ORDER BY func.name
                LIMIT 1
                """

                with self.neo4j_service.driver.session() as session:
                    result = session.run(
                        cypher,
                        {
                            "tenant_id": tenant_id,
                            "repo_id": repo_id,
                            "base_name": base_name,
                        },
                    )

                    record = result.single()
                    if record:
                        definition = SymbolDefinition(
                            symbol_id=record["symbol_id"],
                            symbol_name=record["name"],
                            symbol_type="function",
                            file_path=record["file_path"],
                            line_number=record["line_number"],
                            signature=record["signature"],
                            docstring=record["docstring"],
                            parameters=[],
                            return_type=None,
                        )
                        return definition, 0.4

            # Heuristic 2: Similar function names
            cypher = """
            MATCH (f:File {tenant_id: $tenant_id, repo_id: $repo_id})
            MATCH (f)-[:CONTAINS]->(func:Function)
            WHERE func.name CONTAINS $symbol_name OR $symbol_name CONTAINS func.name
            RETURN func.function_id as symbol_id,
                   func.name as name,
                   func.signature as signature,
                   func.start_line as line_number,
                   func.docstring as docstring,
                   f.path as file_path
            ORDER BY func.name
            LIMIT 1
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "repo_id": repo_id,
                        "symbol_name": symbol_name,
                    },
                )

                record = result.single()
                if record:
                    definition = SymbolDefinition(
                        symbol_id=record["symbol_id"],
                        symbol_name=record["name"],
                        symbol_type="function",
                        file_path=record["file_path"],
                        line_number=record["line_number"],
                        signature=record["signature"],
                        docstring=record["docstring"],
                        parameters=[],
                        return_type=None,
                    )
                    return definition, 0.3

            return None, 0.0

        except Exception as e:
            logger.error(f"Heuristic resolution failed: {e}")
            return None, 0.0

    def create_call_edges(
        self, file_path: str, language: str, tenant_id: str, repo_id: str
    ) -> list[dict[str, Any]]:
        """Create call edges for a file"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            calls = []
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                # Find function calls
                if language == "python":
                    # Python function call patterns
                    func_calls = re.findall(r"(\w+)\s*\(", line)
                    for func_name in func_calls:
                        if func_name not in [
                            "if",
                            "for",
                            "while",
                            "def",
                            "class",
                            "import",
                            "from",
                        ]:
                            calls.append(
                                {
                                    "from_function_id": self._get_current_function_id(
                                        file_path, line_num, tenant_id, repo_id
                                    ),
                                    "to_function_id": self._resolve_function_id(
                                        func_name, file_path, tenant_id, repo_id
                                    ),
                                    "kind": "call",
                                    "line": line_num,
                                    "snippet_s3": "",
                                    "confidence": 0.8,
                                }
                            )

                elif language in ["javascript", "typescript"]:
                    # JavaScript function call patterns
                    func_calls = re.findall(r"(\w+)\s*\(", line)
                    for func_name in func_calls:
                        if func_name not in [
                            "if",
                            "for",
                            "while",
                            "function",
                            "class",
                            "import",
                            "export",
                        ]:
                            calls.append(
                                {
                                    "from_function_id": self._get_current_function_id(
                                        file_path, line_num, tenant_id, repo_id
                                    ),
                                    "to_function_id": self._resolve_function_id(
                                        func_name, file_path, tenant_id, repo_id
                                    ),
                                    "kind": "call",
                                    "line": line_num,
                                    "snippet_s3": "",
                                    "confidence": 0.8,
                                }
                            )

            return calls

        except Exception as e:
            logger.error(f"Failed to create call edges: {e}")
            return []

    def _get_current_function_id(
        self, file_path: str, line_number: int, tenant_id: str, repo_id: str
    ) -> str:
        """Get function ID for the current line"""
        try:
            cypher = """
            MATCH (f:File {tenant_id: $tenant_id, repo_id: $repo_id, path: $file_path})
            MATCH (f)-[:CONTAINS]->(func:Function)
            WHERE func.start_line <= $line_number AND func.end_line >= $line_number
            RETURN func.function_id as function_id
            ORDER BY func.start_line DESC
            LIMIT 1
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "repo_id": repo_id,
                        "file_path": file_path,
                        "line_number": line_number,
                    },
                )

                record = result.single()
                if record:
                    return record["function_id"]

            return ""

        except Exception as e:
            logger.error(f"Failed to get current function ID: {e}")
            return ""

    def _resolve_function_id(
        self, function_name: str, file_path: str, tenant_id: str, repo_id: str
    ) -> str:
        """Resolve function name to function ID"""
        try:
            cypher = """
            MATCH (f:File {tenant_id: $tenant_id, repo_id: $repo_id, path: $file_path})
            MATCH (f)-[:CONTAINS]->(func:Function {name: $function_name})
            RETURN func.function_id as function_id
            LIMIT 1
            """

            with self.neo4j_service.driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "tenant_id": tenant_id,
                        "repo_id": repo_id,
                        "file_path": file_path,
                        "function_name": function_name,
                    },
                )

                record = result.single()
                if record:
                    return record["function_id"]

            return ""

        except Exception as e:
            logger.error(f"Failed to resolve function ID: {e}")
            return ""


class SymbolService:
    """High-level symbol service"""

    def __init__(self, neo4j_service):
        self.resolver = SymbolResolver(neo4j_service)
        self.neo4j_service = neo4j_service

    def resolve_file_symbols(
        self, file_path: str, language: str, tenant_id: str, repo_id: str
    ) -> list[ResolutionResult]:
        """Resolve all symbols in a file"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            symbols = self._extract_symbols(content, language)
            results = []

            for symbol in symbols:
                result = self.resolver.resolve_symbol(
                    symbol["name"],
                    file_path,
                    symbol["line"],
                    language,
                    tenant_id,
                    repo_id,
                )
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Failed to resolve file symbols: {e}")
            return []

    def _extract_symbols(self, content: str, language: str) -> list[dict[str, Any]]:
        """Extract symbols from content"""
        symbols = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            if language == "python":
                # Extract function calls
                func_calls = re.findall(r"(\w+)\s*\(", line)
                for func_name in func_calls:
                    if func_name not in [
                        "if",
                        "for",
                        "while",
                        "def",
                        "class",
                        "import",
                        "from",
                    ]:
                        symbols.append(
                            {
                                "name": func_name,
                                "line": line_num,
                                "type": "function_call",
                            }
                        )

            elif language in ["javascript", "typescript"]:
                # Extract function calls
                func_calls = re.findall(r"(\w+)\s*\(", line)
                for func_name in func_calls:
                    if func_name not in [
                        "if",
                        "for",
                        "while",
                        "function",
                        "class",
                        "import",
                        "export",
                    ]:
                        symbols.append(
                            {
                                "name": func_name,
                                "line": line_num,
                                "type": "function_call",
                            }
                        )

        return symbols


if __name__ == "__main__":
    # Test symbol resolver

    neo4j_service = Neo4jService(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password"),
    )

    symbol_service = SymbolService(neo4j_service)

    # Test symbol resolution
    result = symbol_service.resolve_file_symbols(
        "src/main.py", "python", "tenant_123", "repo_123"
    )

    print(f"Resolved {len(result)} symbols")
    for res in result:
        print(f"  - {res.reference.symbol_name}: {res.confidence:.2f}")
        if res.definition:
            print(f"    -> {res.definition.file_path}:{res.definition.line_number}")

    neo4j_service.close()
