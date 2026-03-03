import argparse
import json
import logging
import sys
from pathlib import Path
from src.crew import run_review

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI-Powered multi-agent code review"
    )
    parser.add_argument(
        "repo_path",
        type=str,
        help="Path to the repository to review",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (JSON). Defaults to stdout.",
    )

    args = parser.parse_args()
    repo = Path(args.repo_path)
    if not repo.is_dir():
        logger.error(f"Not a valid directory: {args.repo_path}")
        sys.exit(1)
    
    logger.info(f"Reviewing repository: {repo.resolve()}")
    report = run_review(str(repo.resolve()))
    output_json = report.model_dump_json(indent=2)

    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        logger.info(f"Report saved to: {args.output}")
    else:
        print(output_json)

if __name__ == "__main__":
    main()