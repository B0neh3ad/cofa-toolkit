"""Copy selected toolkit skills/templates into a project without replacing existing files."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def tree_digest(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob("*")) if p.is_file()}


def plan_install(target, names, templates):
    target = target.resolve(strict=True)
    if not target.is_dir():
        raise ValueError("Target must be an existing project directory")
    planned = []
    for kind, entries in [("skill", names), ("template", templates)]:
        for name in sorted(set(entries)):
            if Path(name).name != name or name in {".", ".."}:
                raise ValueError("Use catalog names, not paths")
            src = ROOT / ("skills" if kind == "skill" else "templates") / name
            dst = target / ".agents/skills" / name if kind == "skill" else target / name
            if not src.exists() or (kind == "skill" and not (src / "SKILL.md").is_file()):
                raise ValueError(f"Unknown {kind}: {name}")
            if src.is_symlink() or (src.is_dir() and any(p.is_symlink() for p in src.rglob("*"))):
                raise ValueError(f"Symlink source is not supported: {name}")
            cursor = dst
            while cursor != target:
                if cursor.is_symlink():
                    raise ValueError(f"Refusing symlink destination: {cursor}")
                cursor = cursor.parent
            if dst.exists():
                linked_contents = kind == "skill" and dst.is_dir() and any(p.is_symlink() for p in dst.rglob("*"))
                same = (dst.is_dir() and not linked_contents and tree_digest(src) == tree_digest(dst)) if kind == "skill" else (
                    dst.is_file() and src.read_bytes() == dst.read_bytes())
                status = "unchanged" if same else "skipped-existing"
            else:
                status = "copy"
            planned.append((src, dst, kind, status))
    return planned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--profile", action="append", default=[])
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--template", action="append", default=[])
    parser.add_argument("--all-skills", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    profiles = json.loads((ROOT / "skills/profiles.json").read_text())
    available = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
    if args.list:
        print(json.dumps({"profiles": profiles, "skills": available,
                          "templates": sorted(p.name for p in (ROOT / "templates").iterdir() if p.is_file())},
                         ensure_ascii=False, indent=2))
        return 0
    if not args.target:
        parser.error("--target is required unless --list is used")
    names = list(available if args.all_skills else args.skill)
    for profile in args.profile:
        if profile not in profiles:
            parser.error(f"Unknown profile: {profile}")
        names.extend(profiles[profile])
    if not names and not args.template:
        parser.error("Choose --profile, --skill, --all-skills, or --template")
    try:
        plan = plan_install(args.target, names, args.template)
        for src, dst, kind, status in plan:
            if status == "copy" and not args.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if kind == "skill":
                    shutil.copytree(src, dst)
                else:
                    # Exclusive creation also protects an existing file created after preflight.
                    with dst.open("xb") as stream:
                        stream.write(src.read_bytes())
            print(f"{status}: {dst}")
    except (ValueError, OSError) as error:
        parser.exit(1, f"Setup stopped: {error}\n")
    print("No existing instruction/configuration file was replaced. Merge skipped templates explicitly.")
    print("Check /skills in the provided Codex; if not detected, start a new session or read SKILL.md explicitly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
