import pytest
from src.models import Finding, AgentReport, ReviewReport, Severity


def test_finding_creation():
    finding = Finding(
        file="src/config.py",
        line=10,
        title="Hardcoded secret",
        description="API key found in source code",
        severity=Severity.CRITICAL,
        recommendation="Use environment variables",
    )
    assert finding.severity == Severity.CRITICAL
    assert finding.file == "src/config.py"


def test_finding_optional_line():
    finding = Finding(
        file="README.md",
        title="Missing install instructions",
        description="No setup guide",
        severity=Severity.LOW,
        recommendation="Add quick start section",
    )
    assert finding.line is None


def test_agent_report_score_bounds():
    report = AgentReport(
        agent_name="Security Auditor",
        summary="All clear",
        findings=[],
        score=85,
    )
    assert report.score == 85


def test_agent_report_score_too_high():
    with pytest.raises(Exception):
        AgentReport(
            agent_name="Test",
            summary="Test",
            findings=[],
            score=101,
        )


def test_agent_report_score_too_low():
    with pytest.raises(Exception):
        AgentReport(
            agent_name="Test",
            summary="Test",
            findings=[],
            score=-1,
        )


def test_review_report_creation():
    agent = AgentReport(
        agent_name="Test Agent",
        summary="Looks good",
        findings=[],
        score=90,
    )
    report = ReviewReport(
        repo_name="test-repo",
        files_reviewed=10,
        security=agent,
        quality=agent,
        performance=agent,
        documentation=agent,
        overall_score=90,
        summary="Review complete",
    )
    assert report.files_reviewed == 10
    assert report.overall_score == 90


def test_review_report_json_export():
    agent = AgentReport(
        agent_name="Test",
        summary="OK",
        findings=[],
        score=75,
    )
    report = ReviewReport(
        repo_name="test",
        files_reviewed=5,
        security=agent,
        quality=agent,
        performance=agent,
        documentation=agent,
        overall_score=75,
        summary="Done",
    )
    json_str = report.model_dump_json()
    assert "test" in json_str
    assert "75" in json_str


def test_severity_values():
    assert Severity.CRITICAL == "critical"
    assert Severity.HIGH == "high"
    assert Severity.MEDIUM == "medium"
    assert Severity.LOW == "low"
    assert Severity.INFO == "info"
