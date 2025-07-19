import shutil
import logging
from app.shared.services.git_service import GitService
from app.features.code_analysis.parsers.structure_parser import parse_repo

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for code analysis operations."""
    
    def __init__(self):
        self.git_service = GitService()
    
    def analyze_repo(self, url: str) -> dict:
        """
        Analyze a repository by cloning it, parsing the structure, and cleaning up.
        
        Args:
            url: Git repository URL
            
        Returns:
            Repository analysis results
        """
        repo_path = self.git_service.clone_repo(url)
        try:
            logger.info(f"Starting analysis of repository: {url}")
            result = parse_repo(repo_path)
            logger.info(f"Analysis completed for repository: {url}")
            return result
        except Exception as e:
            logger.error(f"Analysis failed for repository {url}: {e}")
            raise
        finally:
            # Clean up the cloned repository
            try:
                shutil.rmtree(repo_path)
                logger.info(f"Cleaned up temporary repository: {repo_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up repository {repo_path}: {e}") 