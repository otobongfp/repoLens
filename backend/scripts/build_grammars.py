from tree_sitter import Language
import os

os.makedirs("build", exist_ok=True)

Language.build_library(
    "build/my-languages.so",
    [
        # "grammars/tree-sitter-python",
        # "grammars/tree-sitter-javascript",
        "grammars/tree-sitter-typescript/typescript",
        "grammars/tree-sitter-typescript/tsx",
    ]
)

print("✅ Built grammars into build/my-languages.so")
