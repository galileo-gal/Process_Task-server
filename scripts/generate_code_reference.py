# scripts/generate_code_reference.py
"""Auto-generates docs/code_reference.md from src/**/*.py using AST parsing."""

import ast
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Architecture layer order (matches project structure)
LAYER_ORDER = {
    "core": 1,
    "scheduler": 2,
    "dispatch": 3,
    "executors": 4,
    "servers": 5,
    "workloads": 6,
    "utils": 7,
}

def get_git_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        return "unknown"


def infer_description(node) -> str:
    """Try docstring first, then infer from AST body."""
    docstring = ast.get_docstring(node)
    if docstring:
        return docstring.split("\n")[0].strip()

    # Infer from function/method body
    for stmt in ast.walk(node):
        # Check for return statement
        if isinstance(stmt, ast.Return) and stmt.value:
            return f"Returns {ast.unparse(stmt.value)[:60]}"
        # Check for assignments (marks timestamps etc)
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Attribute):
                    return f"Sets self.{target.attr} on the job instance"

    return f"Executes {node.name.replace('_', ' ')} operation"

def format_params(node: ast.FunctionDef) -> str:
    params = []
    args = node.args
    all_args = args.args
    defaults_offset = len(all_args) - len(args.defaults)

    for i, arg in enumerate(all_args):
        if arg.arg == "self":
            continue
        if i >= defaults_offset:
            default = ast.unparse(args.defaults[i - defaults_offset])
            params.append(f"{arg.arg}={default}")
        else:
            params.append(arg.arg)
    return ", ".join(params)

def extract_return_type(node: ast.FunctionDef) -> str:
    if node.returns:
        return ast.unparse(node.returns)
    return "Any"

def parse_file(filepath: Path) -> dict:
    source = filepath.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    file_doc = ast.get_docstring(tree) or ""
    classes = []
    functions = []

    for node in ast.iter_child_nodes(tree):
        # Skip private
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                functions.append({
                    "name": node.name,
                    "params": format_params(node),
                    "returns": extract_return_type(node),
                    "doc": infer_description(node),
                    "is_async": isinstance(node, ast.AsyncFunctionDef)
                })

        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                methods = []
                for item in ast.iter_child_nodes(node):
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not item.name.startswith("_"):
                            methods.append({
                                "name": item.name,
                                "params": format_params(item),
                                "returns": extract_return_type(item),
                                "doc": infer_description(item),
                                "is_async": isinstance(item, ast.AsyncFunctionDef)
                            })
                classes.append({
                    "name": node.name,
                    "doc": infer_description(node),
                    "methods": sorted(methods, key=lambda x: x["name"])
                })

    return {
        "file_doc": file_doc.split("\n")[0].strip() if file_doc else "",
        "classes": sorted(classes, key=lambda x: x["name"]),
        "functions": sorted(functions, key=lambda x: x["name"])
    }

def get_layer(rel_path: str) -> str:
    parts = Path(rel_path).parts
    if len(parts) > 1:
        return parts[1]  # src/<layer>/file.py
    return "other"

def render_markdown(all_files: list, git_hash: str) -> str:
    lines = [
        "<!-- AUTO-GENERATED FILE. DO NOT EDIT MANUALLY -->",
        f"<!-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Commit: {git_hash} -->",
        "",
        "# Code Reference – Process_Task-server",
        "",
        "**Grouped by architecture layer. Regenerate:** `python scripts/generate_code_reference.py`",
        "",
    ]

    # Group by layer
    layers = {}
    for entry in all_files:
        layer = get_layer(entry["rel_path"])
        layers.setdefault(layer, []).append(entry)

    # Sort layers by defined order
    sorted_layers = sorted(
        layers.items(),
        key=lambda x: LAYER_ORDER.get(x[0], 99)
    )

    for layer_name, files in sorted_layers:
        lines.append(f"---")
        lines.append(f"## Layer: `{layer_name}/`")
        lines.append("")

        for entry in sorted(files, key=lambda x: x["rel_path"]):
            rel = entry["rel_path"]
            data = entry["data"]

            lines.append(f"### `{rel}`")
            if data["file_doc"]:
                lines.append(f"> {data['file_doc']}")
            lines.append("")

            for cls in data["classes"]:
                lines.append(f"**Class: `{cls['name']}`** – {cls['doc']}")
                for m in cls["methods"]:
                    async_tag = "async " if m["is_async"] else ""
                    lines.append(f"- `{async_tag}{m['name']}({m['params']})` → `{m['returns']}` – {m['doc']}")
                lines.append("")

            if data["functions"]:
                lines.append("**Functions:**")
                for fn in data["functions"]:
                    async_tag = "async " if fn["is_async"] else ""
                    lines.append(f"- `{async_tag}{fn['name']}({fn['params']})` → `{fn['returns']}` – {fn['doc']}")
                lines.append("")

    return "\n".join(lines)

def main(force: bool = False):
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"
    output_file = repo_root / "docs" / "code_reference.md"

    if not src_dir.exists():
        print("ERROR: src/ not found.")
        sys.exit(1)

    all_files = []
    for py_file in sorted(src_dir.rglob("*.py")):
        # Skip __init__, __pycache__, private
        if "__pycache__" in str(py_file):
            continue
        if py_file.name == "__init__.py":
            continue

        data = parse_file(py_file)
        if data is None:
            continue

        # Skip empty files
        if not data["classes"] and not data["functions"]:
            continue

        rel_path = str(py_file.relative_to(repo_root))
        all_files.append({"rel_path": rel_path, "data": data})

    git_hash = get_git_hash()
    markdown = render_markdown(all_files, git_hash)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown, encoding="utf-8")
    print(f"✅ code_reference.md updated | {len(all_files)} files | commit: {git_hash}")

if __name__ == "__main__":
    force = "--force" in sys.argv
    main(force)