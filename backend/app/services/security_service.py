# RepoLens Security Assessment Service
# CVE scanning and SAST analysis

import os
import logging
import json
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CVEInfo:
    """CVE information"""
    cve_id: str
    summary: str
    severity: str
    cvss: Optional[float]
    references: List[str]

@dataclass
class SecurityFinding:
    """Security finding"""
    finding_id: str
    rule_id: str
    tool: str
    severity: str
    description: str
    file_id: str
    start_line: int
    end_line: int

class CVEScanner:
    """CVE scanner using OSV API"""
    
    def __init__(self):
        self.osv_api_url = "https://api.osv.dev/v1/query"
    
    def scan_dependencies(self, dependencies: List[Dict[str, str]]) -> List[CVEInfo]:
        """Scan dependencies for CVEs"""
        cves = []
        
        for dep in dependencies:
            try:
                # Query OSV API
                query = {
                    "package": {
                        "name": dep['name'],
                        "ecosystem": dep['ecosystem']
                    },
                    "version": dep['version']
                }
                
                response = requests.post(self.osv_api_url, json=query)
                if response.status_code == 200:
                    data = response.json()
                    
                    for vuln in data.get('vulns', []):
                        cve = CVEInfo(
                            cve_id=vuln.get('id', ''),
                            summary=vuln.get('summary', ''),
                            severity=self._extract_severity(vuln),
                            cvss=self._extract_cvss(vuln),
                            references=vuln.get('references', [])
                        )
                        cves.append(cve)
                
            except Exception as e:
                logger.error(f"CVE scan failed for {dep['name']}: {e}")
        
        return cves
    
    def _extract_severity(self, vuln: Dict[str, Any]) -> str:
        """Extract severity from vulnerability"""
        severity = vuln.get('severity', [])
        if severity:
            return severity[0].get('score', 'unknown')
        return 'unknown'
    
    def _extract_cvss(self, vuln: Dict[str, Any]) -> Optional[float]:
        """Extract CVSS score"""
        severity = vuln.get('severity', [])
        if severity:
            return severity[0].get('score', 0.0)
        return None

class SASTScanner:
    """Static Application Security Testing"""
    
    def __init__(self):
        self.tools = {
            'python': ['bandit', 'safety'],
            'javascript': ['eslint', 'npm audit'],
            'typescript': ['eslint', 'npm audit']
        }
    
    def scan_file(self, file_path: str, language: str) -> List[SecurityFinding]:
        """Scan file for security issues"""
        findings = []
        
        if language == 'python':
            findings.extend(self._scan_python_file(file_path))
        elif language in ['javascript', 'typescript']:
            findings.extend(self._scan_js_file(file_path))
        
        return findings
    
    def _scan_python_file(self, file_path: str) -> List[SecurityFinding]:
        """Scan Python file with bandit"""
        findings = []
        
        try:
            # Run bandit
            result = subprocess.run([
                'bandit', '-f', 'json', file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                for issue in data.get('results', []):
                    finding = SecurityFinding(
                        finding_id=str(uuid.uuid4()),
                        rule_id=issue.get('test_id', ''),
                        tool='bandit',
                        severity=issue.get('issue_severity', 'medium'),
                        description=issue.get('issue_text', ''),
                        file_id=issue.get('filename', ''),
                        start_line=issue.get('line_number', 0),
                        end_line=issue.get('line_number', 0)
                    )
                    findings.append(finding)
            
        except Exception as e:
            logger.error(f"Bandit scan failed: {e}")
        
        return findings
    
    def _scan_js_file(self, file_path: str) -> List[SecurityFinding]:
        """Scan JavaScript file with ESLint security rules"""
        findings = []
        
        try:
            # Run ESLint with security rules
            result = subprocess.run([
                'eslint', '--config', 'security.json', file_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                # Parse ESLint output
                lines = result.stdout.split('\n')
                for line in lines:
                    if ':' in line and 'error' in line:
                        parts = line.split(':')
                        if len(parts) >= 4:
                            finding = SecurityFinding(
                                finding_id=str(uuid.uuid4()),
                                rule_id=parts[3].strip(),
                                tool='eslint',
                                severity='medium',
                                description=parts[4].strip() if len(parts) > 4 else '',
                                file_id=parts[0],
                                start_line=int(parts[1]),
                                end_line=int(parts[1])
                            )
                            findings.append(finding)
            
        except Exception as e:
            logger.error(f"ESLint scan failed: {e}")
        
        return findings

class SecurityService:
    """High-level security service"""
    
    def __init__(self, neo4j_service):
        self.neo4j_service = neo4j_service
        self.cve_scanner = CVEScanner()
        self.sast_scanner = SASTScanner()
    
    def assess_repository(self, repo_id: str, tenant_id: str) -> Dict[str, Any]:
        """Perform comprehensive security assessment"""
        # Get repository files
        files = self._get_repository_files(repo_id, tenant_id)
        
        # Scan for CVEs
        dependencies = self._extract_dependencies(files)
        cves = self.cve_scanner.scan_dependencies(dependencies)
        
        # Scan for SAST findings
        findings = []
        for file_info in files:
            file_findings = self.sast_scanner.scan_file(
                file_info['path'], file_info['language']
            )
            findings.extend(file_findings)
        
        # Store results
        self._store_security_results(repo_id, tenant_id, cves, findings)
        
        return {
            'cves_found': len(cves),
            'findings_found': len(findings),
            'high_severity': len([f for f in findings if f.severity == 'high']),
            'last_scanned': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_repository_files(self, repo_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Get repository files from Neo4j"""
        cypher = """
        MATCH (f:File {tenant_id: $tenant_id, repo_id: $repo_id})
        RETURN f.path as path, f.lang as language
        """
        
        try:
            with self.neo4j_service.driver.session() as session:
                result = session.run(cypher, {
                    'tenant_id': tenant_id,
                    'repo_id': repo_id
                })
                
                return [dict(record) for record in result]
                
        except Exception as e:
            logger.error(f"Failed to get repository files: {e}")
            return []
    
    def _extract_dependencies(self, files: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract dependencies from files"""
        dependencies = []
        
        for file_info in files:
            if file_info['language'] == 'python':
                # Look for requirements.txt
                if 'requirements.txt' in file_info['path']:
                    deps = self._parse_requirements_file(file_info['path'])
                    dependencies.extend(deps)
            
            elif file_info['language'] in ['javascript', 'typescript']:
                # Look for package.json
                if 'package.json' in file_info['path']:
                    deps = self._parse_package_json(file_info['path'])
                    dependencies.extend(deps)
        
        return dependencies
    
    def _parse_requirements_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse Python requirements.txt"""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package name and version
                        if '==' in line:
                            name, version = line.split('==', 1)
                            dependencies.append({
                                'name': name.strip(),
                                'version': version.strip(),
                                'ecosystem': 'PyPI'
                            })
        
        except Exception as e:
            logger.error(f"Failed to parse requirements.txt: {e}")
        
        return dependencies
    
    def _parse_package_json(self, file_path: str) -> List[Dict[str, str]]:
        """Parse JavaScript package.json"""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # Extract dependencies
                deps = data.get('dependencies', {})
                for name, version in deps.items():
                    dependencies.append({
                        'name': name,
                        'version': version,
                        'ecosystem': 'npm'
                    })
        
        except Exception as e:
            logger.error(f"Failed to parse package.json: {e}")
        
        return dependencies
    
    def _store_security_results(self, repo_id: str, tenant_id: str, 
                               cves: List[CVEInfo], findings: List[SecurityFinding]):
        """Store security results in Neo4j"""
        # Store CVEs
        for cve in cves:
            cypher = """
            MERGE (c:CVE {cve_id: $cve_id})
            SET c.summary = $summary,
                c.severity = $severity,
                c.cvss = $cvss,
                c.references = $references,
                c.last_scanned = datetime()
            
            MERGE (r:Repo {tenant_id: $tenant_id, repo_id: $repo_id})
            MERGE (r)-[:HAS_VULNERABILITY]->(c)
            """
            
            with self.neo4j_service.driver.session() as session:
                session.run(cypher, {
                    'cve_id': cve.cve_id,
                    'summary': cve.summary,
                    'severity': cve.severity,
                    'cvss': cve.cvss,
                    'references': cve.references,
                    'tenant_id': tenant_id,
                    'repo_id': repo_id
                })
        
        # Store findings
        for finding in findings:
            cypher = """
            CREATE (f:SecurityFinding {
                finding_id: $finding_id,
                rule_id: $rule_id,
                tool: $tool,
                severity: $severity,
                description: $description,
                file_id: $file_id,
                start_line: $start_line,
                end_line: $end_line,
                created_at: datetime()
            })
            
            MERGE (r:Repo {tenant_id: $tenant_id, repo_id: $repo_id})
            MERGE (r)-[:HAS_FINDING]->(f)
            """
            
            with self.neo4j_service.driver.session() as session:
                session.run(cypher, {
                    'finding_id': finding.finding_id,
                    'rule_id': finding.rule_id,
                    'tool': finding.tool,
                    'severity': finding.severity,
                    'description': finding.description,
                    'file_id': finding.file_id,
                    'start_line': finding.start_line,
                    'end_line': finding.end_line,
                    'tenant_id': tenant_id,
                    'repo_id': repo_id
                })

if __name__ == "__main__":
    # Test security service
    from neo4j import GraphDatabase
    
    neo4j_service = Neo4jService(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    security_service = SecurityService(neo4j_service)
    
    # Test security assessment
    result = security_service.assess_repository("repo_123", "tenant_123")
    print(f"Security assessment result: {result}")
    
    neo4j_service.close()
