"""Small local heuristic check. Reports locations and rules, never matched values."""

import argparse
import json
import re
from pathlib import Path


RULES = {
    "private-key": re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
    "provider-key": re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b"
    ),
    "credential-assignment": re.compile(
        r"""(?i)\b(?:api[_-]?key|gateway[_-]?key|access[_-]?token|token|client[_-]?secret|secret|password|authorization)\b"""
        r"""["']?\s*[:=]\s*["']?([A-Za-z0-9_./+=-]{16,})"""
    ),
    "credential-url": re.compile(
        r"(?i)[?&](?:token|api_key|access_token|secret|password)=([^&\s\"']{12,})"
    ),
}
PLACEHOLDERS = ("example", "placeholder", "your_", "changeme", "redacted")
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}


def redact(text):
    text = re.sub(
        r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----.*?"
        r"(?:-----END (?:[A-Z0-9]+ )*PRIVATE KEY-----|\Z)",
        "[REDACTED PRIVATE KEY]",
        text,
        flags=re.S,
    )
    text = RULES["provider-key"].sub("[REDACTED KEY]", text)
    text = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9_./+=-]+", "Bearer [REDACTED]", text)
    text = re.sub(
        r"""(?i)(\b(?:api[_-]?key|gateway[_-]?key|access[_-]?token|token|client[_-]?secret|secret|password|authorization)\b"""
        r"""["']?\s*[:=]\s*["']?)([^\s"'&,;}]+)""",
        r"\1[REDACTED]",
        text,
    )
    return text


def scan(paths):
    findings = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for rule, pattern in RULES.items():
            for match in pattern.finditer(text):
                value = match.group(1) if match.lastindex else match.group()
                if any(word in value.lower() for word in PLACEHOLDERS):
                    continue
                findings.append({
                    "path": str(path),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "rule": rule,
                })
    return findings


def collect(paths):
    result = set()
    for path in paths:
        if path.is_symlink():
            raise ValueError("Symlink input is not supported")
        path = path.resolve()
        if path.is_file():
            result.add(path)
        elif path.is_dir():
            for candidate in path.rglob("*"):
                relative = candidate.relative_to(path)
                if any(part in SKIP_DIRS for part in relative.parts):
                    continue
                if candidate.is_symlink() or any(
                    parent.is_symlink() for parent in candidate.parents
                    if parent != path and parent.is_relative_to(path)
                ):
                    continue
                if candidate.is_file():
                    result.add(candidate)
        else:
            raise ValueError("Input path does not exist")
    return sorted(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        findings = scan(collect(args.paths))
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": redact(str(exc))}))
        return 2
    print(json.dumps({
        "findings": findings,
        "scope": "heuristic only; zero findings is not proof of no secrets",
    }, ensure_ascii=False, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
