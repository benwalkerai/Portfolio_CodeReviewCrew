# Portfolio_CodeReviewCrew
Multi-agent AI code review system built with CrewAI. Four specialised agents (Security Auditor, Code Quality Analyst, Performance Reviewer, Documentation Reviewer) collaboratively analyse codebases and produce consolidated review reports with actionable findings.

## Architecture Overview
The app takes a GitHub repo URL (or local path), distributes the code across four specialised  CrewAI agents and produces a consolidated review report.

User Input (repo URL/Local Path)
    --> Code Ingestion (parse files)
        --> CrewAI Crew (4 agents, sequential + delegation)
            --> Consolidated Report (Markdown/HTML)

| Agent                  | Role                   | Focus                                                                | Output                                  |
| ---------------------- | ---------------------- | -------------------------------------------------------------------- | --------------------------------------- |
| Security Auditor       | Find vulnerabilities   | Hardcoded secrets, SQL injection, dependency risks, input validation | Security findings with severity ratings |
| Code Quality Analyst   | Assess maintainability | Naming, complexity, DRY violations, type hints, error handling       | Quality score + specific issues         |
| Performance Reviewer   | Spot inefficiencies    | N+1 patterns, memory leaks, blocking calls, unnecessary loops        | Performance recommendations             |
| Documentation Reviewer | Evaluate docs          | Missing docstrings, README accuracy, inline comments, API docs       | Documentation coverage report           |


### Project Structure
Portfolio-CodeReviewCrew/
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── security_auditor.py
│   │   ├── quality_analyst.py
│   │   ├── performance_reviewer.py
│   │   └── documentation_reviewer.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── review_tasks.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── file_reader.py          # Read and parse code files
│   │   ├── ast_analyzer.py         # Python AST complexity analysis
│   │   └── dependency_checker.py   # Check for known vuln packages
│   ├── crew.py                     # Crew assembly and orchestration
│   ├── config.py                   # Settings, env loading
│   └── models.py                   # Pydantic output schemas
├── ui/
│   ├── __init__.py
│   └── interface.py                # Streamlit UI
├── tests/
│   ├── test_agents.py
│   └── test_tools.py
├── .env.example
├── pyproject.toml
├── README.md
└── Dockerfile

## Build Phases
Phase 1: Skeleton
1. Create the repo with pyproject.toml (crewai, streamlit, python-dotenv, pydantic)
2. Setup config.py with _require_env() pattern
3. Define Pydantic output models, SecurityFinding, QualityIssue, PerformanceFlag, DocGap and top-levl ReviewReport
4. Create the four agent definitions in agents/ with role, goal, backstory and allow_delegation=False

Phase 2: Tools & Tasks
1. Build file_reader.py - takes a repo path, returns a dict of {filepath: content} filtered by extension (.py, .js. ts, etc)
2. Build ast_analyser.py, uses Python's ast module to calculate cyclomatic complexity, function length, nesting depth
3. Build dependency_checker.py, reads requriements.txt/pyproject.toml and flags known vulnerable packages
4. Wire up review_tasks.py, one Task per agent, each receiving the parsed code as context, each outputting the corresponding Pydantic model

Phase 3: Crew Orchestration
1. crew.py assembles the crew with Process.sequential, security -> quality -> performance -> docs
2. The Security agent's output feeds in Quality (so it can note this insecure patterns is also a quality issue)
3. A final manager task merges all four outputs into the consolidated ReviewReport

Phase 4: UI
1. Streamlit interface: Text input for repo URL/path "Run review" button
2. Progress display showing which agent is currently active (CrewAI's callback system)
3. Results rendered as expandable sections per agent, colour coded by severity
4. Export to Markdown/HTML/PDF button

Phase 5: Polish
1. ReadMe with architecture diagram, screenshots, usage instructions
2. Docker + Docker Compose
3. .env.example with clear placeholders
4. Testing
