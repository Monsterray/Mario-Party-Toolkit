#!/usr/bin/env python3
"""Small, dependency-free result contract for emulator runs.

Process logs can establish loading/booting. Only a person or a narrow oracle
may promote a run to visible or behavioral confirmation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FACTS = ("loaded", "booted", "visibly_changed", "behavior_confirmed")


def observation(*, loaded=False, booted=False, visibly_changed=False, behavior_confirmed=False):
    result = {
        "loaded": bool(loaded),
        "booted": bool(booted),
        "visibly_changed": bool(visibly_changed),
        "behavior_confirmed": bool(behavior_confirmed),
    }
    errors = validate_observation(result)
    if errors:
        raise ValueError("; ".join(errors))
    return result


def validate_observation(value):
    errors = []
    if not isinstance(value, dict):
        return ["observation must be an object"]
    missing = [fact for fact in FACTS if fact not in value]
    if missing:
        errors.append("missing facts: " + ", ".join(missing))
        return errors
    if value["booted"] and not value["loaded"]:
        errors.append("booted requires loaded")
    if value["visibly_changed"] and not value["booted"]:
        errors.append("visibly_changed requires booted")
    if value["behavior_confirmed"] and not value["visibly_changed"]:
        errors.append("behavior_confirmed requires visibly_changed")
    if any(not isinstance(value[fact], bool) for fact in FACTS):
        errors.append("all facts must be boolean")
    return errors


def validate_result(result):
    if not isinstance(result, dict):
        return ["result must be an object"]
    errors = validate_observation(result.get("observation", {}))
    if "schema_version" in result and result["schema_version"] != 1:
        errors.append("unsupported schema_version")
    return errors


def status_for(result):
    errors = validate_result(result)
    if errors:
        return "error"
    facts = result["observation"]
    if facts["behavior_confirmed"]:
        return "behavior_confirmed"
    if facts["visibly_changed"]:
        return "visibly_changed"
    if facts["booted"]:
        return "booted"
    if facts["loaded"]:
        return "loaded"
    return "not_loaded"


def confirm_result(result, facts, evidence=None):
    result = dict(result)
    current = dict(result.get("observation", {}))
    for fact in facts:
        if fact not in FACTS:
            raise ValueError(f"unknown fact: {fact}")
        current[fact] = True
    result["observation"] = observation(**current)
    result["status"] = status_for(result)
    if evidence:
        result["semantic_evidence"] = evidence
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Promote an emulator result after human/oracle confirmation")
    parser.add_argument("result", type=Path)
    parser.add_argument("--confirm", action="append", choices=FACTS, default=[])
    parser.add_argument("--evidence", help="Short description of the observed result")
    parser.add_argument("--output", type=Path, help="Write JSON here; default is stdout")
    args = parser.parse_args(argv)
    data = json.loads(args.result.read_text(encoding="utf-8"))
    data = confirm_result(data, args.confirm, args.evidence)
    errors = validate_result(data)
    if errors:
        parser.error("; ".join(errors))
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
