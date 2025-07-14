from app.parser.repo_cloner import clone_repo
from app.parser.structure_parser import parse_repo
import shutil

def analyze_repo(url: str):
    repo_path = clone_repo(url)
    try:
        return parse_repo(repo_path)
    finally:
        shutil.rmtree(repo_path)