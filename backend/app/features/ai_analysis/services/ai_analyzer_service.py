import logging
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI
from app.core.config import settings
import os

logger = logging.getLogger(__name__)


class AIAnalyzerService:
    def __init__(self):
        self._analysis_cache = {}
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not found. AI analysis will be disabled.")
            self.client = None
            self.enabled = False
        else:
            try:
                self.client = OpenAI(api_key=settings.openai_api_key)
                self.enabled = True
                logger.info("AI Analyzer Service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
                self.enabled = False

    async def analyze_codebase(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled or not self.client:
            return self._get_disabled_response()

        try:
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            technology_stack = graph_data.get("technology_stack", {})
            documentation = graph_data.get("documentation", [])
            configurations = graph_data.get("configurations", [])
            summary = graph_data.get("summary", None)

            cache_key = f"{len(nodes)}_{len(edges)}_{hash(str(sorted([n.get('id', '') for n in nodes[:10]])))}"

            if cache_key in self._analysis_cache:
                logger.info("Returning cached analysis result")
                return self._analysis_cache[cache_key]

            combined_prompt = self._create_combined_analysis_prompt(
                nodes, edges, technology_stack, documentation, configurations, summary
            )

            logger.info("Starting comprehensive AI analysis...")

            try:
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[{"role": "user", "content": combined_prompt}],
                    max_tokens=settings.ai_max_tokens,
                    temperature=settings.ai_temperature,
                )

                analysis_text = response.choices[0].message.content
                results = self._parse_combined_analysis(analysis_text)

            except Exception as e:
                if "rate_limit_exceeded" in str(e) or "Request too large" in str(e):
                    logger.warning("Token limit exceeded, using fallback analysis")
                    results = self._create_fallback_analysis(nodes, edges)
                else:
                    raise e

            self._analysis_cache[cache_key] = results
            logger.info("AI analysis completed successfully")
            return results

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "complexity_score": 0,
                "security_score": 0,
                "architecture_score": 0,
                "quality_score": 0,
                "recommendations": [],
            }

    async def analyze_function(
        self, function_node: Dict[str, Any], graph_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.enabled or not self.client:
            return self._get_disabled_response()

        try:
            function_prompt = self._create_function_analysis_prompt(
                function_node, graph_data
            )

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": function_prompt}],
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
            )

            analysis_text = response.choices[0].message.content
            results = self._parse_function_analysis(analysis_text)

            logger.info(
                f"Function analysis completed for: {function_node.get('label', 'Unknown')}"
            )
            return results

        except Exception as e:
            logger.error(f"Function analysis failed: {e}")
            return {
                "error": f"Function analysis failed: {str(e)}",
                "complexity_score": 0,
                "readability_score": 0,
                "performance_score": 0,
                "recommendations": [],
            }

    async def answer_question(
        self, graph_data: Dict[str, Any], question: str
    ) -> Dict[str, Any]:
        if not self.enabled or not self.client:
            return {"error": "AI service is disabled"}

        try:
            question_prompt = self._create_question_prompt(graph_data, question)

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": question_prompt}],
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
            )

            answer = response.choices[0].message.content
            return {"answer": answer, "question": question}

        except Exception as e:
            logger.error(f"Question answering failed: {e}")
            return {"error": f"Failed to answer question: {str(e)}"}

    async def get_status(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "openai_configured": bool(settings.openai_api_key),
            "model": settings.openai_model,
            "max_tokens": settings.ai_max_tokens,
            "temperature": settings.ai_temperature,
        }

    async def get_cache_stats(self) -> Dict[str, Any]:
        return {
            "cache_size": len(self._analysis_cache),
            "cache_keys": list(self._analysis_cache.keys())[:10],
        }

    async def clear_cache(self):
        self._analysis_cache.clear()
        logger.info("AI analysis cache cleared")

    def _get_disabled_response(self) -> Dict[str, Any]:
        return {
            "error": "AI analysis is disabled. Please configure OpenAI API key.",
            "complexity_score": 0,
            "security_score": 0,
            "architecture_score": 0,
            "quality_score": 0,
            "recommendations": [],
        }

    def _create_combined_analysis_prompt(
        self, nodes, edges, technology_stack, documentation, configurations, summary
    ):
        prompt = f"""
Analyze this codebase and provide comprehensive analysis:

Technology Stack: {technology_stack}
Documentation: {len(documentation)} files
Configurations: {len(configurations)} files
Summary: {summary}

Nodes ({len(nodes)}): {[n.get('label', '') for n in nodes[:20]]}
Edges ({len(edges)}): {[e.get('type', '') for e in edges[:20]]}

Provide analysis in this JSON format:
{{
    "complexity_score": 0-100,
    "security_score": 0-100,
    "architecture_score": 0-100,
    "quality_score": 0-100,
    "recommendations": ["list of recommendations"],
    "insights": "overall insights about the codebase"
}}
"""
        return prompt

    def _create_function_analysis_prompt(self, function_node, graph_data):
        prompt = f"""
Analyze this function:

Function: {function_node.get('label', 'Unknown')}
Type: {function_node.get('type', 'Unknown')}
File: {function_node.get('file', 'Unknown')}

Provide analysis in this JSON format:
{{
    "complexity_score": 0-100,
    "readability_score": 0-100,
    "performance_score": 0-100,
    "recommendations": ["list of recommendations"],
    "insights": "function-specific insights"
}}
"""
        return prompt

    def _create_question_prompt(self, graph_data, question):
        nodes_summary = [n.get("label", "") for n in graph_data.get("nodes", [])[:10]]
        prompt = f"""
Based on this codebase structure: {nodes_summary}

Question: {question}

Provide a helpful answer about the codebase.
"""
        return prompt

    def _parse_combined_analysis(self, analysis_text: str) -> Dict[str, Any]:
        try:
            import json

            json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {
            "complexity_score": 50,
            "security_score": 50,
            "architecture_score": 50,
            "quality_score": 50,
            "recommendations": [
                "Analysis completed but could not parse detailed results"
            ],
            "insights": analysis_text[:500],
        }

    def _parse_function_analysis(self, analysis_text: str) -> Dict[str, Any]:
        try:
            import json

            json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {
            "complexity_score": 50,
            "readability_score": 50,
            "performance_score": 50,
            "recommendations": [
                "Analysis completed but could not parse detailed results"
            ],
            "insights": analysis_text[:500],
        }

    def _create_fallback_analysis(self, nodes, edges):
        return {
            "complexity_score": min(100, len(nodes) * 2),
            "security_score": 60,
            "architecture_score": 70,
            "quality_score": 65,
            "recommendations": [
                "Consider breaking down large functions",
                "Add more documentation",
                "Implement error handling",
            ],
            "insights": f"Codebase has {len(nodes)} nodes and {len(edges)} relationships",
        }
