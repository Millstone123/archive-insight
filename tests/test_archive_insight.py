from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "fixtures" / "release.zip.hex"
MANIFEST = ROOT / "fixtures" / "release.manifest.json"
PREVIEW = ROOT / "fixtures" / "release-preview.link"


class ArchiveInsightTests(unittest.TestCase):
    def test_lists_expected_members(self):
        from archive_insight.inspector import archive_entries
        self.assertEqual([item["path"] for item in archive_entries(ARCHIVE)], ["CHANGELOG.md", "LICENSE.txt", "docs/usage.md", "src/build-info.json"])

    def test_verifies_manifest(self):
        from archive_insight.inspector import verify_archive
        self.assertTrue(verify_archive(ARCHIVE, MANIFEST)["valid"])

    def test_detects_unexpected_member(self):
        import io
        import tempfile
        import zipfile
        from archive_insight.inspector import load_archive, verify_archive
        with zipfile.ZipFile(io.BytesIO(load_archive(ARCHIVE))) as source:
            entries = {item.filename: source.read(item.filename) for item in source.infolist()}
        entries["EXTRA.txt"] = b"extra\n"
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "changed.zip"
            with zipfile.ZipFile(changed, "w") as output:
                for name, data in sorted(entries.items()):
                    output.writestr(name, data)
            result = verify_archive(changed, MANIFEST)
        self.assertFalse(result["valid"])
        self.assertIn("unexpected:EXTRA.txt", result["errors"])

    def test_preview_smoke(self):
        completed = subprocess.run([sys.executable, "-m", "archive_insight", "preview", str(ARCHIVE)], cwd=ROOT, text=True, capture_output=True, check=True)
        result = json.loads(completed.stdout)
        self.assertTrue(result["previewed"])
        self.assertEqual(result["preview_exit"], 0)

    def test_summary_is_deterministic(self):
        completed = subprocess.run([sys.executable, "-m", "archive_insight", "summary", str(ARCHIVE), "--manifest", str(MANIFEST), "--preview", str(PREVIEW)], cwd=ROOT, text=True, capture_output=True, check=True)
        result = json.loads(completed.stdout)
        self.assertEqual(result["summary"], "valid")
        self.assertEqual(result["preview_exit"], 0)
        self.assertEqual(result["members"], 4)


if __name__ == "__main__":
    unittest.main()
