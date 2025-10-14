# RepoLens Parser Service
# Tree-sitter based code parsing with multi-language support

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import boto3

# Tree-sitter imports
try:
    import tree_sitter
    from tree_sitter import Language, Parser, Node
except ImportError:
    raise ImportError("tree_sitter not installed. Run: pip install tree_sitter")

# Language packages
try:
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript
    import tree_sitter_typescript as tstypescript
except ImportError as e:
    logging.warning(f"Some language packages not available: {e}")

logger = logging.getLogger(__name__)

@dataclass
class CodeSnippet:
    """Code snippet with metadata"""
    snippet_id: str
    file_path: str
    start_line: int
    end_line: int
    content: str
    language: str
    snippet_type: str
    metadata: Dict[str, Any]
    content_hash: str

@dataclass
class Function:
    """Function definition"""
    function_id: str
    name: str
    signature: str
    start_line: int
    end_line: int
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    complexity: int
    snippet: CodeSnippet

@dataclass
class ParsedFile:
    """Parsed file result"""
    file_id: str
    file_path: str
    language: str
    file_hash: str
    status: str
    functions: List[Function]
    classes: List[Dict[str, Any]]
    imports: List[Dict[str, Any]]
    ast_s3_path: str
    errors: List[str]

class TreeSitterParser:
    """Tree-sitter parser for multiple languages"""
    
    def __init__(self, s3_client: Optional[boto3.client] = None):
        self.s3_client = s3_client
        self.languages = {}
        self.parsers = {}
        self._init_languages()
        self._init_parsers()
    
    def _init_languages(self):
        """Initialize language grammars"""
        configs = {
            'python': {
                'module': tspython,
                'extensions': ['.py'],
                'queries': {
                    'functions': '(function_definition name: (identifier) @name)',
                    'classes': '(class_definition name: (identifier) @name)',
                    'imports': '(import_statement) @import'
                }
            },
            'javascript': {
                'module': tsjavascript,
                'extensions': ['.js', '.jsx'],
                'queries': {
                    'functions': '(function_declaration name: (identifier) @name)',
                    'classes': '(class_declaration name: (identifier) @name)',
                    'imports': '(import_statement) @import'
                }
            },
            'typescript': {
                'module': tstypescript,
                'extensions': ['.ts', '.tsx'],
                'queries': {
                    'functions': '(function_declaration name: (identifier) @name)',
                    'classes': '(class_declaration name: (identifier) @name)',
                    'imports': '(import_statement) @import'
                }
            }
        }
        
        for lang_name, config in configs.items():
            try:
                language = Language(config['module'].language())
                self.languages[lang_name] = {
                    'language': language,
                    'extensions': config['extensions'],
                    'queries': config['queries']
                }
                logger.info(f"Initialized {lang_name} parser")
            except Exception as e:
                logger.warning(f"Failed to initialize {lang_name}: {e}")
    
    def _init_parsers(self):
        """Initialize parsers"""
        for lang_name, lang_config in self.languages.items():
            parser = Parser()
            parser.set_language(lang_config['language'])
            self.parsers[lang_name] = parser
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        for lang_name, lang_config in self.languages.items():
            if ext in lang_config['extensions']:
                return lang_name
        
        return None
    
    def parse_file(self, file_path: str, content: str) -> ParsedFile:
        """Parse a file and extract code elements"""
        language = self.detect_language(file_path)
        if not language:
            return self._create_failed_parse(file_path, f"Unsupported language")
        
        try:
            parser = self.parsers[language]
            tree = parser.parse(bytes(content, 'utf8'))
            
            if not tree.root_node:
                return self._create_failed_parse(file_path, "Parse failed")
            
            functions = self._extract_functions(tree.root_node, file_path, content, language)
            classes = self._extract_classes(tree.root_node, file_path, content, language)
            imports = self._extract_imports(tree.root_node, file_path, content, language)
            
            ast_json = self._create_ast_json(tree.root_node, file_path)
            ast_s3_path = self._upload_ast(file_path, ast_json)
            
            file_hash = hashlib.sha256(content.encode('utf8')).hexdigest()
            
            return ParsedFile(
                file_id=self._generate_id(file_path),
                file_path=file_path,
                language=language,
                file_hash=file_hash,
                status="parsed",
                functions=functions,
                classes=classes,
                imports=imports,
                ast_s3_path=ast_s3_path,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return self._create_failed_parse(file_path, str(e))
    
    def _extract_functions(self, root_node: Node, file_path: str, content: str, language: str) -> List[Function]:
        """Extract functions from AST"""
        functions = []
        lines = content.split('\n')
        
        if language == 'python':
            functions = self._extract_python_functions(root_node, file_path, lines)
        elif language in ['javascript', 'typescript']:
            functions = self._extract_js_functions(root_node, file_path, lines)
        
        return functions
    
    def _extract_python_functions(self, root_node: Node, file_path: str, lines: List[str]) -> List[Function]:
        """Extract Python functions"""
        functions = []
        
        def traverse(node: Node):
            if node.type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = name_node.text.decode('utf8')
                    
                    # Extract parameters
                    parameters = []
                    params_node = node.child_by_field_name('parameters')
                    if params_node:
                        for child in params_node.children:
                            if child.type == 'identifier':
                                parameters.append(child.text.decode('utf8'))
                    
                    # Extract docstring
                    docstring = None
                    body = node.child_by_field_name('body')
                    if body and len(body.children) > 0:
                        first_stmt = body.children[0]
                        if first_stmt.type == 'expression_statement':
                            expr = first_stmt.children[0]
                            if expr.type == 'string':
                                docstring = expr.text.decode('utf8').strip('"\'')
                    
                    # Create snippet
                    start_line = node.start_point[0] + 1
                    end_line = node.end_point[0] + 1
                    snippet_content = '\n'.join(lines[start_line-1:end_line])
                    
                    snippet = CodeSnippet(
                        snippet_id=self._generate_id(f"{file_path}:{name}"),
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        content=snippet_content,
                        language='python',
                        snippet_type='function',
                        metadata={'parameters': parameters},
                        content_hash=hashlib.sha256(snippet_content.encode('utf8')).hexdigest()
                    )
                    
                    complexity = self._calculate_complexity(node)
                    
                    function = Function(
                        function_id=self._generate_id(f"{file_path}:{name}"),
                        name=name,
                        signature=f"def {name}({', '.join(parameters)})",
                        start_line=start_line,
                        end_line=end_line,
                        parameters=parameters,
                        return_type=None,
                        docstring=docstring,
                        complexity=complexity,
                        snippet=snippet
                    )
                    
                    functions.append(function)
            
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return functions
    
    def _extract_js_functions(self, root_node: Node, file_path: str, lines: List[str]) -> List[Function]:
        """Extract JavaScript/TypeScript functions"""
        functions = []
        
        def traverse(node: Node):
            if node.type in ['function_declaration', 'method_definition']:
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = name_node.text.decode('utf8')
                    
                    # Extract parameters
                    parameters = []
                    params_node = node.child_by_field_name('parameters')
                    if params_node:
                        for child in params_node.children:
                            if child.type == 'identifier':
                                parameters.append(child.text.decode('utf8'))
                    
                    # Create snippet
                    start_line = node.start_point[0] + 1
                    end_line = node.end_point[0] + 1
                    snippet_content = '\n'.join(lines[start_line-1:end_line])
                    
                    snippet = CodeSnippet(
                        snippet_id=self._generate_id(f"{file_path}:{name}"),
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        content=snippet_content,
                        language='javascript',
                        snippet_type='function',
                        metadata={'parameters': parameters},
                        content_hash=hashlib.sha256(snippet_content.encode('utf8')).hexdigest()
                    )
                    
                    complexity = self._calculate_complexity(node)
                    
                    function = Function(
                        function_id=self._generate_id(f"{file_path}:{name}"),
                        name=name,
                        signature=f"function {name}({', '.join(parameters)})",
                        start_line=start_line,
                        end_line=end_line,
                        parameters=parameters,
                        return_type=None,
                        docstring=None,
                        complexity=complexity,
                        snippet=snippet
                    )
                    
                    functions.append(function)
            
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return functions
    
    def _extract_classes(self, root_node: Node, file_path: str, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        # TODO: Implement class extraction
        return []
    
    def _extract_imports(self, root_node: Node, file_path: str, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract import statements"""
        # TODO: Implement import extraction
        return []
    
    def _calculate_complexity(self, node: Node) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        def traverse(n: Node):
            nonlocal complexity
            if n.type in ['if_statement', 'while_statement', 'for_statement']:
                complexity += 1
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return complexity
    
    def _create_ast_json(self, root_node: Node, file_path: str) -> Dict[str, Any]:
        """Create AST JSON"""
        def node_to_dict(node: Node) -> Dict[str, Any]:
            return {
                'type': node.type,
                'text': node.text.decode('utf8'),
                'start_point': node.start_point,
                'end_point': node.end_point,
                'children': [node_to_dict(child) for child in node.children]
            }
        
        return {
            'file_path': file_path,
            'ast': node_to_dict(root_node),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
    
    def _upload_ast(self, file_path: str, ast_json: Dict[str, Any]) -> str:
        """Upload AST to S3"""
        if not self.s3_client:
            return f"mock_s3_path/{file_path}.ast.json"
        
        try:
            s3_key = f"ast/{file_path}.ast.json"
            self.s3_client.put_object(
                Bucket=os.getenv('S3_BUCKET', 'repolens'),
                Key=s3_key,
                Body=json.dumps(ast_json, indent=2),
                ContentType='application/json'
            )
            return f"s3://{os.getenv('S3_BUCKET', 'repolens')}/{s3_key}"
        except Exception as e:
            logger.error(f"Failed to upload AST: {e}")
            return f"mock_s3_path/{file_path}.ast.json"
    
    def _create_failed_parse(self, file_path: str, error: str) -> ParsedFile:
        """Create failed parse result"""
        return ParsedFile(
            file_id=self._generate_id(file_path),
            file_path=file_path,
            language="unknown",
            file_hash="",
            status="failed",
            functions=[],
            classes=[],
            imports=[],
            ast_s3_path="",
            errors=[error]
        )
    
    def _generate_id(self, text: str) -> str:
        """Generate unique ID"""
        return hashlib.sha256(text.encode('utf8')).hexdigest()[:16]

class ParserService:
    """Parser service with batch processing"""
    
    def __init__(self, s3_client: Optional[boto3.client] = None):
        self.parser = TreeSitterParser(s3_client)
        self.results: Dict[str, ParsedFile] = {}
    
    def parse_repository(self, repo_path: str) -> Dict[str, ParsedFile]:
        """Parse entire repository"""
        repo_path = Path(repo_path)
        parsed_files = {}
        
        # Get supported extensions
        supported_extensions = set()
        for lang_config in self.parser.languages.values():
            supported_extensions.update(lang_config['extensions'])
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    content = file_path.read_text(encoding='utf8', errors='ignore')
                    relative_path = str(file_path.relative_to(repo_path))
                    
                    parsed_file = self.parser.parse_file(relative_path, content)
                    parsed_files[relative_path] = parsed_file
                    
                    logger.info(f"Parsed {relative_path}: {len(parsed_file.functions)} functions")
                    
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                    parsed_files[str(file_path.relative_to(repo_path))] = self.parser._create_failed_parse(
                        str(file_path.relative_to(repo_path)), str(e)
                    )
        
        self.results.update(parsed_files)
        return parsed_files
    
    def get_stats(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        total_files = len(self.results)
        successful = sum(1 for f in self.results.values() if f.status == "parsed")
        failed = total_files - successful
        
        total_functions = sum(len(f.functions) for f in self.results.values())
        
        language_stats = {}
        for parsed_file in self.results.values():
            lang = parsed_file.language
            if lang not in language_stats:
                language_stats[lang] = {'files': 0, 'functions': 0}
            language_stats[lang]['files'] += 1
            language_stats[lang]['functions'] += len(parsed_file.functions)
        
        return {
            'total_files': total_files,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total_files if total_files > 0 else 0,
            'total_functions': total_functions,
            'language_stats': language_stats
        }

if __name__ == "__main__":
    # Test parser
    parser_service = ParserService()
    
    sample_code = '''
def hello_world(name: str) -> str:
    """A simple hello world function"""
    return f"Hello, {name}!"

class Calculator:
    """A simple calculator class"""
    
    def add(self, a: int, b: int) -> int:
        return a + b
'''
    
    parsed_file = parser_service.parser.parse_file("test.py", sample_code)
    print(f"Parsed file: {parsed_file.file_path}")
    print(f"Functions: {len(parsed_file.functions)}")
    
    for func in parsed_file.functions:
        print(f"  Function: {func.name} - {func.signature}")
        print(f"    Complexity: {func.complexity}")
        print(f"    Docstring: {func.docstring}")
