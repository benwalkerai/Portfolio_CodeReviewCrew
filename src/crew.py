import re
import json
import logging
from typing import Callable
from crewai import Crew, Process
from src.agents import (
    create_security_auditor,
    create_quality_analyst,
    create_performance_reviewer,
    create_documentation_reviewer,
)
from src.tasks import (
    create_security_task,
    create_quality_task,
    create_performance_task,
    create_documentation_task,
)
from src.tools.file_reader import FileReaderTool
from src.models import ReviewReport, AgentReport
from src.tools.repo_loader import RepoLoader


logger = logging.getLogger(__name__)


def run_review(repo_path: str, on_status: Callable[[str], None] | None = None) -> ReviewReport:
    loader = RepoLoader()
    try:
        def status(msg: str) -> None:
            logger.info(msg)
            if on_status:
                on_status(msg)

        def step_callback(step_output) -> None:
            agent_name = getattr(step_output, "agent", "Agent")
            status(f"{agent_name} working...")

        def task_callback(task_output) -> None:
            agent_name = task_output.agent if task_output.agent else "Agent"
            status(f"{agent_name} completed")
        status("Loading repository...")
        repo_path = loader.load(repo_path)
        reader = FileReaderTool(repo_path=repo_path)
        files = reader._run()
        if not files:
            raise ValueError(f"No supported code files found in: {repo_path}")

        logger.info(f"Found {len(files)} files to review")

        code_context = _build_context(files)

        security_agent = create_security_auditor(repo_path)
        quality_agent = create_quality_analyst(repo_path)
        performance_agent = create_performance_reviewer(repo_path)
        docs_agent = create_documentation_reviewer(repo_path)

        security_task = create_security_task(security_agent, code_context)
        quality_task = create_quality_task(quality_agent, code_context)
        performance_task = create_performance_task(performance_agent, code_context)
        docs_task = create_documentation_task(docs_agent, code_context)

        crew = Crew(
            agents=[security_agent, quality_agent, performance_agent, docs_agent],
            tasks=[security_task, quality_task, performance_task, docs_task],
            process=Process.sequential,
            memory=True,
            verbose=True,
            step_callback=step_callback,
            task_callback=task_callback,
        )

        logger.info("Starting code review crew...")
        result = crew.kickoff()                                    # FIX 1: missing kickoff call

        return _parse_results(result, repo_path, len(files))
    finally:
        loader.cleanup()



def _build_context(files: dict[str, str], max_chars: int = 80_000) -> str:
    parts: list[str] = []
    total = 0

    for filepath, content in sorted(files.items()):
        header = f"\n--- {filepath} ---\n"
        section = header + content

        if total + len(section) > max_chars:
            parts.append(f"\n--- [TRUNCATED: {len(files) - len(parts)} files omitted] ---")
            break
        parts.append(section)
        total += len(section)
    return "".join(parts)

def _extract_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    match = re.search(r"```(?:json)?\s*(\{.*?})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{.*}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None

def _parse_results(
    crew_result, repo_name: str, files_reviewed: int
) -> ReviewReport:
    task_outputs = crew_result.tasks_output

    agent_reports: list[AgentReport] = []
    for output in task_outputs:
        data = _extract_json(output.raw) if output.raw else None
        if data:
            try:
                agent_reports.append(AgentReport(**data))
            except Exception:
                agent_reports.append(
                    AgentReport(
                        agent_name=data.get("agent_name", output.agent or "Unknown"),
                        summary=data.get("summary", output.raw[:500]),
                        findings=[],
                        score=data.get("score", 0),
                    )
                )
        else:
            agent_reports.append(
                AgentReport(
                    agent_name=output.agent or "Unknown",
                    summary=output.raw[:500] if output.raw else "No output",
                    findings=[],
                    score=0,
                )
            )

    while len(agent_reports) < 4:
        agent_reports.append(
            AgentReport(agent_name="Unknown", summary="No output", findings=[], score=0)
        )

    overall = sum(r.score for r in agent_reports) // 4

    return ReviewReport(
        repo_name=repo_name,
        files_reviewed=files_reviewed,
        security=agent_reports[0],
        quality=agent_reports[1],
        performance=agent_reports[2],
        documentation=agent_reports[3],
        overall_score=overall,
        summary=f"Review Complete. {files_reviewed} files analysed across 4 dimensions.",
    )
