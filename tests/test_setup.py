"""Regression checks for project boundaries, existing files and MCP fragments."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location("toolkit_" + name, ROOT / "scripts" / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


setup = module("setup")
mcp = module("mcp_config")
CATALOG = json.loads((ROOT / "mcp/catalog.json").read_text())


class SetupTests(unittest.TestCase):
    def test_existing_project_instructions_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            instructions = project / "AGENTS.md"
            instructions.write_text("Existing task rules")
            plan = setup.plan_install(project, ["domain-discovery"], ["AGENTS.md"])
            self.assertEqual([p[3] for p in plan], ["copy", "skipped-existing"])
            self.assertEqual(instructions.read_text(), "Existing task rules")
            self.assertFalse((project / ".agents").exists())

    def test_existing_identical_skill_is_idempotent_and_changes_are_not_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            import shutil
            project = Path(folder)
            destination = project / ".agents/skills/domain-discovery"
            shutil.copytree(ROOT / "skills/domain-discovery", destination)
            self.assertEqual(setup.plan_install(project, ["domain-discovery"], [])[0][3], "unchanged")
            (destination / "SKILL.md").write_text("Local adaptation")
            self.assertEqual(setup.plan_install(project, ["domain-discovery"], [])[0][3], "skipped-existing")

    def test_path_escape_and_unknown_skill_do_not_write_anything(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            for name in ["../outside", "not-a-real-skill"]:
                with self.assertRaises(ValueError):
                    setup.plan_install(project, [name], [])
            self.assertEqual(list(project.iterdir()), [])

    def test_symlink_skill_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as outside:
            project = Path(folder)
            (project / ".agents").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                setup.plan_install(project, ["domain-discovery"], [])

    def test_nested_links_in_existing_skills_are_preserved_without_reading_targets(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as outside:
            project = Path(folder)
            destination = project / ".agents/skills/domain-discovery"
            destination.mkdir(parents=True)
            private = Path(outside) / "private.txt"
            private.write_text("outside selected project")
            (destination / "reference.txt").symlink_to(private)
            with mock.patch.object(setup, "tree_digest", side_effect=AssertionError("Must not read linked content")):
                plan = setup.plan_install(project, ["domain-discovery"], [])
            self.assertEqual(plan[0][3], "skipped-existing")


class MCPTests(unittest.TestCase):
    def test_local_scope_and_memory_file_are_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder).resolve()
            configs = mcp.build_configs(project, ["filesystem", "memory"], CATALOG, "/usr/bin/node")
            self.assertEqual(configs["cofa_filesystem"]["args"][-1], str(project))
            self.assertEqual(configs["cofa_memory"]["env"]["MEMORY_FILE_PATH"], str(project / ".cofa/memory.jsonl"))
            self.assertFalse((project / ".codex").exists())

    def test_db_requires_existing_file_and_generates_tool_level_readonly(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            with self.assertRaises(ValueError):
                mcp.build_configs(project, ["dbhub"], CATALOG, "node")
            db = project / 'measurements.db'
            db.touch()
            configs = mcp.build_configs(project, ["dbhub"], CATALOG, "node", db)
            config = (project / ".cofa/dbhub.toml").read_text()
            self.assertIn('name = "execute_sql"\nsource = "local"\nreadonly = true', config)
            self.assertIn('--config', configs["cofa_dbhub"]["args"])
            self.assertNotIn('--dsn', configs["cofa_dbhub"]["args"])

    def test_existing_output_and_symlink_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fragment.json"
            mcp.write_new_or_identical(path, "original")
            mcp.write_new_or_identical(path, "original")
            with self.assertRaises(ValueError):
                mcp.write_new_or_identical(path, "different")
            self.assertEqual(path.read_text(), "original")
            link = path.parent / "link"
            link.symlink_to(path)
            with self.assertRaises(ValueError):
                mcp.write_new_or_identical(link, "original")

    def test_remote_only_config_needs_no_node_or_credentials(self):
        with tempfile.TemporaryDirectory() as folder:
            configs = mcp.build_configs(Path(folder), ["openai-docs"], CATALOG, None)
            self.assertEqual(configs["cofa_openai_docs"], {"url": "https://developers.openai.com/mcp"})
            text = mcp.as_toml(configs)
            self.assertIn('[mcp_servers.cofa_openai_docs]', text)
            self.assertNotIn('token', text)


if __name__ == "__main__":
    unittest.main()
