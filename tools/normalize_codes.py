#!/usr/bin/env python3
"""Normalize and deduplicate JSONL code candidates with provenance."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

CODE_RE = re.compile(r"^([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]{2,8})$")


def _text(value, field):
    value = " ".join(str(value or "").split())
    if not value:
        raise ValueError(f"{field} is required")
    return value


def _source_url(value):
    value = _text(value, "source_url")
    if urlparse(value).scheme not in {"http", "https"}:
        raise ValueError("source_url must use http or https")
    return value


def _code_lines(value):
    lines = value if isinstance(value, list) else str(value or "").splitlines()
    normalized, ignored = [], []
    for raw in lines:
        line = " ".join(str(raw).split())
        if not line or line.startswith(("#", "//")):
            continue
        match = CODE_RE.fullmatch(line)
        if match:
            normalized.append(f"{match.group(1).upper()} {match.group(2).upper()}")
        else:
            ignored.append(line)
    if not normalized:
        raise ValueError("codes contains no valid code lines")
    return normalized, ignored


def normalize_record(raw):
    if not isinstance(raw, dict):
        raise ValueError("each candidate must be an object")
    lines, ignored = _code_lines(raw.get("codes"))
    record = {
        "game": _text(raw.get("game"), "game").lower(),
        "region": _text(raw.get("region", "unknown"), "region").upper(),
        "revision": _text(raw.get("revision", "unknown"), "revision"),
        "code_family": _text(raw.get("code_family", "unknown"), "code_family").lower(),
        "name": _text(raw.get("name"), "name"),
        "code_lines": lines,
        "source_url": _source_url(raw.get("source_url")),
        "source_name": _text(raw.get("source_name"), "source_name"),
        "evidence": _text(raw.get("evidence"), "evidence"),
        "confidence": float(raw.get("confidence", 0.5)),
    }
    if not 0 <= record["confidence"] <= 1:
        raise ValueError("confidence must be between 0 and 1")
    identity = json.dumps({key: record[key] for key in (
        "game", "region", "revision", "code_family", "code_lines"
    )}, sort_keys=True, separators=(",", ":")).encode()
    record["id"] = hashlib.sha256(identity).hexdigest()[:16]
    if ignored:
        record["ignored_lines"] = ignored
    return record


def normalize_records(candidates):
    records, duplicates, errors = [], [], []
    seen = set()
    for number, candidate in enumerate(candidates, 1):
        try:
            record = normalize_record(candidate)
        except (TypeError, ValueError) as error:
            errors.append({"line": number, "error": str(error)})
            continue
        if record["id"] in seen:
            duplicates.append({
                "duplicate_of": record["id"],
                "name": record["name"],
                "source_url": record["source_url"],
                "source_name": record["source_name"],
            })
            continue
        seen.add(record["id"])
        records.append(record)
    return {"schema_version": 1, "records": records, "duplicates": duplicates, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSONL candidate file")
    parser.add_argument("--output", type=Path, help="Optional normalized JSON output")
    args = parser.parse_args()
    candidates = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    result = normalize_records(candidates)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
