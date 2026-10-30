"""Run explicit local checks and preserve versioned, redacted execution evidence."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
import uuid

from scan_secrets import redact


MAX_LOG_BYTES = 262144
KINDS = {"unit", "local-integration", "mock", "external-integration", "static"}
CREDENTIAL_FLAG = re.compile(
    r"(?i)^--?(?:api[-_]key|access[-_]token|token|password|secret|authorization)(?:=|$)"
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_file(root, value):
    if not isinstance(value, str) or Path(value).is_absolute():
        raise ValueError("Configured file paths must be relative to the config directory")
    path = (root / value).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("Configured file must exist within the config directory")
    return path


def validate(config, root):
    if config.get("schema_version") != 1:
        raise ValueError("Expected schema_version 1")
    sources = config.get("source_paths")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source_paths must list the files whose state is being checked")
    for value in sources:
        local_file(root, value)
    fixed = config.get("fixed_paths", [])
    if not isinstance(fixed, list):
        raise ValueError("fixed_paths must be a list")
    for value in fixed:
        local_file(root, value)
    checks = config.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("checks must be a nonempty list")
    ids = set()
    for case in checks:
        case_id = case.get("id", "")
        if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", case_id):
            raise ValueError("Check IDs must contain only letters, digits, _ or -")
        if case_id in ids:
            raise ValueError("Check IDs must be unique")
        ids.add(case_id)
        argv = case.get("argv")
        if not isinstance(argv, list) or not argv or not all(
            isinstance(arg, str) and arg for arg in argv
        ):
            raise ValueError("argv must be a nonempty list of nonempty strings")
        if any(CREDENTIAL_FLAG.match(arg) for arg in argv):
            raise ValueError("Do not put credentials in command arguments")
        if case.get("kind") not in KINDS:
            raise ValueError("Each check needs an explicit supported kind")
        timeout = case.get("timeout_seconds", 60)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise ValueError("timeout_seconds must be a number")
        if not math.isfinite(timeout) or not 0 < timeout <= 3600:
            raise ValueError("timeout_seconds must be between 0 and 3600")
        if "stdout_json_file" in case:
            local_file(root, case["stdout_json_file"])


def snapshot(root, paths):
    return {value: digest(local_file(root, value)) for value in paths}


def execute(case, root, output):
    started = time.monotonic()
    argv = [sys.executable if arg == "{python}" else arg for arg in case["argv"]]
    status, reason, returncode = "error", None, None
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            process = subprocess.Popen(
                argv, cwd=root, stdin=subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, start_new_session=(os.name == "posix"),
            )
            try:
                returncode = process.wait(timeout=case.get("timeout_seconds", 60))
                status = "passed" if returncode == 0 else "failed"
                if returncode != 0:
                    reason = "nonzero exit"
            except subprocess.TimeoutExpired:
                if os.name == "posix":
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    process.kill()
                returncode = process.wait()
                status, reason = "timed_out", "timeout"
        except OSError as exc:
            reason = redact(str(exc))
        stdout.seek(0)
        stderr.seek(0)
        out_bytes = stdout.read(MAX_LOG_BYTES + 1)
        err_bytes = stderr.read(MAX_LOG_BYTES + 1)
    truncated = len(out_bytes) > MAX_LOG_BYTES or len(err_bytes) > MAX_LOG_BYTES
    out_text = out_bytes[:MAX_LOG_BYTES].decode("utf-8", errors="replace")
    err_text = err_bytes[:MAX_LOG_BYTES].decode("utf-8", errors="replace")
    if status == "passed" and "stdout_json_file" in case:
        try:
            expected = json.loads(local_file(root, case["stdout_json_file"]).read_text())
            actual = json.loads(out_text)
            actual_json = json.dumps(actual, sort_keys=True, allow_nan=False)
            expected_json = json.dumps(expected, sort_keys=True, allow_nan=False)
            if actual_json != expected_json or len(out_bytes) > MAX_LOG_BYTES:
                status, reason = "failed", "stdout JSON differs from expected JSON"
        except (ValueError, OSError):
            status, reason = "failed", "stdout or expected file is not valid JSON"
    log_name = case["id"] + ".log"
    log = redact("STDOUT\n" + out_text + "\nSTDERR\n" + err_text)
    if truncated:
        log += "\n[LOG TRUNCATED; inspect the command locally if needed]\n"
    (output / log_name).write_text(log, encoding="utf-8")
    return {
        "id": case["id"], "kind": case["kind"],
        "requirements": case.get("requirements", []),
        "argv": [redact(arg) for arg in argv],
        "status": status, "reason": reason, "returncode": returncode,
        "log": log_name, "log_truncated": truncated,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def run(config_path, out_root, stage, baseline_path=None):
    config_path = config_path.resolve()
    root = config_path.parent
    config = json.loads(config_path.read_text(encoding="utf-8"))
    validate(config, root)
    config_hash = digest(config_path)
    baseline = None
    if baseline_path is not None:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        if baseline.get("config_sha256") != config_hash:
            raise ValueError("Baseline used a different check configuration")
        if baseline.get("schema_version") != 1:
            raise ValueError("Unsupported baseline schema")
    tracked = list(dict.fromkeys([
        *config["source_paths"],
        *config.get("fixed_paths", []),
        *(case["stdout_json_file"] for case in config["checks"] if "stdout_json_file" in case),
    ]))
    fixed = set(config.get("fixed_paths", [])) | {
        case["stdout_json_file"] for case in config["checks"] if "stdout_json_file" in case
    }
    before = snapshot(root, tracked)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    output = out_root.resolve() / run_id
    output.mkdir(parents=True, exist_ok=False)
    results = [execute(case, root, output) for case in config["checks"]]
    after = {}
    source_errors = []
    for value in tracked:
        try:
            after[value] = digest(local_file(root, value))
        except (OSError, ValueError):
            after[value] = None
            source_errors.append(value)
    try:
        config_after = digest(config_path)
    except OSError:
        config_after = None
    stable = before == after and config_hash == config_after
    transitions = []
    comparable = baseline is not None and baseline.get("source_stable") is True
    if comparable:
        for value in fixed:
            if baseline.get("source_sha256_after", {}).get(value) != before[value]:
                comparable = False
    if baseline is not None and comparable and stable:
        previous = {case["id"]: case for case in baseline.get("checks", [])}
        for result in results:
            prior = previous.get(result["id"], {})
            if prior.get("status") == "failed" and result["status"] == "passed":
                transitions.append(result["id"])
    passed = stable and all(case["status"] == "passed" for case in results)
    if baseline is not None and not comparable:
        passed = False
    manifest = {
        "schema_version": 1, "stage": stage, "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": config_hash, "python_version": sys.version.split()[0],
        "source_sha256_before": before, "source_sha256_after": after,
        "source_stable": stable, "source_errors": source_errors,
        "checks": results, "passed": passed,
        "baseline_run_id": baseline.get("run_id") if baseline else None,
        "baseline_comparable": comparable,
        "failed_to_passed_checks": transitions,
        "note": "Check transitions require human cause review. Kind labels do not prove external API execution.",
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    for case in results:
        print(f'{case["id"]}: {case["status"]} (exit={case["returncode"]})')
    if not stable:
        print("Sources or configuration changed during the run; evidence is not stable.")
    if baseline is not None and not comparable:
        print("Baseline is not comparable; do not claim the same checks changed from red to green.")
    print(manifest_path)
    return manifest_path, manifest, 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--stage", choices=["baseline", "verify"], default="verify")
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    try:
        out = args.out or args.config.resolve().parent / ".evidence"
        _, _, code = run(args.config, out, args.stage, args.baseline)
        return code
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
        print("Check runner configuration error: " + redact(str(exc)), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
