import tempfile
from git import Repo
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class GitService:
    """Service for Git operations like cloning repositories."""
    
    @staticmethod
    def clone_repo(url: str, branch: Optional[str] = None) -> str:
        """
        Clone a repository to a temporary directory.
        
        Args:
            url: Git repository URL
            branch: Optional branch to checkout
            
        Returns:
            Path to the cloned repository
        """
        temp_dir = tempfile.mkdtemp()
        try:
            repo = Repo.clone_from(url, temp_dir)
            if branch:
                repo.git.checkout(branch)
            logger.info(f"Successfully cloned repository {url} to {temp_dir}")
            return temp_dir
        except Exception as e:
            logger.error(f"Failed to clone repository {url}: {e}")
            raise 