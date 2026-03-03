from crewai import Task, Agent

def create_security_task(agent: Agent, code_context: str) -> Task:
    return Task(
        description=(
            f"Perform a thorough security audit of the following codebase.\n\n"
            f"Focus areas:\n"
            f"1. Hardcoded secrets, API keys, passwords\n"
            f"2. SQL injection, XSS, command injection risks\n"
            f"3. Insecure dependency versions (use the dependency_checker tool)\n"
            f"4. Missing input validation and sanitisation\n"
            f"5. Authentication and authorisation weaknesses\n"
            f"6. Insecure file operations or path traversal risks\n\n"
            f"Codebase:\n{code_context}"
        ),
        expected_output=(
            "Return ONLY a valid JSON object with no additional text, markdown, or explanation. "
            "The JSON must have these exact keys: agent_name (string), summary (string), "
            "score (integer 0-100), and findings (array of objects with keys: file, line, "
            "title, description, severity, recommendation). "
            "severity must be one of: critical, high, medium, low, info."
        ),
        agent=agent,
    )

def create_quality_task(agent: Agent, code_context: str) -> Task:
    return Task(
        description=(
            f"Analyse the code quality and maintainability of the following codebase.\n\n"
            f"Focus areas:\n"
            f"1. DRY violations and code duplication\n"
            f"2. Function/method length and cyclomatic complexity (use ast_analyser tool)\n"
            f"3. Naming conventions and readability\n"
            f"4. Type hints and error handling patterns\n"
            f"5. Single responsibility principle violations\n"
            f"6. Magic numbers and hardcoded values\n\n"
            f"Codebase:\n{code_context}"
        ),
        expected_output=(
            "Return ONLY a valid JSON object with no additional text, markdown, or explanation. "
            "The JSON must have these exact keys: agent_name (string), summary (string), "
            "score (integer 0-100), and findings (array of objects with keys: file, line, "
            "title, description, severity, recommendation). "
            "severity must be one of: critical, high, medium, low, info."
        ),
        agent=agent,
    )

def create_performance_task(agent: Agent, code_context: str) -> Task:
    return Task(
        description=(
            f"Review the following codebase for performance issues.\n\n"
            f"Focus areas:\n"
            f"1. Inefficient algorithms (O(n²) where O(n) is possible.\n\n"
            f"2. Unnecessary loops, redundant iterations\n"
            f"3. Blocking I/O in async contexts\n"
            f"4. Memory-intensive patterns (loading full files/datasets into memory)\n"
            f"5. Missing caching opportunities\n"
            f"6. Database N+1 query patterns\n\n"
            f"Codebase:\n{code_context}"
        ),
        expected_output=(
            "Return ONLY a valid JSON object with no additional text, markdown, or explanation. "
            "The JSON must have these exact keys: agent_name (string), summary (string), "
            "score (integer 0-100), and findings (array of objects with keys: file, line, "
            "title, description, severity, recommendation). "
            "severity must be one of: critical, high, medium, low, info."
        ),
        agent=agent,
    )

def create_documentation_task(agent: Agent, code_context: str) -> Task:
    return Task(
        description=(
            f"Evaluate the documentation quality of the following codebase.\n\n"
            f"Focus areas:\n"
            f"1. Module and function docstrings (use ast_analyzer for coverage stats)\n"
            f"2. README completeness — install, usage, architecture, examples\n"
            f"3. Inline comments where logic is non-obvious\n"
            f"4. Type hints as self-documentation\n"
            f"5. API documentation and usage examples\n"
            f"6. Stale or misleading comments\n\n"
            f"Codebase:\n{code_context}"
        ),
        expected_output=(
            "A JSON object with: agent_name, summary, score (0-100), "
            "and a findings array where each finding has: file, line, title, "
            "description, severity (critical/high/medium/low/info), and recommendation."
        ),
        agent=agent,
    )
