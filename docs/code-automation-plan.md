# Automated code discovery and testing plan

## Goal

Make new Mario Party codes easy to discover, normalize, validate, and test
without confusing code loading with gameplay proof.

## Milestones

### 1. Catalog and deterministic validation

- Inventory every generator in `codes/marioParty1.py` through
  `codes/marioParty9.py`.
- Record each generator's parameters, platform, code family, and preferred
  test runner.
- Add tests that fail when a generator cannot be imported or disappears from
  the catalog.
- Keep ROM identity and gameplay fixtures separate from generator metadata.

### 2. Source ingestion and normalization

- Import candidate codes from trusted databases and project sources.
- Normalize GameShark, Gecko, and Action Replay text into one schema.
- Record source URLs, region, revision, confidence, and evidence excerpts.
- Deduplicate equivalent code lists.

The first deterministic importer is `tools/normalize_codes.py`. It accepts one
JSON object per line with `game`, `name`, `codes`, `source_url`, `source_name`,
and `evidence`; `region`, `revision`, `code_family`, and `confidence` are also
accepted. It emits canonical records, duplicate provenance, and line-level
errors:

```bash
./mariovenv/bin/python tools/normalize_codes.py candidates.jsonl \
  --output normalized-codes.json
```

Model-generated summaries may help fill descriptions later, but source URLs,
code lines, and evidence remain deterministic inputs and are never inferred by
the importer.

### 3. Emulator runners and baseline fixtures

- Use Mupen native cheats for MP1–3.
- Use Dolphin native Gecko codes for MP4–9.
- Keep GeckoLoader-patched images as a separate compatibility target.
- Add deterministic save states, input sequences, screenshots, and logs.

### 4. Semantic verification

- Define an expected observable result for each fixture, such as coin count,
  star price, or minigame selection.
- Compare baseline and modified runs with screenshots, OCR, memory watches, or
  other narrow oracles.
- Report `loaded`, `booted`, `visibly_changed`, and `behavior_confirmed`
  separately.

### 5. Local-model research loop

- Let local-LLM retrieve, summarize, normalize, rank, and deduplicate sources.
- Require evidence IDs and explicit unknowns in every factual result.
- Cache extracted pages and disassembly; send only changed or relevant facts.
- Use frontier models only for unresolved conflicts or high-value synthesis.

## Milestone 1 usage

Print the current deterministic catalog with:

```bash
./mariovenv/bin/python tools/code_catalog.py --pretty
```

The catalog is generated from Python signatures rather than hand-maintained
duplicate metadata. This keeps it accurate while the code-generator API is
still changing.

## Milestones 3 and 4 usage

Runner output now carries an explicit observation contract. A process/log can
establish `loaded` and `booted`; it must not claim gameplay success. Confirm
the visible and behavioral facts only after checking the baseline and modified
runs yourself:

```bash
./mariovenv/bin/python tools/runner_result.py run.json \
  --confirm visibly_changed \
  --confirm behavior_confirmed \
  --evidence "Blue-space coin count changed in gameplay" \
  --output verified-run.json
```

The contract rejects impossible claims (`booted` without `loaded`, visible
change without boot, and behavior without a visible change). Reusable fixture
metadata lives in `data/test-scenarios.json`; ROM paths remain machine-local.
Use `mpt_cli native-cheat` for MP1–3 and the native Dolphin Gecko runner for
MP4–9. GeckoLoader images remain a separate compatibility test target.
