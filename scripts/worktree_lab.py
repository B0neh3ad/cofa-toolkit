"""Create a fresh local demo repo; run two isolated workers and integrate their commits.

This exercises Git mechanics with deterministic fixture edits, not AI subagents.
It never opens an existing repository, creates a remote, or deletes the demo.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from run_checks import run
from scan_secrets import redact


def git(folder, *args):
    command = [
        "git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
        "-c", "user.name=Toolkit Lab", "-c", "user.email=toolkit@example.invalid",
        "-C", str(folder), *args,
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError(redact(result.stderr.strip() or result.stdout.strip()))
    return result.stdout.strip()


def prepare(parent=None):
    root = Path(tempfile.mkdtemp(prefix="cofa-worktree-lab-", dir=parent)).resolve()
    files = {
        ".gitignore": ".parallel/\n.evidence/\n__pycache__/\nlab-summary.json\n",
        "AGENTS.md": (
            "# Demo working agreements\n"
            "Read CONTRACT.md. Change only the assigned file. Run the assigned check.\n"
            "The coordinator alone integrates commits into the main checkout.\n"
        ),
        "CONTRACT.md": (
            "# Contract v1\n"
            "calculate.total(values) sums a list of integers; empty list returns 0.\n"
            "view.render(value) returns 'Total: ' followed by the integer value.\n"
            "Worker A owns calculate.py. Worker B owns view.py.\n"
            "The coordinator owns the contract, tests, application and main checkout.\n"
        ),
        "calculate.py": "def total(values):\n    raise NotImplementedError\n",
        "view.py": "def render(value):\n    raise NotImplementedError\n",
        "app.py": (
            "import json\nfrom calculate import total\nfrom view import render\n"
            'if __name__ == "__main__":\n'
            '    print(json.dumps({"display": render(total([3, 7]))}))\n'
        ),
        "test_app.py": (
            "import unittest\nfrom calculate import total\nfrom view import render\n"
            "class AppTests(unittest.TestCase):\n"
            "    def test_total(self):\n"
            "        self.assertEqual(total([]), 0)\n"
            "        self.assertEqual(total([3, 7]), 10)\n"
            "    def test_view(self):\n"
            '        self.assertEqual(render(10), "Total: 10")\n'
        ),
        "expected.json": '{"display": "Total: 10"}\n',
    }
    for name, value in files.items():
        (root / name).write_text(value, encoding="utf-8")
    config = {
        "schema_version": 1,
        "source_paths": ["calculate.py", "view.py", "app.py"],
        "fixed_paths": ["test_app.py", "CONTRACT.md", "AGENTS.md", "expected.json"],
        "checks": [
            {"id": "acceptance", "kind": "unit",
             "argv": ["{python}", "-m", "unittest", "-v"], "timeout_seconds": 10},
            {"id": "sample-cli", "kind": "local-integration",
             "argv": ["{python}", "app.py"], "stdout_json_file": "expected.json",
             "timeout_seconds": 10},
        ],
    }
    (root / "checks.json").write_text(json.dumps(config, indent=2) + "\n")
    git(root, "init", "--initial-branch=main")
    git(root, "add", "--", *files, "checks.json")
    git(root, "commit", "-m", "lab: pin contract and scaffold")
    return root


def worker(worktree, branch, filename, content, test_name):
    started = time.monotonic()
    if Path(git(worktree, "rev-parse", "--show-toplevel")).resolve() != worktree.resolve():
        raise RuntimeError("Unexpected worker directory")
    if git(worktree, "branch", "--show-current") != branch:
        raise RuntimeError("Unexpected worker branch")
    (worktree / filename).write_text(content, encoding="utf-8")
    changed = git(worktree, "diff", "--name-only").splitlines()
    if changed != [filename]:
        raise RuntimeError("Worker modified files outside its assignment")
    check = subprocess.run(
        [sys.executable, "-m", "unittest", test_name, "-v"],
        cwd=worktree, capture_output=True, text=True, timeout=10,
    )
    if check.returncode:
        raise RuntimeError(redact(check.stdout + check.stderr))
    git(worktree, "add", "--", filename)
    git(worktree, "commit", "-m", "lab: implement " + filename)
    return {
        "branch": branch, "worktree": str(worktree), "file": filename,
        "commit": git(worktree, "rev-parse", "HEAD"),
        "test": test_name, "test_returncode": check.returncode,
        "test_output": redact(check.stdout + check.stderr),
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def demo(parent=None):
    if shutil.which("git") is None:
        raise RuntimeError("Git must already be installed")
    started = time.monotonic()
    root = prepare(parent)
    print("New demo repository:", root, flush=True)
    with contextlib.redirect_stdout(io.StringIO()):
        baseline_path, baseline, baseline_code = run(
            root / "checks.json", root / ".evidence", "baseline"
        )
    if baseline_code != 1 or baseline["passed"]:
        raise RuntimeError("Expected the intentionally incomplete scaffold to fail")
    base = git(root, "rev-parse", "HEAD")
    tasks = [
        ("lab/compute", "calculate.py", "def total(values):\n    return sum(values)\n",
         "test_app.AppTests.test_total", root / ".parallel" / "compute"),
        ("lab/view", "view.py", 'def render(value):\n    return f"Total: {value}"\n',
         "test_app.AppTests.test_view", root / ".parallel" / "view"),
    ]
    for branch, _, _, _, path in tasks:
        git(root, "worktree", "add", "-b", branch, str(path), base)
    reports = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(worker, path, branch, filename, content, check)
            for branch, filename, content, check, path in tasks
        ]
        for future in as_completed(futures):
            report = future.result()
            if git(root, "status", "--porcelain", "--untracked-files=no"):
                raise RuntimeError("Main checkout must be clean before integration")
            changed = git(root, "diff", "--name-only", base, report["commit"]).splitlines()
            if changed != [report["file"]]:
                raise RuntimeError("Commit changed files outside its assignment")
            git(root, "cherry-pick", "--no-edit", report["commit"])
            report["integrated_as"] = git(root, "rev-parse", "HEAD")
            reports.append(report)
            print("Integrated completed task:", report["branch"], flush=True)
    with contextlib.redirect_stdout(io.StringIO()):
        final_path, final, final_code = run(
            root / "checks.json", root / ".evidence", "verify", baseline_path
        )
    summary = {
        "demo_type": "deterministic local Git exercise; no AI agents were launched",
        "repository": str(root), "base_commit": base,
        "workers": reports,
        "baseline_manifest": str(baseline_path), "final_manifest": str(final_path),
        "baseline_exit": baseline_code, "final_exit": final_code,
        "failed_to_passed_checks": final["failed_to_passed_checks"],
        "main_branch": git(root, "branch", "--show-current"),
        "worktrees": git(root, "worktree", "list", "--porcelain"),
        "duration_seconds": round(time.monotonic() - started, 3),
        "passed": final_code == 0 and len(reports) == 2,
    }
    path = root / "lab-summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print("Integrated checks:", "PASS" if summary["passed"] else "FAIL")
    print("Summary:", path)
    print("Demo preserved for inspection; no remote or push was used.")
    return path, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, help="Existing parent for a newly created demo directory")
    args = parser.parse_args()
    try:
        parent = args.parent.resolve() if args.parent else None
        if parent is not None and not parent.is_dir():
            raise ValueError("--parent must be an existing directory")
        _, summary = demo(parent)
        return 0 if summary["passed"] else 1
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print("Worktree lab error: " + redact(str(exc)), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
