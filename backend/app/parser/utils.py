import os
from typing import List

def find_files_with_extension(root_dir: str, extensions: List[str]) -> List[str]:
    matches = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                matches.append(os.path.join(root, file))
    return matches 