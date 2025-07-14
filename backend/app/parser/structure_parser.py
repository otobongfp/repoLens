import os
import logging
from collections import Counter
from tree_sitter import Language, Parser
from app.parser.utils import find_files_with_extension
from app.models.response import RepoGraphResponse, Node, Edge, Summary


# Load compiled grammar
LIB_PATH = "build/my-languages.so"

LANGUAGES = {
    ".ts": Language(LIB_PATH, "typescript"),
    ".tsx": Language(LIB_PATH, "tsx"),
}

logger = logging.getLogger(__name__)

def extract_identifier(node, code):
    if node.type in ("identifier", "property_identifier", "name"):
        return code[node.start_byte:node.end_byte].decode()

    if node.type == "member_expression":
        parts = []
        def collect_parts(n):
            if n.type in ("identifier", "property_identifier", "name"):
                parts.append(code[n.start_byte:n.end_byte].decode())
            elif n.type == "member_expression":
                for child in n.children:
                    collect_parts(child)
        collect_parts(node)
        return ".".join(parts) if parts else None
    
    # Handle call expressions
    if node.type == "call_expression":
        fn = node.child_by_field_name("function")
        if fn:
            return extract_identifier(fn, code)
    
    # Handle other exp types
    for child in node.children:
        if child.type in ("identifier", "property_identifier", "name"):
            return code[child.start_byte:child.end_byte].decode()
        elif child.type in ("member_expression", "call_expression"):
            result = extract_identifier(child, code)
            if result:
                return result
    
    return None

def get_node_line_info(node):
    return node.start_point[0] + 1, node.end_point[0] + 1

def find_function_node(called_name, all_nodes):
    """Find a function node by name across all files"""
    for node in all_nodes:
        if node['type'] == 'function' and node['label'] == called_name:
            return node
    
    if '.' in called_name:
        method_name = called_name.split('.')[-1]
        for node in all_nodes:
            if node['type'] == 'function' and node['label'] == method_name:
                return node
    
    return None

def walk_ast(node, code, file_node_id, nodes, edges, file_path, rel_file_path, current_function_id=None, current_class_id=None, import_counter=None):
    if node.type in ["function_declaration", "method_definition"]:
        name = extract_identifier(node, code)
        if name:
            func_id = f"func:{rel_file_path}:{name}"
            start_line, end_line = get_node_line_info(node)
            nodes.append({
                "id": func_id,
                "label": name,
                "type": "function",
                "path": rel_file_path,
                "meta": {
                    "start_line": start_line,
                    "end_line": end_line,
                    "parent_file": rel_file_path
                }
            })
            edges.append({
                "from": file_node_id,
                "to": func_id,
                "type": "contains",
                "meta": {"line": start_line}
            })
            if current_class_id:
                edges.append({
                    "from": current_class_id,
                    "to": func_id,
                    "type": "contains",
                    "meta": {"line": start_line}
                })
            # Set this as the current function for nested calls
            current_function_id = func_id
    elif node.type == "class_declaration":
        name = extract_identifier(node, code)
        if name:
            class_id = f"class:{rel_file_path}:{name}"
            start_line, end_line = get_node_line_info(node)
            nodes.append({
                "id": class_id,
                "label": name,
                "type": "class",
                "path": rel_file_path,
                "meta": {
                    "start_line": start_line,
                    "end_line": end_line,
                    "parent_file": rel_file_path
                }
            })
            edges.append({
                "from": file_node_id,
                "to": class_id,
                "type": "contains",
                "meta": {"line": start_line}
            })
            current_class_id = class_id
    elif node.type == "import_statement":
        for child in node.children:
            if child.type in ("string", "identifier"):
                import_name = code[child.start_byte:child.end_byte].decode().strip('"').strip("'")
                import_id = f"import:{import_name}"
                nodes.append({
                    "id": import_id,
                    "label": import_name,
                    "type": "import",
                    "path": None,
                    "meta": {
                        "imported_module": import_name,
                        "source_file": rel_file_path
                    }
                })
                start_line, _ = get_node_line_info(child)
                edges.append({
                    "from": file_node_id,
                    "to": import_id,
                    "type": "imports",
                    "meta": {"line": start_line}
                })
                if import_counter is not None:
                    import_counter[import_name] += 1
    elif node.type == "call_expression":
        fn = node.child_by_field_name("function")
        called = extract_identifier(fn, code) if fn else extract_identifier(node, code)
        if called and current_function_id:
            start_line, _ = get_node_line_info(node)
            
            # Try to find the called function in the current file first
            called_id = f"func:{rel_file_path}:{called}"
            
            # Check if this function exists in our nodes
            target_node = None
            for n in nodes:
                if n['id'] == called_id:
                    target_node = n
                    break
            
            # If not found in current file, try to find in other files
            if not target_node:
                target_node = find_function_node(called, nodes)
                if target_node:
                    called_id = target_node['id']
            
            # Create the call edge only if the target function exists
            target_exists = any(n['id'] == called_id for n in nodes)
            if target_exists:
                edges.append({
                    "from": current_function_id,
                    "to": called_id,
                    "type": "calls",
                    "meta": {"line": start_line}
                })
            else:
                # For external calls, create a placeholder node if it doesn't exist
                if not any(n['id'] == called_id for n in nodes):
                    nodes.append({
                        "id": called_id,
                        "label": called,
                        "type": "function",
                        "path": "external",
                        "meta": {
                            "start_line": start_line,
                            "end_line": start_line,
                            "parent_file": "external",
                            "external": True
                        }
                    })
                edges.append({
                    "from": current_function_id,
                    "to": called_id,
                    "type": "calls",
                    "meta": {"line": start_line, "external": True}
                })
            
            # Also check for method calls (e.g., this.service.method())
            if '.' in called:
                parts = called.split('.')
                if len(parts) >= 2:
                    method_name = parts[-1]
                    method_id = f"func:{rel_file_path}:{method_name}"
                    
                    # Check if method exists
                    method_node = None
                    for n in nodes:
                        if n['id'] == method_id:
                            method_node = n
                            break
                    
                    if not method_node:
                        method_node = find_function_node(method_name, nodes)
                        if method_node:
                            method_id = method_node['id']
                    
                    # Create additional edge for method call
                    if method_node:
                        edges.append({
                            "from": current_function_id,
                            "to": method_id,
                            "type": "calls",
                            "meta": {"line": start_line, "call_type": "method"}
                        })
                    else:
                        # Create placeholder for external method call
                        if not any(n['id'] == method_id for n in nodes):
                            nodes.append({
                                "id": method_id,
                                "label": method_name,
                                "type": "function",
                                "path": "external",
                                "meta": {
                                    "start_line": start_line,
                                    "end_line": start_line,
                                    "parent_file": "external",
                                    "external": True,
                                    "call_type": "method"
                                }
                            })
                        edges.append({
                            "from": current_function_id,
                            "to": method_id,
                            "type": "calls",
                            "meta": {"line": start_line, "call_type": "method", "external": True}
                        })
    
    for child in node.children:
        walk_ast(child, code, file_node_id, nodes, edges, file_path, rel_file_path, current_function_id, current_class_id, import_counter)

def parse_repo(repo_path: str) -> RepoGraphResponse:
    nodes = []
    edges = []
    import_counter = Counter()
    files = find_files_with_extension(repo_path, list(LANGUAGES.keys()))
    logger.info("Files found: %s", files)
    total_functions = 0
    total_classes = 0
    
    # First pass: collect all nodes
    for file_path in files:
        ext = os.path.splitext(file_path)[-1]
        language = LANGUAGES.get(ext)
        if not language:
            continue
        parser = Parser()
        parser.set_language(language)
        with open(file_path, "rb") as f:
            code = f.read()
        tree = parser.parse(code)
        root_node = tree.root_node
        rel_file_path = os.path.relpath(file_path, repo_path)
        file_node_id = f"file:{rel_file_path}"
        nodes.append({
            "id": file_node_id,
            "label": os.path.basename(file_path),
            "type": "file",
            "path": rel_file_path,
            "meta": {
                "abs_path": file_path,
                "rel_path": rel_file_path
            }
        })
        walk_ast(root_node, code, file_node_id, nodes, edges, file_path, rel_file_path, import_counter=import_counter)
    
    # Deduplicate
    unique_nodes = {n['id']: n for n in nodes}.values()
    unique_edges = {(e['from'], e['to'], e['type']): e for e in edges}.values()
    
    for n in unique_nodes:
        if n['type'] == "function":
            total_functions += 1
        elif n['type'] == "class":
            total_classes += 1
    top_imports = [{"import": name, "count": count} for name, count in import_counter.most_common(5)]
    
    return RepoGraphResponse(
        nodes=[Node(**n) for n in unique_nodes],
        edges=[Edge(**e) for e in unique_edges],
        summary=Summary(
            totalFiles=len(files),
            totalFunctions=total_functions,
            totalClasses=total_classes,
            topImports=top_imports
        )
    )
 