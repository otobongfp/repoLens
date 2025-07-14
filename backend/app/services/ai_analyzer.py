import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from app.core.config import config

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        if not config.OPENAI_API_KEY:
            logger.warning("OpenAI API key not found. AI analysis will be disabled.")
            self.client = None
            self.enabled = False
        else:
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.enabled = config.AI_ANALYSIS_ENABLED
    
    def analyze_codebase(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the entire codebase and provide comprehensive insights."""
        if not self.enabled or not self.client:
            return self._get_disabled_response()
        
        try:
            # Extract key information from graph
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            
            # Prepare analysis prompts
            analysis_prompts = [
                self._create_complexity_analysis_prompt(nodes, edges),
                self._create_security_analysis_prompt(nodes, edges),
                self._create_maintainability_analysis_prompt(nodes, edges),
                self._create_architecture_analysis_prompt(nodes, edges),
                self._create_code_quality_analysis_prompt(nodes, edges)
            ]
            
            # Run all analyses
            results = {}
            for prompt_name, prompt in analysis_prompts:
                try:
                    response = self.client.chat.completions.create(
                        model=config.OPENAI_MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=config.AI_MAX_TOKENS,
                        temperature=config.AI_TEMPERATURE
                    )
                    results[prompt_name] = response.choices[0].message.content
                except Exception as e:
                    logger.error(f"Error in {prompt_name}: {e}")
                    results[prompt_name] = f"Analysis failed: {str(e)}"
            
            # Calculate overall scores
            scores = self._calculate_scores(results, nodes, edges)
            
            return {
                "enabled": True,
                "scores": scores,
                "analysis": results,
                "summary": self._generate_summary(scores, results)
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._get_error_response(str(e))
    
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
                # Simple score extraction (in real implementation, parse JSON properly)
                if "score" in response.lower():
                    lines = response.split('\n')
                    for line in lines:
                        if "score" in line.lower() and ":" in line:
                            score_part = line.split(":")[1].strip()
                            # Extract number from string
                            import re
                            numbers = re.findall(r'\d+', score_part)
                            if numbers:
                                scores[analysis_type] = min(10, max(1, int(numbers[0])))
            except:
                pass
        
        # Calculate overall score
        scores["overall"] = sum(scores.values()) / len(scores)
        
        return scores
    
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