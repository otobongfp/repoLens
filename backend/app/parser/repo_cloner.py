import tempfile
from git import Repo

def clone_repo(url: str) -> str:
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(url, temp_dir)
    return temp_dir
