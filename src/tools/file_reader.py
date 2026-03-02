import os
from crewai.tools import BaseTool
from pydantic import Field

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go",
    ".rs", ".rb", ".php", ".css", ".html", ".yml", ".yaml",
    ".toml", ".json", ".md", ".sh", ".ps1", ".dockerfile",
}

IGNORED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".mypy_cache", ".ruff_cache", "dist", "build",
    ".egg-info", "uv.lock",
}

MAX_FILE_SIZE = 100_000  # 100 KB per file

class FileReaderTool(BaseTool):
    name: str = "file_reader"
    description: str = (
        "Reads all supported code files from a local directory path. "
        "Returns a dictionary of {filepath: content} for analysis."
    )
    repo_path: str = Field(description="Path to the repository directory to read files from.")

    def _run(self) -> dict[str, str]:
        files: dict[str, str] ={}

        for root, dirs, filenames in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    continue

                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, self.repo_path)

                try:
                    if os.path.getsize(filepath) > MAX_FILE_SIZE:
                        files[relative_path] = f"[FILE TOO LARGE - SKIPPED]"
                        continue
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        files[relative_path] = f.read()
                except (OSError, PermissionError):
                    files[relative_path] = "[UNREADABLE]"
        return files