# RepoLens Parser Service
# Tree-sitter based code parsing with multi-language support

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


# Tree-sitter imports
try:
    import tree_sitter
    from tree_sitter import Language, Node, Parser
except ImportError:
    raise ImportError("tree_sitter not installed. Run: pip install tree_sitter")

# Language packages
try:
    import tree_sitter_javascript as tsjavascript
    import tree_sitter_python as tspython
    import tree_sitter_typescript as tstypescript
except ImportError as e:
    logging.warning(f"Some language packages not available: {e}")

logger = logging.getLogger(__name__)


@dataclass
class CodeSnippet:
    file_path: str
    content: str
    language: str
    functions: list[dict[str, Any]]
    classes: list[dict[str, Any]]
    imports: list[str]
    complexity_score: int
    lines_of_code: int
    docstring: Optional[str] = None


class ParserService:
    def __init__(self):
        self.supported_languages = {
            "python": {"extensions": [".py"], "parser": None},
            "javascript": {"extensions": [".js"], "parser": None},
            "typescript": {"extensions": [".ts", ".tsx"], "parser": None},
            "java": {"extensions": [".java"], "parser": None},
            "cpp": {"extensions": [".cpp", ".cc", ".cxx"], "parser": None},
            "c": {"extensions": [".c"], "parser": None},
            "go": {"extensions": [".go"], "parser": None},
            "rust": {"extensions": [".rs"], "parser": None},
            "php": {"extensions": [".php"], "parser": None},
            "ruby": {"extensions": [".rb"], "parser": None},
            "swift": {"extensions": [".swift"], "parser": None},
            "kotlin": {"extensions": [".kt"], "parser": None},
        }
        self._initialize_parsers()

    def _initialize_parsers(self):
        """Initialize tree-sitter parsers for supported languages"""
        try:
            if "tspython" in globals():
                python_language = Language(tspython.language(), "python")
                self.supported_languages["python"]["parser"] = python_language

            if "tsjavascript" in globals():
                js_language = Language(tsjavascript.language(), "javascript")
                self.supported_languages["javascript"]["parser"] = js_language

            if "tstypescript" in globals():
                ts_language = Language(tstypescript.language(), "typescript")
                self.supported_languages["typescript"]["parser"] = ts_language

        except Exception as e:
            logger.warning(f"Failed to initialize some parsers: {e}")

    def get_language_from_extension(self, file_path: str) -> Optional[str]:
        """Get language from file extension"""
        ext = Path(file_path).suffix.lower()
        for lang, config in self.supported_languages.items():
            if ext in config["extensions"]:
                return lang
        return None

    def parse_file(self, file_path: str, content: str) -> CodeSnippet:
        """Parse a single file and extract code structure"""
        language = self.get_language_from_extension(file_path)
        if not language:
            return CodeSnippet(
                file_path=file_path,
                content=content,
                language="unknown",
                functions=[],
                classes=[],
                imports=[],
                complexity_score=0,
                lines_of_code=len(content.splitlines()),
            )

        try:
            if language == "python":
                return self._parse_python(file_path, content)
            elif language in ["javascript", "typescript"]:
                return self._parse_javascript_typescript(file_path, content, language)
            else:
                return self._parse_generic(file_path, content, language)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return CodeSnippet(
                file_path=file_path,
                content=content,
                language=language,
                functions=[],
                classes=[],
                imports=[],
                complexity_score=0,
                lines_of_code=len(content.splitlines()),
            )

    def _parse_python(self, file_path: str, content: str) -> CodeSnippet:
        """Parse Python files using tree-sitter"""
        functions = []
        classes = []
        imports = []

        try:
            language = self.supported_languages["python"]["parser"]
            if not language:
                return self._parse_generic(file_path, content, "python")

            parser = Parser()
            parser.set_language(language)
            tree = parser.parse(bytes(content, "utf8"))

            def traverse_node(node: Node, depth: int = 0):
                if node.type == "function_definition":
                    func_name = None
                    for child in node.children:
                        if child.type == "identifier":
                            func_name = child.text.decode("utf8")
                            break

                    if func_name:
                        functions.append(
                            {
                                "name": func_name,
                                "signature": node.text.decode("utf8")[:100],
                                "complexity": depth + 1,
                                "line_start": node.start_point[0] + 1,
                                "line_end": node.end_point[0] + 1,
                            }
                        )

                elif node.type == "class_definition":
                    class_name = None
                    for child in node.children:
                        if child.type == "identifier":
                            class_name = child.text.decode("utf8")
                            break

                    if class_name:
                        classes.append(
                            {
                                "name": class_name,
                                "line_start": node.start_point[0] + 1,
                                "line_end": node.end_point[0] + 1,
                            }
                        )

                elif (
                    node.type == "import_statement"
                    or node.type == "import_from_statement"
                ):
                    imports.append(node.text.decode("utf8").strip())

                for child in node.children:
                    traverse_node(child, depth + 1)

            traverse_node(tree.root_node)

        except Exception as e:
            logger.error(f"Python parsing failed for {file_path}: {e}")

        return CodeSnippet(
            file_path=file_path,
            content=content,
            language="python",
            functions=functions,
            classes=classes,
            imports=imports,
            complexity_score=len(functions) + len(classes),
            lines_of_code=len(content.splitlines()),
        )

    def _parse_javascript_typescript(
        self, file_path: str, content: str, language: str
    ) -> CodeSnippet:
        """Parse JavaScript/TypeScript files"""
        functions = []
        classes = []
        imports = []

        # Simple regex-based parsing for JS/TS
        import re

        # Find function declarations
        func_pattern = r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))"
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1) or match.group(2)
            if func_name:
                functions.append(
                    {
                        "name": func_name,
                        "signature": match.group(0)[:100],
                        "complexity": 1,
                        "line_start": content[: match.start()].count("\n") + 1,
                        "line_end": content[: match.end()].count("\n") + 1,
                    }
                )

        # Find class declarations
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, content):
            classes.append(
                {
                    "name": match.group(1),
                    "line_start": content[: match.start()].count("\n") + 1,
                    "line_end": content[: match.end()].count("\n") + 1,
                }
            )

        # Find imports
        import_pattern = r"(?:import|require)\s+.*?;"
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(0).strip())

        return CodeSnippet(
            file_path=file_path,
            content=content,
            language=language,
            functions=functions,
            classes=classes,
            imports=imports,
            complexity_score=len(functions) + len(classes),
            lines_of_code=len(content.splitlines()),
        )

    def _parse_generic(
        self, file_path: str, content: str, language: str
    ) -> CodeSnippet:
        """Generic parsing for unsupported languages"""
        functions = []
        classes = []
        imports = []

        lines = content.splitlines()
        for i, line in enumerate(lines):
            line = line.strip()

            # Simple heuristics for different languages
            if language in ["java", "cpp", "c"]:
                if "class " in line and "{" in line:
                    class_name = line.split("class ")[1].split()[0]
                    classes.append(
                        {"name": class_name, "line_start": i + 1, "line_end": i + 1}
                    )
                elif "(" in line and ")" in line and "{" in line:
                    func_name = line.split("(")[0].split()[-1]
                    functions.append(
                        {
                            "name": func_name,
                            "signature": line,
                            "complexity": 1,
                            "line_start": i + 1,
                            "line_end": i + 1,
                        }
                    )

            elif language == "go":
                if "func " in line:
                    func_name = line.split("func ")[1].split("(")[0]
                    functions.append(
                        {
                            "name": func_name,
                            "signature": line,
                            "complexity": 1,
                            "line_start": i + 1,
                            "line_end": i + 1,
                        }
                    )
                elif "type " in line and "struct" in line:
                    class_name = line.split("type ")[1].split()[0]
                    classes.append(
                        {"name": class_name, "line_start": i + 1, "line_end": i + 1}
                    )

        return CodeSnippet(
            file_path=file_path,
            content=content,
            language=language,
            functions=functions,
            classes=classes,
            imports=imports,
            complexity_score=len(functions) + len(classes),
            lines_of_code=len(lines),
        )

    def parse_repository(self, repo_path: str) -> list[CodeSnippet]:
        """Parse entire repository and return list of code snippets"""
        snippets = []
        repo_path = Path(repo_path)

        if not repo_path.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            return snippets

        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                language = self.get_language_from_extension(str(file_path))
                if language:
                    try:
                        with open(file_path, encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                        snippet = self.parse_file(str(file_path), content)
                        snippets.append(snippet)

                    except Exception as e:
                        logger.warning(f"Failed to read {file_path}: {e}")

        return snippets

    def get_supported_extensions(self) -> dict[str, list[str]]:
        """Get all supported file extensions"""
        return {
            lang: config["extensions"]
            for lang, config in self.supported_languages.items()
        }
