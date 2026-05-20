#!/usr/bin/env python3
"""CLI entry point for the FNOL claims processing agent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.agent import process_fnol, process_fnol_to_json


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Process FNOL documents and produce routing recommendations."
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to a single FNOL file (.txt or .pdf)",
    )
    parser.add_argument(
        "--samples",
        action="store_true",
        help="Process all sample documents in ./samples/",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for JSON output when using --samples (default: output)",
    )
    args = parser.parse_args()

    if args.samples:
        samples_dir = Path(__file__).parent / "samples"
        files = sorted(samples_dir.glob("fnol_*.*"))
        if not files:
            print("No sample files found.", file=sys.stderr)
            return 1
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for path in files:
            if path.suffix.lower() not in {".txt", ".pdf"}:
                continue
            result = process_fnol(path)
            out_path = args.output_dir / f"{path.stem}.json"
            out_path.write_text(
                json.dumps(result.to_json_dict(), indent=2),
                encoding="utf-8",
            )
            print(f"Processed {path.name} -> {out_path}")
            print(json.dumps(result.to_json_dict(), indent=2))
            print("-" * 60)
        return 0

    if not args.path:
        parser.print_help()
        return 1

    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    print(process_fnol_to_json(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
