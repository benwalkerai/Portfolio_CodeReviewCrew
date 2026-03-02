import subprocess
import json
from pathlib import Path
from crewai.tools import BaseTool
from pydantic import Field


class DependencyCheckerTool(BaseTool):
    name: str = "dependency_checker"
    description: str = (
        "Audits project dependencies against the OSV vulnerability database "
        "using pip-audit. Returns known CVEs and recommended fixes."
    )
    repo_path: str = Field(description="Path to the repository root")

    def _run(self) -> dict:
        repo = Path(self.repo_path)
        requirements = self._find_dependency_file(repo)

        if not requirements:
            return {
                "status": "warning",
                "message": "No dependency file found (pyproject.toml or requirements.txt)",
                "vulnerabilities": [],
            }

        try:
            result = subprocess.run(
                [
                    "pip-audit",
                    "--requirement", str(requirements),
                    "--format", "json",
                    "--progress-spinner", "off",
                ],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(repo),
            )

            if result.stdout:
                audit_data = json.loads(result.stdout)
                vulns = self._parse_results(audit_data)
            else:
                vulns = []

            return {
                "status": "ok" if not vulns else "vulnerabilities_found",
                "vulnerability_count": len(vulns),
                "vulnerabilities": vulns,
                "source": "OSV (Open Source Vulnerabilities database)",
            }

        except FileNotFoundError:
            return self._fallback_check(repo)
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Audit timed out after 120s"}
        except (json.JSONDecodeError, KeyError) as e:
            return {"status": "error", "message": f"Failed to parse audit results: {e}"}

    def _parse_results(self, audit_data: dict) -> list[dict]:
        vulns = []
        for dep in audit_data.get("dependencies", []):
            for vuln in dep.get("vulns", []):
                vulns.append({
                    "package": dep.get("name"),
                    "installed_version": dep.get("version"),
                    "vulnerability_id": vuln.get("id"),
                    "description": vuln.get("description", "")[:200],
                    "fix_versions": vuln.get("fix_versions", []),
                })
        return vulns

    def _find_dependency_file(self, repo: Path) -> Path | None:
        reqtxt = repo / "requirements.txt"
        if reqtxt.exists():
            return reqtxt

        pyproject = repo / "pyproject.toml"
        if pyproject.exists():
            # Export to temp requirements for pip-audit compatibility
            temp_req = repo / ".audit_requirements.txt"
            try:
                subprocess.run(
                    ["uv", "pip", "compile", str(pyproject), "-o", str(temp_req)],
                    capture_output=True,
                    timeout=60,
                )
                if temp_req.exists():
                    return temp_req
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        return None

    def _fallback_check(self, repo: Path) -> dict:
        return {
            "status": "error",
            "message": (
                "pip-audit not installed. Install with: uv add pip-audit --dev. "
                "Falling back is not available."
            ),
            "vulnerabilities": [],
        }
