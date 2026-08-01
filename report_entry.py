"""Record today's lab attendance and update the report."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOG_FILE = ROOT / "entry_log.csv"
GRAPH_SCRIPT = ROOT / "plot_graph.py"


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command in the project directory and show its output."""
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
    )


def has_entry_for(date_text: str) -> bool:
    if not LOG_FILE.exists():
        return False

    with LOG_FILE.open(newline="", encoding="utf-8") as log_file:
        return any(row.get("date") == date_text for row in csv.DictReader(log_file))


def append_entry(date_text: str, time_text: str) -> None:
    needs_header = not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0
    with LOG_FILE.open("a", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(log_file)
        if needs_header:
            writer.writerow(["date", "time"])
        writer.writerow([date_text, time_text])


def main(*, dry_run: bool = False) -> int:
    now = datetime.now()
    date_text = now.strftime("%Y-%m-%d")
    time_text = now.strftime("%H:%M:%S")

    if dry_run:
        print(f"Dry run: would record {date_text},{time_text}")
        return 0

    pull_result = run_git("pull", "origin", "main")
    if pull_result.returncode != 0:
        print("Warning: git pull failed; continuing with the local checkout.")

    if has_entry_for(date_text):
        print("Today's attendance has already been recorded.")
        return 0

    append_entry(date_text, time_text)

    # This process is already running inside uv's environment, so invoke the
    # report generator with the same interpreter instead of starting uv again.
    try:
        subprocess.run([sys.executable, str(GRAPH_SCRIPT)], cwd=ROOT, check=True)
    except subprocess.CalledProcessError:
        print("Error: the attendance log was updated, but report generation failed.")
        return 1

    files_to_commit = ["entry_log.csv", "monthly_report.png", "README.md"]
    if run_git("add", *files_to_commit).returncode != 0:
        return 1

    commit_result = run_git("commit", "-m", f"Lab Entry: {date_text}")
    if commit_result.returncode != 0:
        print("Error: failed to commit the attendance update.")
        return 1

    return run_git("push", "origin", "main").returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="check the direct uv entrypoint without changing files or git",
    )
    args = parser.parse_args()
    raise SystemExit(main(dry_run=args.dry_run))
