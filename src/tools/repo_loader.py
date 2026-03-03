import shutil
import subprocess
import tempfile
from pathlib import Path

class RepoLoader:
    """Resolves a repo input (local path or GitHub URL) to a local directory path."""
    
    def __init__(self) -> None:
        self._temp_dir: str | None = None
    
    def load(self, repo_input: str) -> str:
        """Return a local directory path for the given input."""
        if self._is_github_url(repo_input):
            return self._clone_repo(repo_input)
        
        path = Path(repo_input)
        if not path.is_dir():
            raise ValueError(f"Not a valid directory: {repo_input}")
        return str(path.resolve())
    
    def cleanup(self) -> None:
        """Remove any temporary directories"""
        if self._temp_dir:
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            self._temp_dir = None

    def _is_github_url(self, value:str) -> bool:
        return value.startswith(("https://github.com/", "git:github.com:"))
    
    def _clone_repo(self, url: str) -> str:
        self._temp_dir = tempfile.mkdtemp(prefix="code_review_")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", url, self._temp_dir],
                capture_output=True,
                text=True,
                timeout=120,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to clone {url}: {e.stderr.strip()}")
        except FileNotFoundError:
            raise EnvironmentError("git is not installed or not on PATH")
        return self._temp_dir