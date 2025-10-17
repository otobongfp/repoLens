# RepoLens Backend - Services
# Repository analysis services
import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import mimetypes
from .models import (
    Node,
    Edge,
    FileInfo,
    FileContent,
    FunctionSummary,
    RepositorySummary,
    RepoGraphResponse,
    EnhancedRepoGraphResponse,
    NodeType,
    EdgeType,
)


class CodeParser:
    """Parse code files and extract functions, classes, imports"""

    def __init__(self):
        self.supported_extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
        }

    def get_language_from_extension(self, file_path: str) -> Optional[str]:
        """Get programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(ext)

    def parse_python_file(self, file_path: str, content: str) -> List[FunctionSummary]:
        """Parse Python file using AST"""
        try:
            tree = ast.parse(content)
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func = FunctionSummary(
                        name=node.name,
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        parameters=[arg.arg for arg in node.args.args],
                        docstring=ast.get_docstring(node),
                    )
                    functions.append(func)

            return functions
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}")
            return []

    def parse_javascript_file(
        self, file_path: str, content: str
    ) -> List[FunctionSummary]:
        """Parse JavaScript/TypeScript file using regex"""
        functions = []

        # Match function declarations
        func_patterns = [
            r"function\s+(\w+)\s*\([^)]*\)\s*{",  # function name() {
            r"(\w+)\s*:\s*function\s*\([^)]*\)\s*{",  # name: function() {
            r"(\w+)\s*=\s*function\s*\([^)]*\)\s*{",  # name = function() {
            r"(\w+)\s*=\s*\([^)]*\)\s*=>\s*{",  # name = () => {
            r"(\w+)\s*\([^)]*\)\s*=>\s*{",  # name() => {
        ]

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern in func_patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    # Find end of function (simplified)
                    end_line = self._find_function_end(lines, i - 1)
                    functions.append(
                        FunctionSummary(
                            name=func_name, start_line=i, end_line=end_line or i
                        )
                    )

        return functions

    def _find_function_end(self, lines: List[str], start_idx: int) -> Optional[int]:
        """Find the end line of a function (simplified)"""
        brace_count = 0
        for i in range(start_idx, len(lines)):
            line = lines[i]
            brace_count += line.count("{") - line.count("}")
            if brace_count == 0 and "{" in line:
                return i + 1
        return None

    def parse_file(self, file_path: str, content: str) -> List[FunctionSummary]:
        """Parse file based on its language"""
        language = self.get_language_from_extension(file_path)

        if language == "python":
            return self.parse_python_file(file_path, content)
        elif language in ["javascript", "typescript"]:
            return self.parse_javascript_file(file_path, content)
        else:
            # For other languages, return empty for now
            return []


class RepositoryAnalyzer:
    """Analyze repository structure and generate graph"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.parser = CodeParser()
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []

    def analyze_repository(self) -> RepoGraphResponse:
        """Analyze entire repository and generate graph"""
        if not self.root_path.exists():
            return RepoGraphResponse(nodes=[], edges=[], summary=None)

        # Get all files
        files = self._get_all_files()

        # Create nodes for files
        for file_info in files:
            self._create_file_node(file_info)

        # Parse files and create function/class nodes
        for file_info in files:
            self._parse_file_and_create_nodes(file_info)

        # Create edges (imports, calls, etc.)
        self._create_edges()

        # Generate summary
        summary = self._generate_summary(files)

        return RepoGraphResponse(nodes=self.nodes, edges=self.edges, summary=summary)

    def _get_all_files(self) -> List[FileInfo]:
        """Get all code files in repository"""
        files = []

        for file_path in self.root_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in self.parser.supported_extensions:
                    try:
                        stat = file_path.stat()
                        files.append(
                            FileInfo(
                                path=str(file_path.relative_to(self.root_path)),
                                size=stat.st_size,
                                language=self.parser.get_language_from_extension(
                                    str(file_path)
                                ),
                            )
                        )
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")

        return files

    def _create_file_node(self, file_info: FileInfo):
        """Create a node for a file"""
        node_id = f"file_{file_info.path.replace('/', '_').replace('.', '_')}"
        node = Node(
            id=node_id,
            label=Path(file_info.path).name,
            type=NodeType.FILE,
            path=file_info.path,
            meta={"size": file_info.size, "language": file_info.language},
        )
        self.nodes.append(node)

    def _parse_file_and_create_nodes(self, file_info: FileInfo):
        """Parse file and create function/class nodes"""
        try:
            file_path = self.root_path / file_info.path
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # Parse functions
            functions = self.parser.parse_file(str(file_path), content)

            for func in functions:
                func_id = f"func_{file_info.path.replace('/', '_')}_{func.name}"
                func_node = Node(
                    id=func_id,
                    label=func.name,
                    type=NodeType.FUNCTION,
                    path=file_info.path,
                    meta={
                        "start_line": func.start_line,
                        "end_line": func.end_line,
                        "parameters": func.parameters,
                        "docstring": func.docstring,
                    },
                )
                self.nodes.append(func_node)

                # Create edge from file to function
                file_id = f"file_{file_info.path.replace('/', '_').replace('.', '_')}"
                edge = Edge(from_node=file_id, to_node=func_id, type=EdgeType.USES)
                self.edges.append(edge)

        except Exception as e:
            print(f"Error parsing file {file_info.path}: {e}")

    def _create_edges(self):
        """Create edges between nodes (imports, calls, etc.)"""
        # This is a simplified version
        # In a real implementation, you'd analyze imports and function calls
        pass

    def _generate_summary(self, files: List[FileInfo]) -> RepositorySummary:
        """Generate repository summary"""
        languages = list(set(f.language for f in files if f.language))
        total_functions = len([n for n in self.nodes if n.type == NodeType.FUNCTION])
        total_classes = len([n for n in self.nodes if n.type == NodeType.CLASS])

        return RepositorySummary(
            total_files=len(files),
            total_functions=total_functions,
            total_classes=total_classes,
            languages=languages,
            main_technologies=languages[:5],  # Top 5 languages
        )

    def get_files(self) -> List[FileInfo]:
        """Get list of all files"""
        return self._get_all_files()

    def get_file_content(self, file_path: str) -> FileContent:
        """Get content of a specific file"""
        try:
            full_path = self.root_path / file_path
            if not full_path.exists():
                return FileContent(path=file_path, content="")

            content = full_path.read_text(encoding="utf-8", errors="ignore")
            language = self.parser.get_language_from_extension(file_path)
            functions = self.parser.parse_file(str(full_path), content)

            return FileContent(
                path=file_path,
                content=content,
                language=language,
                functions=[func.dict() for func in functions],
            )
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return FileContent(path=file_path, content="")

    def search_symbols(self, query: str) -> List[Node]:
        """Search for symbols/functions in the repository"""
        results = []
        query_lower = query.lower()

        for node in self.nodes:
            if query_lower in node.label.lower() or query_lower in node.path.lower():
                results.append(node)

        return results
