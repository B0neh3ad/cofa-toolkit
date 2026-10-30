"""Generate selected MCP JSON/TOML fragments; never edit managed Codex settings."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def write_new_or_identical(path, content):
    if path.is_symlink():
        raise ValueError(f"Refusing symlink: {path}")
    if path.exists():
        if path.read_text() != content:
            raise ValueError(f"Existing different file, merge explicitly: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(content)


def build_configs(project, names, catalog, node, database=None):
    project = project.resolve(strict=True)
    if not project.is_dir():
        raise ValueError("Project must be an existing directory")
    state = project / ".cofa"
    if state.is_symlink():
        raise ValueError("Refusing symlink state directory")
    configs = {}
    for name in names:
        item = catalog[name]
        if "url" in item:
            configs["cofa_" + name.replace("-", "_")] = {"url": item["url"]}
            continue
        entry = ROOT / "mcp/servers" / name / "node_modules" / item["package"] / "dist/index.js"
        config = {"command": node, "args": [str(entry)]}
        if name == "filesystem":
            config["args"].append(str(project))
        elif name == "memory":
            state.mkdir(exist_ok=True)
            config["env"] = {"MEMORY_FILE_PATH": str(state / "memory.jsonl")}
        elif name == "sequential-thinking":
            config["env"] = {"DISABLE_THOUGHT_LOGGING": "true"}
        elif name == "dbhub":
            if database is None:
                raise ValueError("dbhub requires --database pointing to an existing local SQLite file")
            database = database.resolve(strict=True)
            if not database.is_file():
                raise ValueError("Database must be an existing file")
            # Paths are quoted as TOML strings; no shell, network DSN or credential interpolation.
            db_config = ('[[sources]]\nid = "local"\ndsn = ' + json.dumps("sqlite://" + str(database)) +
                         '\n\n[[tools]]\nname = "execute_sql"\nsource = "local"\nreadonly = true\nmax_rows = 1000\n'
                         '\n[[tools]]\nname = "search_objects"\nsource = "local"\n')
            db_path = state / "dbhub.toml"
            write_new_or_identical(db_path, db_config)
            config["args"].extend(["--transport", "stdio", "--config", str(db_path)])
        configs["cofa_" + name.replace("-", "_")] = config
    return configs


def as_toml(configs):
    lines = []
    for name, config in configs.items():
        lines.append(f"[mcp_servers.{name}]")
        for key in ["command", "args", "url"]:
            if key in config:
                lines.append(f"{key} = {json.dumps(config[key], ensure_ascii=True)}")
        if "env" in config:
            lines.append(f"[mcp_servers.{name}.env]")
            lines.extend(f"{key} = {json.dumps(value)}" for key, value in config["env"].items())
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--servers", nargs="+", default=[])
    parser.add_argument("--database", type=Path)
    parser.add_argument("--install", action="store_true", help="npm ci only for selected servers")
    parser.add_argument("--format", choices=["json", "toml"], default="json")
    parser.add_argument("--output", type=Path, help="Create a new fragment, never replace a different file")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    catalog = json.loads((ROOT / "mcp/catalog.json").read_text())
    if args.list:
        print(json.dumps(catalog, indent=2))
        return 0
    if not args.project or not args.servers:
        parser.error("--project and --servers are required")
    names = list(dict.fromkeys(args.servers))
    if any(name not in catalog for name in names):
        parser.error("Unknown server; use --list")
    local = [name for name in names if "package" in catalog[name]]
    try:
        node = shutil.which("node")
        if local:
            if not node:
                raise ValueError("Node is missing; use compatible choices or CLI fallback, do not upgrade managed tools")
            raw = subprocess.run([node, "--version"], check=True, capture_output=True, text=True).stdout
            version = tuple(map(int, re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)\s*", raw).groups()))
            for name in local:
                required = tuple(catalog[name]["min_node"])
                if version < required:
                    raise ValueError(f"{name} needs Node {'.'.join(map(str, required))}+; actual {raw.strip()}")
        # Validate target and DB requirements before any package installation.
        configs = build_configs(args.project, names, catalog, node, args.database)
        for name in local:
            if args.install:
                npm = shutil.which("npm")
                if not npm:
                    raise ValueError("npm is missing")
                subprocess.run([npm, "ci", "--prefix", str(ROOT / "mcp/servers" / name),
                                "--ignore-scripts", "--no-audit", "--no-fund", "--cache",
                                str(args.project.resolve() / ".cofa/npm-cache")],
                               check=True, timeout=90, stdout=sys.stderr)
            config = configs["cofa_" + name.replace("-", "_")]
            if not Path(config["args"][0]).is_file():
                raise ValueError(f"{name} is not installed; rerun with --install for this choice")
        content = (json.dumps({"mcpServers": configs}, ensure_ascii=False, indent=2) + "\n"
                   if args.format == "json" else as_toml(configs))
        if args.output:
            write_new_or_identical(args.output, content)
            print(str(args.output))
        else:
            print(content, end="")
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, AttributeError) as error:
        parser.exit(1, f"MCP setup stopped: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
