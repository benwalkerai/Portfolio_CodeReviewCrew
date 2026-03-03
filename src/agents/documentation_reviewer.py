from crewai import Agent
from src.config import get_llm, VERBOSE
from src.tools.file_reader import FileReaderTool
from src.tools.ast_analyser import ASTAnalyserTool

def create_documentation_reviewer(repo_path: str) -> Agent:
    return Agent(
        role="Documentation Reviewer",
        goal=(
            "Evaluate documentation completeness: docstrings, README accuracy, "
            "inline comments, type hints as documentation, and API usage examples. "
            "Flag gaps that would confuse a new contributor."
        ),
        backstory=(
            "You are a developer experience lead who believes good documentation "
            "is the difference between an adopted project and an abandoned one. "
            "You assess docs from the perspective of someone seeing the codebase "
            "for the first time. You check that README structure matches actual code. "
        ),
        llm=get_llm(),
        tools=[
            FileReaderTool(repo_path=repo_path),
            ASTAnalyserTool(source_code="", filename=""),
        ],
        verbose=VERBOSE,
        allow_delegation=False,
    )