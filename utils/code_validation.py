"""Lightweight checks that stop obviously mis-targeted code from being injected."""

import re


TARGET_RE = re.compile(r"\bMP([123])\b", re.IGNORECASE)


def code_targets(code_text: str):
    return {f"mp{match.group(1)}" for match in TARGET_RE.finditer(code_text)}


def validate_code_target(code_text: str, game: str):
    expected = game.lower()
    targets = code_targets(code_text)
    if not targets:
        return True, "No explicit game label found; ROM identity check is still required."
    if targets == {expected}:
        return True, f"Codes are labeled for {expected.upper()}."
    return False, f"Codes target {', '.join(sorted(targets))}; selected ROM target is {expected.upper()}."
