import json
import logging
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


def run_review(repo_path: str) -> ReviewReport:
    loader = RepoLoader()
    try:
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


def _parse_results(
    crew_result, repo_name: str, files_reviewed: int
) -> ReviewReport:
    task_outputs = crew_result.tasks_output                    # FIX 2: tasks_outputs → task_outputs (match usage below)

    agent_reports: list[AgentReport] = []
    for output in task_outputs:                                # FIX 3: was using undefined task_outputs
        try:
            data = json.loads(output.raw)
            agent_reports.append(AgentReport(**data))
        except (json.JSONDecodeError, TypeError):
            agent_reports.append(                              # FIX 4: agents_reports → agent_reports
                AgentReport(
                    agent_name=output.agent or "Unknown",
                    summary=output.raw[:500] if output.raw else "No output",  # FIX 5: outout → output
                    findings=[],                               # FIX 6: missing comma after []
                    score=0,
                )
            )

    # FIX 7: while/overall/return were INSIDE the for loop — dedented
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
