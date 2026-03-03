from crewai import Agent
from src.config import get_llm, VERBOSE
from src.tools.file_reader import FileReaderTool
from src.tools.ast_analyser import ASTAnalyserTool

def create_quality_analyst(repo_path: str) -> Agent:
    return Agent(
        role="Code Quality Analyst",
        goal=(
            "Assess code maintainability, readability, and adherence to best practises. "
            "Identify DRY violations, excessive complexity, poor naming, missing type hints, "
            "and inadequate error handling."
        ),
        backstory=(
            "You are a principal software engineer who has mentored hundreds of developers. "
            "You champion clean code principles and pragmatic refactoring. You use concrete "
            "metrics like cyclomatic complexity and function length to backup every finding, "
            "not just opinions. You balance perfectionism with practicality. "
        ),
        llm=get_llm(),
        tools=[
            FileReaderTool(repo_path=repo_path),
            ASTAnalyserTool(source_code="", filename=""),
        ],
        verbose=VERBOSE,
        allow_delegation=False,
    )