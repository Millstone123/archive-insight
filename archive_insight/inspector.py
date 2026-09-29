from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any


def load_archive(path: Path) -> bytes:
    raw = path.read_bytes()
    if path.suffix == ".hex":
        return bytes.fromhex("".join(raw.decode("ascii").split()))
    return raw


def archive_entries(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(io.BytesIO(load_archive(path))) as archive:
        return [
            {"path": info.filename, "size": info.file_size, "compressed_size": info.compress_size}
            for info in sorted(archive.infolist(), key=lambda item: item.filename)
            if not info.is_dir()
        ]


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("members"), list):
        raise ValueError("manifest must contain a members list")
    return value


def verify_archive(path: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    expected = {item["path"]: item for item in manifest["members"]}
    actual = {item["path"]: item for item in archive_entries(path)}
    errors: list[str] = []
    with zipfile.ZipFile(io.BytesIO(load_archive(path))) as archive:
        for name, item in sorted(expected.items()):
            current = actual.get(name)
            if current is None:
                errors.append(f"missing:{name}")
                continue
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != item.get("sha256"):
                errors.append(f"digest:{name}")
            if len(data) != item.get("size"):
                errors.append(f"size:{name}")
        for name in sorted(set(actual) - set(expected)):
            errors.append(f"unexpected:{name}")
    return {"archive": path.name, "members": len(actual), "expected_members": len(expected), "errors": errors, "valid": not errors}


def summary(path: Path, manifest_path: Path) -> dict[str, Any]:
    result = verify_archive(path, manifest_path)
    result["summary"] = "valid" if result["valid"] else "invalid"
    result["member_names"] = [item["path"] for item in archive_entries(path)]
    return result
