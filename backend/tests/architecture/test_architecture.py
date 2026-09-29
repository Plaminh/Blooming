import os
import re
from pathlib import Path
import pytest
import warnings

# Use backend root
BACKEND_ROOT = Path(__file__).parent.parent.parent / "app"
assert BACKEND_ROOT.exists(), f"Backend root not found at {BACKEND_ROOT}"
REPO_ROOT = BACKEND_ROOT.parent.parent

def get_python_files():
    return list(BACKEND_ROOT.rglob("*.py"))

def test_repositories_do_not_import_services():
    for py_file in get_python_files():
        rel_path = py_file.relative_to(BACKEND_ROOT).as_posix()
        if "repositories/" in rel_path or "repository/" in rel_path or rel_path.endswith("_repository.py"):
            content = py_file.read_text(encoding="utf-8")
            assert not re.search(r"^\s*(from|import)\s+app\.services", content, re.MULTILINE), \
                f"Repository {rel_path} imports service module (absolute)."
            assert not re.search(r"^\s*from\s+\.+services\b", content, re.MULTILINE), \
                f"Repository {rel_path} imports service module (relative)."
            assert not re.search(r"^\s*from\s+\.+\s+import\s+(.*?,\s*)?services\b", content, re.MULTILINE), \
                f"Repository {rel_path} imports service module (relative import)."

def test_repositories_do_not_import_routes():
    for py_file in get_python_files():
        rel_path = py_file.relative_to(BACKEND_ROOT).as_posix()
        if "repositories/" in rel_path or "repository/" in rel_path or rel_path.endswith("_repository.py"):
            content = py_file.read_text(encoding="utf-8")
            assert not re.search(r"^\s*(from|import)\s+app\.api\.routes", content, re.MULTILINE), \
                f"Repository {rel_path} imports route module (absolute)."
            assert not re.search(r"^\s*from\s+\.+api\.routes\b", content, re.MULTILINE), \
                f"Repository {rel_path} imports route module (relative)."
            assert not re.search(r"^\s*from\s+\.+api\s+import\s+(.*?,\s*)?routes\b", content, re.MULTILINE), \
                f"Repository {rel_path} imports route module (relative)."

def test_services_do_not_import_api_routes():
    for py_file in get_python_files():
        rel_path = py_file.relative_to(BACKEND_ROOT).as_posix()
        if "services/" in rel_path or "service/" in rel_path or rel_path.endswith("_service.py"):
            content = py_file.read_text(encoding="utf-8")
            assert not re.search(r"^\s*(from|import)\s+app\.api\.routes", content, re.MULTILINE), \
                f"Service {rel_path} imports route module (absolute)."
            assert not re.search(r"^\s*from\s+\.+api\.routes\b", content, re.MULTILINE), \
                f"Service {rel_path} imports route module (relative)."
            assert not re.search(r"^\s*from\s+\.+api\s+import\s+(.*?,\s*)?routes\b", content, re.MULTILINE), \
                f"Service {rel_path} imports route module (relative)."

def test_db_models_do_not_import_services():
    for py_file in get_python_files():
        rel_path = py_file.relative_to(BACKEND_ROOT).as_posix()
        if "models/" in rel_path or "db/models" in rel_path or rel_path.endswith("_model.py"):
            content = py_file.read_text(encoding="utf-8")
            assert not re.search(r"^\s*(from|import)\s+app\.services", content, re.MULTILINE), \
                f"Model {rel_path} imports service module (absolute)."
            assert not re.search(r"^\s*from\s+\.+services\b", content, re.MULTILINE), \
                f"Model {rel_path} imports service module (relative)."
            assert not re.search(r"^\s*from\s+\.+\s+import\s+(.*?,\s*)?services\b", content, re.MULTILINE), \
                f"Model {rel_path} imports service module (relative import)."

def test_route_persistence_guard():
    allowlist = ["api/routes/health.py"]

    for py_file in get_python_files():
        rel_path = py_file.relative_to(BACKEND_ROOT).as_posix()
        if ("api/routes" in rel_path or "api/v1" in rel_path or "/routes/" in rel_path) and rel_path not in allowlist:
            content = py_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            for i, line in enumerate(lines):
                # Ignore comments
                if line.strip().startswith("#"):
                    continue
                match = re.search(r"\b(select\(|db\.execute\(|db\.scalar\(|db\.scalars\(|db\.add\(|db\.delete\()", line)
                assert not match, \
                    f"Route persistence violation in {rel_path}:{i+1}: {match.group(1)}"

def test_repository_transaction_guard():
    allowlist = []

    for py_file in get_python_files():
        rel_path = py_file.relative_to(BACKEND_ROOT).as_posix()
        if ("repositories/" in rel_path or "repository/" in rel_path or rel_path.endswith("_repository.py")) and rel_path not in allowlist:
            content = py_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if line.strip().startswith("#"):
                    continue
                match = re.search(r"\b(commit\(|rollback\()", line)
                assert not match, \
                    f"Repository transaction violation in {rel_path}:{i+1}: {match.group(1)}"

def test_module_size_warning():
    for py_file in get_python_files():
        rel_path = py_file.relative_to(BACKEND_ROOT).as_posix()
        lines = py_file.read_text(encoding="utf-8").splitlines()
        line_count = len(lines)

        if "services/" in rel_path or "service/" in rel_path or rel_path.endswith("_service.py"):
            assert line_count <= 700, f"Oversized service module {rel_path} ({line_count} > 700 lines)"
            if line_count > 400:
                warnings.warn(f"Oversized service module {rel_path}: {line_count} > 400 lines")

        if "api/routes" in rel_path or "api/v1" in rel_path or "/routes/" in rel_path:
            assert line_count <= 450, f"Oversized route module {rel_path} ({line_count} > 450 lines)"
            if line_count > 250:
                warnings.warn(f"Oversized route module {rel_path}: {line_count} > 250 lines")

def test_temporary_artifact_guard():
    exclude_dirs = {
        ".git", "node_modules", ".venv", "target", "build", "dist",
        ".svelte-kit", ".pytest_cache", ".ruff_cache", ".cache", "__pycache__"
    }

    prefixes = ("fix_", "move_", "split_", "cleanup_", "rewrite_", "old_")
    suffixes = (".bak", ".tmp")

    # Check for temporary artifacts in the entire repository, ignoring exclusions
    for root, dirs, files in os.walk(REPO_ROOT):
        # Exclude directories in-place to avoid traversing them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # We want to avoid false positives on legitimate source names.
            # e.g. fix_something.py might be legit? No, the rule explicitly says "Detect fix_*, ...".
            # But "Avoid false positives on legitimate source names."
            # Maybe if it's `old_...` or ends with `.tmp`.
            # Let's strictly check if the file starts with the prefix and it's not a common legitimate file.

            is_temp = False
            for prefix in prefixes:
                if file.startswith(prefix):
                    is_temp = True
                    break

            if not is_temp:
                for suffix in suffixes:
                    if file.endswith(suffix):
                        is_temp = True
                        break

            if is_temp:
                rel_path = Path(os.path.join(root, file)).relative_to(REPO_ROOT).as_posix()
                assert False, f"Temporary artifact found: {rel_path}"

def test_old_ai_import_paths():
    for py_file in get_python_files():
        rel_path = py_file.relative_to(BACKEND_ROOT).as_posix()
        content = py_file.read_text(encoding="utf-8")
        match = re.search(r"app\.ai\.(router|parser|providers|budget|drafts|patches|validators|proactive)", content)
        assert not match, f"Old AI import path {match.group()} found in {rel_path}"
