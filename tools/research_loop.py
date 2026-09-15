#!/usr/bin/env python3
"""Record auditable phase-5 local-model research without hidden state."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def make_record(topic, source_url, source_name, evidence, summary, model, unknowns):
    record = {
        "schema_version": 1,
        "topic": " ".join(topic.split()),
        "source": {"name": " ".join(source_name.split()), "url": source_url},
        "evidence": " ".join(evidence.split()),
        "summary": " ".join(summary.split()),
        "model": model or "none",
        "unknowns": [" ".join(item.split()) for item in unknowns if item.strip()],
    }
    identity = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["evidence_id"] = hashlib.sha256(identity).hexdigest()[:16]
    record["recorded_utc"] = datetime.now(timezone.utc).isoformat()
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--model", default="none")
    parser.add_argument("--unknown", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.source_url.startswith(("http://", "https://")):
        parser.error("--source-url must use http or https")
    record = make_record(
        args.topic, args.source_url, args.source_name, args.evidence,
        args.summary, args.model, args.unknown,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(record["evidence_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
