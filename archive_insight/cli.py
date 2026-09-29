from __future__ import annotations

import argparse
import json
from pathlib import Path

from .inspector import archive_entries, summary, verify_archive


def main() -> int:
    parser = argparse.ArgumentParser(prog="archive-insight")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("list", "verify", "summary"):
        command = sub.add_parser(name)
        command.add_argument("archive", type=Path)
        if name in {"verify", "summary"}:
            command.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "list":
        print(json.dumps(archive_entries(args.archive), indent=2, sort_keys=True))
        return 0
    if args.command == "verify":
        print(json.dumps(verify_archive(args.archive, args.manifest), indent=2, sort_keys=True))
        return 0
    result = summary(args.archive, args.manifest)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
