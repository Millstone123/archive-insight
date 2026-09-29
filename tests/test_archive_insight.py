from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "fixtures" / "release.zip.hex"
MANIFEST = ROOT / "fixtures" / "release.manifest.json"


class ArchiveInsightTests(unittest.TestCase):
    def test_lists_expected_members(self):
        from archive_insight.inspector import archive_entries
        self.assertEqual([item["path"] for item in archive_entries(ARCHIVE)], ["CHANGELOG.md", "LICENSE.txt", "docs/usage.md", "src/build-info.json"])

    def test_verifies_manifest(self):
        from archive_insight.inspector import verify_archive
        self.assertTrue(verify_archive(ARCHIVE, MANIFEST)["valid"])

    def test_detects_unexpected_member(self):
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


if __name__ == "__main__":
    unittest.main()
