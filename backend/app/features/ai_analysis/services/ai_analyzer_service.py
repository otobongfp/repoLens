import logging
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI
from app.core.config import settings
import os

logger = logging.getLogger(__name__)

class AIAnalyzerService:
    """Service for AI-powered code analysis."""
    
    def __init__(self):
        # Simple cache for analysis results
        self._analysis_cache = {}
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not found. AI analysis will be disabled.")
            self.client = None
            self.enabled = False
        else:
            try:
                # Try different initialization methods for compatibility
                try:
                    self.client = OpenAI(api_key=settings.openai_api_key)
                except TypeError as e:
                    if "proxies" in str(e):
                        # Fallback for older versions
                        self.client = OpenAI(api_key=settings.openai_api_key, http_client=None)
                    else:
                        raise e
                self.enabled = settings.ai_analysis_enabled
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
                self.enabled = False
    
    def analyze_codebase(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the entire codebase and provide comprehensive insights."""
        if not self.enabled or not self.client:
            return self._get_disabled_response()
        
        try:
            # Extract key information from graph
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            technology_stack = graph_data.get("technology_stack", {})
            documentation = graph_data.get("documentation", [])
            configurations = graph_data.get("configurations", [])
            summary = graph_data.get("summary", None)
            # Create a simple cache key based on graph structure
            cache_key = f"{len(nodes)}_{len(edges)}_{hash(str(sorted([n.get('id', '') for n in nodes[:10]])))}_{hash(str(technology_stack))}_{hash(str(documentation))}_{hash(str(configurations))}_{hash(str(summary))}"
            # Check cache first
            if cache_key in self._analysis_cache:
                logger.info("Returning cached analysis result")
                return self._analysis_cache[cache_key]
            # Create a single comprehensive analysis prompt
            combined_prompt = self._create_combined_analysis_prompt(
                nodes, edges, technology_stack, documentation, configurations, summary
            )
            logger.info("Starting comprehensive AI analysis...")
            # Single API call for all analyses
            try:
                response = self.client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=[{"role": "user", "content": combined_prompt}],
                    max_tokens=config.AI_MAX_TOKENS,
                    temperature=config.AI_TEMPERATURE
                )
                # Parse the combined response
                analysis_text = response.choices[0].message.content
                results = self._parse_combined_analysis(analysis_text)
            except Exception as e:
                if "rate_limit_exceeded" in str(e) or "Request too large" in str(e):
                    logger.warning("Token limit exceeded, using fallback analysis")
                    # Use a much simpler analysis for large codebases
                    results = self._create_fallback_analysis(nodes, edges)
                else:
                    raise e
            # Calculate overall scores
            scores = self._calculate_scores(results, nodes, edges)
            logger.info("AI analysis completed successfully")
            result = {
                "enabled": True,
                "scores": scores,
                "analysis": results,
                "summary": self._generate_summary(scores, results)
            }
            # Cache the result
            self._analysis_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._get_error_response(str(e))
    
    def clear_cache(self):
        """Clear the analysis cache."""
        self._analysis_cache.clear()
        logger.info("Analysis cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._analysis_cache),
            "cached_keys": list(self._analysis_cache.keys())
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of tokens (1 token ≈ 4 characters for English text)."""
        return len(text) // 4
    
    def _reduce_graph_for_qa(self, graph_data: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Reduce graph data to fit within token limits for Q&A."""
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        # Extract key information from the question to determine what's relevant
        question_lower = question.lower()
        
        # Determine what types of nodes are most relevant
        relevant_types = set()
        if any(word in question_lower for word in ['function', 'method', 'call']):
            relevant_types.add('function')
        if any(word in question_lower for word in ['class', 'object', 'interface']):
            relevant_types.add('class')
        if any(word in question_lower for word in ['import', 'dependency', 'package']):
            relevant_types.add('import')
        if any(word in question_lower for word in ['file', 'module']):
            relevant_types.add('file')
        
        # If no specific types mentioned, include all types but limit counts
        if not relevant_types:
            relevant_types = {'function', 'class', 'import', 'file'}
        
        # Filter nodes by relevance and limit counts
        filtered_nodes = []
        type_counts = {}
        max_nodes_per_type = 10  # Reduced further to accommodate code content
        
        for node in nodes:
            node_type = node.get('type', '')
            if node_type in relevant_types:
                # Limit each type to reasonable counts
                if type_counts.get(node_type, 0) < max_nodes_per_type:
                    # Include code content in the node
                    node_with_content = node.copy()
                    
                    # Add code content if available
                    if node_type in ['function', 'class'] and 'meta' in node and 'code' in node['meta']:
                        # Truncate code if too long
                        code = node['meta']['code']
                        if len(code) > 1000:  #TODO Limit code length
                            code = code[:1000] + "\n// ... (truncated)"
                        node_with_content['code'] = code
                    elif node_type == 'file' and 'meta' in node and 'content' in node['meta']:
                        # For files, include a summary of content
                        content = node['meta']['content']
                        if len(content) > 500: 
                            content = content[:500] + "\n// ... (truncated)"
                        node_with_content['content'] = content
                    
                    filtered_nodes.append(node_with_content)
                    type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        # Filter edges to only include connections between filtered nodes
        filtered_node_ids = {node['id'] for node in filtered_nodes}
        filtered_edges = [
            edge for edge in edges 
            if edge.get('from') in filtered_node_ids and edge.get('to') in filtered_node_ids
        ]
        
        # Limit total edges
        if len(filtered_edges) > 30:  # Reduced from 50
            filtered_edges = filtered_edges[:30]
        
        # Create summary statistics
        original_stats = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'node_types': self._count_node_types(nodes)
        }
        
        reduced_graph = {
            'nodes': filtered_nodes,
            'edges': filtered_edges,
            'summary': {
                'original_stats': original_stats,
                'filtered_stats': {
                    'nodes_included': len(filtered_nodes),
                    'edges_included': len(filtered_edges),
                    'relevance_criteria': list(relevant_types)
                },
                'note': f"Graph reduced for token limits. Showing {len(filtered_nodes)}/{len(nodes)} nodes and {len(filtered_edges)}/{len(edges)} edges."
            }
        }
        
        return reduced_graph
    
    def _extract_code_summary(self, nodes: List[Dict]) -> Dict[str, Any]:
        """Extract a summary of code content for better Q&A."""
        classes = []
        functions = []
        files = []
        
        for node in nodes:
            node_type = node.get('type', '')
            node_label = node.get('label', 'Unknown')
            node_path = node.get('path', 'Unknown')
            
            if node_type in ['class', 'interface', 'type']:
                code = node.get('meta', {}).get('code', '')
                classes.append({
                    'name': node_label,
                    'type': node_type,
                    'file': node_path,
                    'code': code[:500] if code else ''  # First 500 chars
                })
            elif node_type == 'function':
                code = node.get('meta', {}).get('code', '')
                functions.append({
                    'name': node_label,
                    'file': node_path,
                    'code': code[:300] if code else ''  # First 300 chars
                })
            elif node_type == 'file':
                content = node.get('meta', {}).get('content', '')
                files.append({
                    'name': node_label,
                    'path': node_path,
                    'content': content[:400] if content else ''  # First 400 chars
                })
        
        return {
            'classes': classes[:10],  # Limit to 10 classes
            'functions': functions[:15],  # Limit to 15 functions
            'files': files[:5]  # Limit to 5 files
        }
    
    def _create_fallback_analysis(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, str]:
        """Create a fallback analysis when token limits are exceeded."""
        files = [n for n in nodes if n.get("type") == "file"]
        functions = [n for n in nodes if n.get("type") == "function"]
        classes = [n for n in nodes if n.get("type") in ["class", "interface", "type"]]
        imports = [n for n in nodes if n.get("type") == "import"]
        
        node_types = self._count_node_types(nodes)
        
        # Calculate basic metrics
        avg_connections_per_node = len(edges) / len(nodes) if nodes else 0
        function_to_file_ratio = len(functions) / len(files) if files else 0
        
        # Determine complexity based on metrics (more realistic scoring)
        complexity_factor = avg_connections_per_node * 2 + function_to_file_ratio
        complexity_score = max(1, min(10, 10 - complexity_factor))
        
        # More realistic default scores
        security_score = 6  # Most codebases have some security considerations
        maintainability_score = max(1, min(10, 7 - complexity_factor * 0.5))
        architecture_score = max(1, min(10, 6 + (len(classes) * 0.5)))
        quality_score = max(1, min(10, (complexity_score + maintainability_score + architecture_score) / 3))
        
        return {
            "complexity": f"""Complexity Analysis (Fallback - Token Limit Exceeded)
Score: {complexity_score}/10
This codebase has {len(functions)} functions across {len(files)} files, with an average of {avg_connections_per_node:.1f} connections per node.
Complexity assessment based on structural metrics: {'High' if complexity_score > 7 else 'Medium' if complexity_score > 4 else 'Low'} complexity detected.
Recommendation: Consider breaking down large functions and reducing coupling between modules.""",
            
            "security": f"""Security Analysis (Fallback - Token Limit Exceeded)
Score: {security_score}/10
Basic security assessment for {len(imports)} dependencies and {len(functions)} functions.
Recommendation: Review dependencies for known vulnerabilities and ensure proper input validation in functions.""",
            
            "maintainability": f"""Maintainability Analysis (Fallback - Token Limit Exceeded)
Score: {maintainability_score}/10
Codebase structure: {len(files)} files, {len(functions)} functions, {len(classes)} classes.
Maintainability assessment: {'Good' if maintainability_score > 7 else 'Fair' if maintainability_score > 4 else 'Needs Improvement'}.
Recommendation: Focus on code organization and documentation.""",
            
            "architecture": f"""Architecture Analysis (Fallback - Token Limit Exceeded)
Score: {architecture_score}/10
Architecture overview: {len(classes)} classes, {len(functions)} functions, {len(edges)} connections.
Architecture assessment: {'Well-structured' if architecture_score > 7 else 'Moderate' if architecture_score > 4 else 'Needs restructuring'}.
Recommendation: Review design patterns and module coupling.""",
            
            "quality": f"""Code Quality Analysis (Fallback - Token Limit Exceeded)
Score: {quality_score}/10
Overall quality assessment based on structural metrics.
Quality level: {'High' if quality_score > 7 else 'Medium' if quality_score > 4 else 'Low'}.
Recommendation: Implement code quality tools and review best practices."""
        }
    
    def analyze_function(self, function_node: Dict[str, Any], graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a specific function in detail."""
        if not self.enabled or not self.client:
            return self._get_disabled_response()
        
        try:
            # Find function's connections
            function_id = function_node.get("id")
            incoming_edges = [e for e in graph_data.get("edges", []) if e.get("to") == function_id]
            outgoing_edges = [e for e in graph_data.get("edges", []) if e.get("from") == function_id]
            
            prompt = f"""
            Analyze this function in detail:
            
            Function: {function_node.get('label', 'Unknown')}
            Type: {function_node.get('type', 'Unknown')}
            File: {function_node.get('path', 'Unknown')}
            Lines: {function_node.get('meta', {}).get('start_line', '?')}-{function_node.get('meta', {}).get('end_line', '?')}
            
            Incoming connections: {len(incoming_edges)}
            Outgoing connections: {len(outgoing_edges)}
            
            Provide a detailed analysis including:
            1. Function purpose and responsibility
            2. Complexity assessment (1-10 scale)
            3. Potential issues or code smells
            4. Security considerations
            5. Performance implications
            6. Refactoring suggestions
            7. Test coverage recommendations
            
            Format the response as JSON with these fields:
            {{
                "purpose": "description",
                "complexity_score": 1-10,
                "issues": ["list of issues"],
                "security_concerns": ["list of concerns"],
                "performance_notes": ["list of notes"],
                "refactoring_suggestions": ["list of suggestions"],
                "test_recommendations": ["list of recommendations"],
                "overall_assessment": "summary"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.AI_MAX_TOKENS,
                temperature=config.AI_TEMPERATURE
            )
            
            return {
                "enabled": True,
                "function_analysis": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Function analysis failed: {e}")
            return self._get_error_response(str(e))
    
    def answer_question(self, graph_data: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Answer a question about the codebase using AI."""
        if not self.enabled or not self.client:
            return {"answer": "AI analysis is disabled. Please configure OpenAI API key.", "error": "AI analysis is disabled."}
        try:
            # Reduce graph data to fit within token limits
            reduced_graph = self._reduce_graph_for_qa(graph_data, question)
            
            # Extract code summary for better context
            code_summary = self._extract_code_summary(graph_data.get("nodes", []))
            
            prompt = f"""
            You are an expert codebase assistant. Here is a simplified graph representation of a codebase with code content:
            {reduced_graph}
            
            Code Summary:
            Classes: {code_summary['classes']}
            Functions: {code_summary['functions']}
            Files: {code_summary['files']}
            
            Question: {question}
            
            Please answer the question as helpfully as possible, referencing:
            1. The codebase structure and relationships
            2. The actual code content provided in the nodes
            3. Specific classes, functions, and their implementations
            
            For questions about classes, functions, or code details, use the code content provided in the nodes to give specific, accurate answers.
            If the graph doesn't contain enough information to answer the question, say so and suggest what additional information would be needed.
            """
            
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.AI_MAX_TOKENS,
                temperature=config.AI_TEMPERATURE
            )
            return {"answer": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"AI Q&A failed: {e}")
            return {"answer": "", "error": str(e)}
    
    def _create_complexity_analysis_prompt(self, nodes: List[Dict], edges: List[Dict]) -> tuple:
        """Create prompt for complexity analysis."""
        files = [n for n in nodes if n.get("type") == "file"]
        functions = [n for n in nodes if n.get("type") == "function"]
        
        prompt = f"""
        Analyze the complexity of this codebase:
        
        Files: {len(files)}
        Functions: {len(functions)}
        Total connections: {len(edges)}
        
        File structure:
        {[f.get('label', 'Unknown') for f in files[:10]]}
        
        Function distribution:
        {[f.get('label', 'Unknown') for f in functions[:20]]}
        
        Provide a complexity analysis including:
        1. Overall complexity score (1-10)
        2. Most complex areas
        3. Potential refactoring opportunities
        4. Cyclomatic complexity assessment
        5. Cognitive load analysis
        
        Format as JSON:
        {{
            "overall_complexity": 1-10,
            "complexity_factors": ["list"],
            "hotspots": ["list of complex areas"],
            "refactoring_opportunities": ["list"],
            "assessment": "summary"
        }}
        """
        return ("complexity", prompt)
    
    def _create_security_analysis_prompt(self, nodes: List[Dict], edges: List[Dict]) -> tuple:
        """Create prompt for security analysis."""
        imports = [n for n in nodes if n.get("type") == "import"]
        functions = [n for n in nodes if n.get("type") == "function"]
        
        prompt = f"""
        Analyze the security aspects of this codebase:
        
        Functions: {len(functions)}
        Imports: {len(imports)}
        
        Import analysis:
        {[i.get('label', 'Unknown') for i in imports]}
        
        Function analysis:
        {[f.get('label', 'Unknown') for f in functions[:20]]}
        
        Provide a security analysis including:
        1. Security score (1-10)
        2. Potential vulnerabilities
        3. Risky dependencies
        4. Authentication/authorization concerns
        5. Data handling risks
        6. Security recommendations
        
        Format as JSON:
        {{
            "security_score": 1-10,
            "vulnerabilities": ["list"],
            "risky_dependencies": ["list"],
            "auth_concerns": ["list"],
            "data_risks": ["list"],
            "recommendations": ["list"],
            "assessment": "summary"
        }}
        """
        return ("security", prompt)
    
    def _create_maintainability_analysis_prompt(self, nodes: List[Dict], edges: List[Dict]) -> tuple:
        """Create prompt for maintainability analysis."""
        files = [n for n in nodes if n.get("type") == "file"]
        
        prompt = f"""
        Analyze the maintainability of this codebase:
        
        Files: {len(files)}
        Total connections: {len(edges)}
        
        File structure:
        {[f.get('path', 'Unknown') for f in files[:15]]}
        
        Provide a maintainability analysis including:
        1. Maintainability score (1-10)
        2. Code organization quality
        3. Documentation assessment
        4. Testing coverage estimation
        5. Technical debt indicators
        6. Improvement suggestions
        
        Format as JSON:
        {{
            "maintainability_score": 1-10,
            "organization_quality": "assessment",
            "documentation_status": "assessment",
            "testing_coverage": "assessment",
            "technical_debt": ["list"],
            "improvements": ["list"],
            "assessment": "summary"
        }}
        """
        return ("maintainability", prompt)
    
    def _create_architecture_analysis_prompt(self, nodes: List[Dict], edges: List[Dict]) -> tuple:
        """Create prompt for architecture analysis."""
        prompt = f"""
        Analyze the architecture of this codebase:
        
        Total nodes: {len(nodes)}
        Total connections: {len(edges)}
        
        Node types:
        {self._count_node_types(nodes)}
        
        Provide an architecture analysis including:
        1. Architecture quality score (1-10)
        2. Design patterns identified
        3. Coupling and cohesion assessment
        4. Scalability considerations
        5. Modularity analysis
        6. Architectural recommendations
        
        Format as JSON:
        {{
            "architecture_score": 1-10,
            "design_patterns": ["list"],
            "coupling_assessment": "description",
            "cohesion_assessment": "description",
            "scalability": "assessment",
            "modularity": "assessment",
            "recommendations": ["list"],
            "assessment": "summary"
        }}
        """
        return ("architecture", prompt)
    
    def _create_code_quality_analysis_prompt(self, nodes: List[Dict], edges: List[Dict]) -> tuple:
        """Create prompt for code quality analysis."""
        prompt = f"""
        Analyze the overall code quality of this codebase:
        
        Total nodes: {len(nodes)}
        Total connections: {len(edges)}
        
        Provide a comprehensive code quality analysis including:
        1. Overall quality score (1-10)
        2. Code smells and anti-patterns
        3. Best practices adherence
        4. Readability assessment
        5. Performance considerations
        6. Quality improvement suggestions
        
        Format as JSON:
        {{
            "quality_score": 1-10,
            "code_smells": ["list"],
            "anti_patterns": ["list"],
            "best_practices": "assessment",
            "readability": "assessment",
            "performance": "assessment",
            "improvements": ["list"],
            "assessment": "summary"
        }}
        """
        return ("quality", prompt)
    
    def _create_combined_analysis_prompt(self, nodes: List[Dict], edges: List[Dict], technology_stack: Any, documentation: List[Any], configurations: List[Any], summary: Any) -> str:
        """Create a single comprehensive analysis prompt for all categories, using enhanced agent data."""
        files = [n for n in nodes if n.get("type") == "file"]
        functions = [n for n in nodes if n.get("type") == "function"]
        classes = [n for n in nodes if n.get("type") == "class"]
        imports = [n for n in nodes if n.get("type") == "import"]
        node_types = self._count_node_types(nodes)
        file_names = [f.get('label', 'Unknown') for f in files[:5]]
        function_names = [f.get('label', 'Unknown') for f in functions[:10]]
        import_names = [i.get('label', 'Unknown') for i in imports[:5]]
        sample_classes = []
        sample_functions = []
        for node in nodes:
            if node.get('type') in ['class', 'interface', 'type'] and len(sample_classes) < 3:
                class_name = node.get('label', 'Unknown')
                class_type = node.get('type', 'class')
                class_code = node.get('meta', {}).get('code', '')[:300]
                sample_classes.append(f"{class_type} {class_name}: {class_code}")
            elif node.get('type') == 'function' and len(sample_functions) < 3:
                func_name = node.get('label', 'Unknown')
                func_code = node.get('meta', {}).get('code', '')[:300]
                sample_functions.append(f"{func_name}: {func_code}")
        # Enhanced: Add technology stack, documentation, configurations, summary
        tech_stack_str = str(technology_stack) if technology_stack else "None"
        documentation_str = "\n".join([f"- {doc.get('label', '')}: {doc.get('meta', {}).get('summary', '')}" for doc in documentation]) if documentation else "None"
        configurations_str = "\n".join([f"- {cfg.get('label', '')}: {cfg.get('meta', {}).get('summary', '')}" for cfg in configurations]) if configurations else "None"
        summary_str = summary if summary else "None"
        prompt = f"""
You are an expert code analyst. Analyze this codebase comprehensively and provide insights in all key areas.

Codebase Overview:
- Files: {len(files)}
- Functions: {len(functions)}
- Classes/Interfaces/Types: {len(classes)}
- Imports: {len(imports)}
- Total connections: {len(edges)}
- Node types: {node_types}
- Technology Stack: {tech_stack_str}
- Documentation: {documentation_str}
- Configurations: {configurations_str}
- Agent Summary: {summary_str}

Sample files: {file_names}
Sample functions: {function_names}
Sample imports: {import_names}

Sample class/interface/type implementations:
{sample_classes}

Sample function implementations:
{sample_functions}

Please provide a comprehensive analysis covering all these areas in a single JSON response:
{{
    "complexity": {{
        "score": 1-10,
        "analysis": "Detailed complexity assessment including cyclomatic complexity, cognitive load, and refactoring opportunities",
        "hotspots": ["list of complex areas"],
        "recommendations": ["refactoring suggestions"]
    }},
    "security": {{
        "score": 1-10,
        "analysis": "Security assessment including vulnerabilities, dependencies, authentication, and data handling",
        "vulnerabilities": ["potential security issues"],
        "recommendations": ["security improvements"]
    }},
    "maintainability": {{
        "score": 1-10,
        "analysis": "Maintainability assessment including code organization, documentation, testing, and technical debt",
        "strengths": ["maintainability strengths"],
        "improvements": ["maintainability improvements"]
    }},
    "architecture": {{
        "score": 1-10,
        "analysis": "Architecture assessment including design patterns, coupling, cohesion, and scalability",
        "patterns": ["identified design patterns"],
        "recommendations": ["architectural improvements"]
    }},
    "quality": {{
        "score": 1-10,
        "analysis": "Overall code quality including best practices, readability, and performance",
        "strengths": ["quality strengths"],
        "issues": ["quality issues and anti-patterns"]
    }}
}}

IMPORTANT SCORING GUIDELINES:
- 10/10: Exceptional, industry-leading code (rare)
- 8-9/10: Very good, well-structured code
- 6-7/10: Good code with some areas for improvement
- 4-5/10: Average code with notable issues
- 1-3/10: Poor code with significant problems

Be realistic and critical in your assessment. Most codebases score 5-7/10.
Focus on actionable insights and specific recommendations.
"""
        return prompt
    
    def _parse_combined_analysis(self, analysis_text: str) -> Dict[str, str]:
        """Parse the combined analysis response into separate categories."""
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                results = {}
                for category, data in parsed.items():
                    if isinstance(data, dict):
                        # Combine all fields into a single analysis text
                        analysis_parts = []
                        if 'analysis' in data:
                            analysis_parts.append(data['analysis'])
                        if 'score' in data:
                            analysis_parts.append(f"Score: {data['score']}/10")
                        if 'hotspots' in data:
                            analysis_parts.append(f"Hotspots: {', '.join(data['hotspots'])}")
                        if 'vulnerabilities' in data:
                            analysis_parts.append(f"Vulnerabilities: {', '.join(data['vulnerabilities'])}")
                        if 'recommendations' in data:
                            analysis_parts.append(f"Recommendations: {', '.join(data['recommendations'])}")
                        if 'strengths' in data:
                            analysis_parts.append(f"Strengths: {', '.join(data['strengths'])}")
                        if 'improvements' in data:
                            analysis_parts.append(f"Improvements: {', '.join(data['improvements'])}")
                        if 'patterns' in data:
                            analysis_parts.append(f"Design Patterns: {', '.join(data['patterns'])}")
                        if 'issues' in data:
                            analysis_parts.append(f"Issues: {', '.join(data['issues'])}")
                        
                        results[category] = '\n\n'.join(analysis_parts)
                    else:
                        results[category] = str(data)
                return results
            else:
                # Fallback: split the text into sections
                sections = analysis_text.split('\n\n')
                results = {}
                current_category = None
                current_content = []
                
                for section in sections:
                    if any(keyword in section.lower() for keyword in ['complexity', 'security', 'maintainability', 'architecture', 'quality']):
                        if current_category and current_content:
                            results[current_category] = '\n\n'.join(current_content)
                        current_category = section.split()[0].lower()
                        current_content = [section]
                    else:
                        if current_content:
                            current_content.append(section)
                
                if current_category and current_content:
                    results[current_category] = '\n\n'.join(current_content)
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to parse combined analysis: {e}")
            # Fallback: return the raw text split by categories
            return {
                "complexity": "Analysis parsing failed. Raw response: " + analysis_text[:500],
                "security": "Analysis parsing failed. Raw response: " + analysis_text[500:1000] if len(analysis_text) > 500 else "",
                "maintainability": "Analysis parsing failed. Raw response: " + analysis_text[1000:1500] if len(analysis_text) > 1000 else "",
                "architecture": "Analysis parsing failed. Raw response: " + analysis_text[1500:2000] if len(analysis_text) > 1500 else "",
                "quality": "Analysis parsing failed. Raw response: " + analysis_text[2000:2500] if len(analysis_text) > 2000 else ""
            }
    
    def _count_node_types(self, nodes: List[Dict]) -> Dict[str, int]:
        """Count nodes by type."""
        counts = {}
        for node in nodes:
            node_type = node.get("type", "unknown")
            counts[node_type] = counts.get(node_type, 0) + 1
        return counts
    
    def _calculate_scores(self, results: Dict[str, str], nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """Calculate overall scores from analysis results."""
        scores = {
            "complexity": 5,
            "security": 5,
            "maintainability": 5,
            "architecture": 5,
            "quality": 5
        }
        
        # Try to extract scores from AI responses
        for analysis_type, response in results.items():
            try:
                # Look for score patterns in the response
                score_patterns = [
                    r'score["\s]*:["\s]*(\d+)',
                    r'score["\s]*:["\s]*(\d+\.\d+)',
                    r'Score["\s]*:["\s]*(\d+)',
                    r'Score["\s]*:["\s]*(\d+\.\d+)',
                    r'(\d+)/10',
                    r'(\d+\.\d+)/10'
                ]
                
                extracted_score = None
                for pattern in score_patterns:
                    match = re.search(pattern, response, re.IGNORECASE)
                    if match:
                        try:
                            score = float(match.group(1))
                            if 1 <= score <= 10:
                                extracted_score = score
                                break
                        except ValueError:
                            continue
                
                if extracted_score is not None:
                    scores[analysis_type] = extracted_score
                else:
                    # If no score found, calculate based on codebase metrics
                    scores[analysis_type] = self._calculate_metric_score(analysis_type, nodes, edges)
                    
            except Exception as e:
                logger.warning(f"Failed to extract score for {analysis_type}: {e}")
                # Calculate based on codebase metrics as fallback
                scores[analysis_type] = self._calculate_metric_score(analysis_type, nodes, edges)
        
        # Calculate overall score
        scores["overall"] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _calculate_metric_score(self, analysis_type: str, nodes: List[Dict], edges: List[Dict]) -> float:
        """Calculate score based on codebase metrics when AI score extraction fails."""
        files = [n for n in nodes if n.get("type") == "file"]
        functions = [n for n in nodes if n.get("type") == "function"]
        classes = [n for n in nodes if n.get("type") == "class"]
        imports = [n for n in nodes if n.get("type") == "import"]
        
        if analysis_type == "complexity":
            # Higher complexity = lower score
            avg_connections = len(edges) / len(nodes) if nodes else 0
            function_to_file_ratio = len(functions) / len(files) if files else 0
            complexity_factor = avg_connections * 2 + function_to_file_ratio
            return max(1, min(10, 10 - complexity_factor))
            
        elif analysis_type == "security":
            # Basic security score based on imports and function count
            risky_imports = sum(1 for imp in imports if any(keyword in imp.get('label', '').lower() 
                                                          for keyword in ['eval', 'exec', 'sql', 'http', 'fs']))
            security_score = 10 - (risky_imports * 0.5) - (len(functions) * 0.01)
            return max(1, min(10, security_score))
            
        elif analysis_type == "maintainability":
            # Higher maintainability = higher score
            file_count = len(files)
            function_count = len(functions)
            class_count = len(classes)
            
            # Good maintainability indicators
            has_classes = class_count > 0
            reasonable_function_count = 5 <= function_count <= 50
            reasonable_file_count = 3 <= file_count <= 20
            
            score = 5  # Base score
            if has_classes: score += 1
            if reasonable_function_count: score += 2
            if reasonable_file_count: score += 2
            return max(1, min(10, score))
            
        elif analysis_type == "architecture":
            # Architecture score based on structure
            has_classes = len(classes) > 0
            has_functions = len(functions) > 0
            has_imports = len(imports) > 0
            connection_density = len(edges) / len(nodes) if nodes else 0
            
            score = 5  # Base score
            if has_classes: score += 1
            if has_functions: score += 1
            if has_imports: score += 1
            if 0.5 <= connection_density <= 2.0: score += 2  # Good connection density
            return max(1, min(10, score))
            
        elif analysis_type == "quality":
            # Quality score based on overall structure
            total_elements = len(nodes)
            connection_ratio = len(edges) / len(nodes) if nodes else 0
            
            score = 5  # Base score
            if 10 <= total_elements <= 100: score += 2  # Good size
            if 0.5 <= connection_ratio <= 2.0: score += 2  # Good connections
            if len(classes) > 0: score += 1  # Has structure
            return max(1, min(10, score))
            
        else:
            return 5.0  # Default score
    
    def _generate_summary(self, scores: Dict[str, Any], results: Dict[str, str]) -> str:
        """Generate a summary of the analysis."""
        overall_score = scores.get("overall", 5)
        
        if overall_score >= 8:
            status = "Excellent"
        elif overall_score >= 6:
            status = "Good"
        elif overall_score >= 4:
            status = "Fair"
        else:
            status = "Needs Improvement"
        
        return f"Overall Code Quality: {status} ({overall_score:.1f}/10)"
    
    def _get_disabled_response(self) -> Dict[str, Any]:
        """Return response when AI analysis is disabled."""
        return {
            "enabled": False,
            "error": "AI analysis is disabled. Please configure OpenAI API key.",
            "scores": {
                "complexity": 5,
                "security": 5,
                "maintainability": 5,
                "architecture": 5,
                "quality": 5,
                "overall": 5
            },
            "analysis": {},
            "summary": "AI analysis not available"
        }
    
    def _get_error_response(self, error: str) -> Dict[str, Any]:
        """Return response when AI analysis fails."""
        return {
            "enabled": True,
            "error": f"AI analysis failed: {error}",
            "scores": {
                "complexity": 5,
                "security": 5,
                "maintainability": 5,
                "architecture": 5,
                "quality": 5,
                "overall": 5
            },
            "analysis": {},
            "summary": "Analysis failed"
        } 