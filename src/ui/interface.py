import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import streamlit as st
import logging
from src.crew import run_review
from src.models import ReviewReport, AgentReport, Severity

logger = logging.getLogger(__name__)

SEVERITY_COLOURS = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
    Severity.INFO: "⚪",
}

def main() -> None:
    st.set_page_config(
        page_title="Code Review Crew",
        page_icon="🔍",
        layout="wide",
    )

    st.title("Code Review Crew")
    st.markdown("Multi-agent AI code review powered by CrewAI")

    with st.sidebar:
        st.header("Configuration")
        repo_input = st.text_input(
            "Repository",
            placeholder="https://github.com/user/repo or /local/path",
            help="Github URL (Public repos) or local file path",
        )
        run_button = st.button("Run Review", type="primary", use_container_width=True)

        st.divider()
        st.markdown("### Agents")
        st.markdown(
            "- Security Auditor\n"
            "- Quality Analyst\n"
            "- Performance Reviewer\n"
            "- Documentation Reviewer"
        )
    if run_button:
        if not repo_input:
            st.error("Please enter a repository path or GitHub URL.")
            return
        is_url = repo_input.startswith(("https://github.com/", "git@github.com:"))
        if not is_url and not Path(repo_input).is_dir():
            st.error(f"Not a valid directory: {repo_input}")
            return

        status_container = st.status("Running code review...", expanded=True)
        log_messages: list[str] = []

        def on_status(msg: str) -> None:
            log_messages.append(msg)
            with status_container:
                st.write(msg)

        try:
            report = run_review(repo_input, on_status=on_status)
            status_container.update(label="✅ Review complete!", state="complete", expanded=False)
        except Exception as e:
            status_container.update(label="❌ Review failed", state="error")
            st.error(f"Error: {e}")
            logger.exception("Review failed")
            return

        _render_report(report)


def _render_report(report: ReviewReport) -> None:
    """Render the full review report."""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Overall", f"{report.overall_score}/100")
    with col2:
        st.metric("Security", f"{report.security.score}/100")
    with col3:
        st.metric("Quality", f"{report.quality.score}/100")
    with col4:
        st.metric("Performance", f"{report.performance.score}/100")
    with col5:
        st.metric("Documentation", f"{report.documentation.score}/100")
    st.divider()
    st.markdown(f"**{report.files_reviewed} files reviewed** across '{report.repo_name}'")

    _render_agent_section("Security Audit", report.security)
    _render_agent_section("Code Quality", report.quality)
    _render_agent_section("Performance", report.performance)
    _render_agent_section("Documentation", report.documentation)

    st.divider()
    st.download_button(
        label="Download Report (JSON)",
        data=report.model_dump_json(indent=2),
        file_name="code_review_report.json",
        mime="application/json",
        use_container_width=True,
    )

def _render_agent_section(title: str, agent_report: AgentReport) -> None:
    """Render a single agent's findings as an expander."""
    finding_count = len(agent_report.findings)
    label = f"{title} - {agent_report.score}/100 ({finding_count} findings)"

    with st.expander(label, expanded=finding_count > 0):
        st.markdown(agent_report.summary)

        if not agent_report.findings:
            st.success("No issues found.")
            return
        
        for finding in agent_report.findings:
            icon = SEVERITY_COLOURS.get(finding.severity, "⚪")
            severity_label = finding.severity.value.upper()

            st.markdown(f"**{icon} [{severity_label}] {finding.title}**")
            st.markdown(f"📁 `{finding.file}`" + (f" (line {finding.line})" if finding.line else ""))
            st.markdown(finding.description)
            st.info(f"💡 **Recommendation:** {finding.recommendation}")
            st.markdown("---")


if __name__ == "__main__":
    main()

