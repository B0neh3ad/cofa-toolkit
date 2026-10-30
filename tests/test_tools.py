"""Tests for evidence integrity and bounded secret reporting, not practice answers."""

import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_checks import run
from scan_secrets import collect, redact, scan


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.code = self.root / "app.py"
        self.code.write_text('print(\'{"total": 1}\')\n')
        (self.root / "expected.json").write_text('{"total": 2}')
        self.config = self.root / "checks.json"
        self.spec = {
            "schema_version": 1,
            "source_paths": ["app.py"],
            "fixed_paths": ["expected.json"],
            "checks": [{
                "id": "result", "kind": "local-integration",
                "argv": ["{python}", "app.py"],
                "stdout_json_file": "expected.json",
                "timeout_seconds": 5,
            }],
        }
        self.save()

    def save(self):
        self.config.write_text(json.dumps(self.spec))

    def execute(self, baseline=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return run(self.config, self.root / "evidence", "verify", baseline)

    def test_red_green_preserves_inputs_and_fingerprints_actual_code(self):
        baseline, before, status = self.execute()
        self.assertEqual(status, 1)
        self.assertEqual(before["checks"][0]["returncode"], 0)
        self.assertEqual(before["checks"][0]["status"], "failed")
        self.code.write_text('print(\'{"total": 2}\')\n')
        _, after, status = self.execute(baseline)
        self.assertEqual(status, 0)
        self.assertEqual(after["failed_to_passed_checks"], ["result"])
        self.assertNotEqual(before["source_sha256_after"], after["source_sha256_after"])
        self.assertTrue(after["source_stable"])

    def test_changed_expected_result_cannot_fake_a_red_green_transition(self):
        baseline, _, _ = self.execute()
        (self.root / "expected.json").write_text('{"total": 1}')
        _, result, status = self.execute(baseline)
        self.assertEqual(result["checks"][0]["status"], "passed")
        self.assertEqual(status, 1)
        self.assertFalse(result["baseline_comparable"])
        self.assertEqual(result["failed_to_passed_checks"], [])

    def test_changed_commands_reject_a_baseline(self):
        baseline, _, _ = self.execute()
        self.spec["checks"][0]["argv"] = ["{python}", "-c", "print('{}')"]
        self.save()
        with self.assertRaisesRegex(ValueError, "different check configuration"):
            self.execute(baseline)

    def test_modification_during_check_invalidates_evidence(self):
        self.code.write_text(
            'from pathlib import Path\n'
            'Path("app.py").write_text("print(0)\\n")\n'
            'print(\'{"total": 2}\')\n'
        )
        _, result, status = self.execute()
        self.assertEqual(status, 1)
        self.assertFalse(result["source_stable"])

    def test_timeout_is_not_reported_as_a_pass(self):
        self.code.write_text("import time\ntime.sleep(10)\n")
        self.spec["checks"][0]["timeout_seconds"] = 0.1
        self.save()
        _, result, status = self.execute()
        self.assertEqual(status, 1)
        self.assertEqual(result["checks"][0]["status"], "timed_out")

    def test_nonzero_output_is_redacted_and_exit_status_preserved(self):
        token = "synthetic" + "credential12345678"
        self.code.write_text(f'print("api_key={token}")\nraise SystemExit(7)\n')
        manifest, result, status = self.execute()
        self.assertEqual(status, 1)
        self.assertEqual(result["checks"][0]["returncode"], 7)
        log = (manifest.parent / result["checks"][0]["log"]).read_text()
        self.assertNotIn(token, log)
        self.assertIn("[REDACTED]", log)

    def test_missing_executable_has_no_fake_exit_code(self):
        self.spec["checks"][0]["argv"] = [str(self.root / "nonexistent-program")]
        self.save()
        _, result, status = self.execute()
        self.assertEqual(status, 1)
        self.assertEqual(result["checks"][0]["status"], "error")
        self.assertIsNone(result["checks"][0]["returncode"])

    def test_json_boolean_does_not_match_a_numeric_expected_value(self):
        (self.root / "expected.json").write_text('{"total": 1}')
        self.code.write_text('print(\'{"total": true}\')\n')
        _, result, status = self.execute()
        self.assertEqual(status, 1)
        self.assertEqual(result["checks"][0]["status"], "failed")

    def test_nonfinite_json_is_not_accepted_as_a_valid_expected_result(self):
        (self.root / "expected.json").write_text('{"total": NaN}')
        self.code.write_text('print(\'{"total": NaN}\')\n')
        _, result, status = self.execute()
        self.assertEqual(status, 1)
        self.assertEqual(result["checks"][0]["status"], "failed")

    def test_source_path_escape_and_credential_flags_are_rejected(self):
        self.spec["source_paths"] = ["../outside.py"]
        self.save()
        with self.assertRaises(ValueError):
            self.execute()
        self.spec["source_paths"] = ["app.py"]
        self.spec["checks"][0]["argv"] = ["tool", "--api-key", "do-not-log"]
        self.save()
        with self.assertRaisesRegex(ValueError, "credentials"):
            self.execute()


class SecretTests(unittest.TestCase):
    def test_findings_include_locations_without_secret_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.txt"
            token = "synthetic" + "credential12345678"
            path.write_text(f'API_KEY="{token}"\n')
            findings = scan(collect([Path(folder)]))
            self.assertEqual(findings[0]["line"], 1)
            self.assertEqual(findings[0]["rule"], "credential-assignment")
            self.assertNotIn(token, json.dumps(findings))

    def test_placeholder_does_not_claim_a_real_credential(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.txt"
            path.write_text('API_KEY="your_example_placeholder"\n')
            self.assertEqual(scan([path]), [])

    def test_gateway_assignment_is_redacted(self):
        token = "synthetic" + "credential12345678"
        self.assertNotIn(token, redact("GATEWAY_KEY=" + token))

    def test_github_pattern_is_detected_without_outputting_value(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.txt"
            token = "gh" + "p_" + "A" * 36
            path.write_text(token)
            findings = scan([path])
            self.assertEqual(findings[0]["rule"], "provider-key")
            self.assertNotIn(token, json.dumps(findings))
            self.assertNotIn(token, redact(token))

    def test_truncated_private_key_and_url_are_redacted(self):
        block = "-----BEGIN " + "PRIVATE KEY-----\nsynthetic-material"
        self.assertNotIn("synthetic-material", redact(block))
        url = "https://example.invalid/?access_token=" + "syntheticcredential123"
        self.assertNotIn("syntheticcredential123", redact(url))

    def test_directory_scan_does_not_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            outside = root / "outside"
            outside.mkdir()
            secret = outside / "secret.txt"
            secret.write_text("not for traversal")
            target = root / "target"
            target.mkdir()
            (target / "link").symlink_to(outside, target_is_directory=True)
            self.assertEqual(collect([target]), [])


if __name__ == "__main__":
    unittest.main()
