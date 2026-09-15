# PartyPlanner64 integration research

Research date: 2026-09-14

This note is based on PartyPlanner64’s official repositories, source-adjacent configuration, and project documentation. It does not copy ROMs or other copyrighted game assets into Mario Party Toolkit (MPT).

## Executive summary

PartyPlanner64 (PP64) and MPT can complement one another without becoming one application:

1. PP64 should remain the board editor/importer for Mario Party 1–3.
2. MPT should validate the user’s input ROM, generate or apply codes/patches, and launch the result in a configured emulator.
3. The shared contract should be a small, text-based manifest plus user-selected patch files—not extracted ROM data or bundled game assets.
4. Every generated code must be tied to a specific title, region, revision, byte order, and base-ROM hash. “Mario Party 1” alone is not enough.

## Current MPT implementation

The repository now provides the first validation and portability layer:

- `utils/rom_identity.py` recognizes N64 byte order, header fields, MD5, and SHA-256.
- `utils/code_validation.py` detects explicit MP1/MP2/MP3 labels and rejects mixed targets.
- The injector uses a per-run temporary directory and platform-independent paths.
- WIT is used for ISO/WBFS extraction and rebuilds.
- GeckoLoader can run from its official Python CLI checkout on macOS/Linux.
- GitHub Actions tests and packages the application on Ubuntu, macOS, and Windows.

N64 `GSInject` remains unresolved. MPT does not claim compatibility with unrelated SM64-, Mario Kart-, or emulator-specific injectors.

## What PP64 already provides

The main repository says PP64 creates/imports custom boards into Mario Party N64 ROMs. It supports only the NTSC-USA Mario Party 1, 2, and 3 base files and publishes the expected MD5 for each:

| Game | PP64-supported base | MD5 published by PP64 |
|---|---|---|
| Mario Party | `Mario Party (U).z64` | `8BC2712139FBF0C56C8EA835802C52DC` |
| Mario Party 2 | `Mario Party 2 (U).z64` | `04840612A35ECE222AFDB2DFBF926409` |
| Mario Party 3 | `Mario Party 3 (U).z64` | `76A8BBC81BC2060EC99C9645867237CC` |

PP64 also states that edited ROMs can be reopened, and that N64 hardware/emulators need the Expansion Pak equivalent (8 MB RAM). Mupen64Plus is listed among the working emulators. These are direct compatibility requirements for any MPT “open in emulator” workflow.

Source: [PartyPlanner64 README](https://github.com/PartyPlanner64/PartyPlanner64#readme).

The repository’s public structure identifies several reusable seams:

- `apps/cli`: a command-line build surface documented by the project README.
- `packages/lib`: reusable TypeScript library code.
- `symbols`: a submodule containing game symbols.
- `public` and build scripts: editor/runtime assets and packaging, which MPT should not copy wholesale.

Source: [PartyPlanner64 repository](https://github.com/PartyPlanner64/PartyPlanner64).

## Reusable data and knowledge

### 1. ROM identity records

MPT should maintain a versioned compatibility table modeled on PP64’s explicit identity rules. At minimum, a record should contain:

```json
{
  "game": "Mario Party 2",
  "region": "NTSC-U",
  "revision": "PP64-supported revision",
  "byte_order": "z64",
  "md5": "04840612A35ECE222AFDB2DFBF926409",
  "ram_mb": 8
}
```

The manifest should also record the output hash after patching. That gives MPT a reproducible answer to “which ROM does this code/patch target?” and prevents applying MP1/MP2/MP3 addresses interchangeably.

MPT should treat PP64’s hashes as compatibility identifiers, not as a reason to distribute ROMs.

### 2. Symbols and RAM labels

The official `symbols` repository contains Project64-debugger-format symbol files for Mario Party 1–3 in Japanese, European, and USA variants. These are useful for:

- displaying human-readable names in a code editor;
- cross-checking MPT’s address labels;
- generating emulator debugger symbol files;
- documenting why a code is tied to one region/revision.

Source: [PartyPlanner64/symbols README](https://github.com/PartyPlanner64/symbols).

MPT should import symbol text as an optional, versioned resource and preserve its source URL/commit. It should not infer that a symbol name is valid for another revision.

### 3. ROM layout/configuration knowledge

PP64’s published Mario Party 1 splitter configuration demonstrates a machine-readable layout approach: header checksum checks, ROM ranges, overlays, main filesystem, strings, HVQ data, audio, and RAM labels. This is valuable as a model for MPT’s own validator and code-generation metadata.

Source: [PartyPlanner64’s `marioparty.u.singleoverlay.yaml` configuration](https://gist.github.com/PartyPlanner64/93952bc7e1e403fda023d17ecb74bd2a).

Recommended MPT representation:

- immutable game identity and expected header checksums;
- named ROM offsets and lengths;
- named RAM addresses;
- alignment and endian requirements;
- a list of operations permitted for that exact target;
- a postcondition or byte signature for every operation.

MPT should store these as metadata and signatures, not as copied ROM sections.

### 4. Custom events and assembly examples

The official PP64 events repository contains small assembly/C examples such as coin adjustment, random coins, sound playback, message display, warps, and debug text. These are useful as interoperability fixtures and as examples for an MPT code generator.

Source: [PartyPlanner64/events](https://github.com/PartyPlanner64/events).

The safe reuse pattern is to link to or separately license compatible source examples, then compile/apply them against a user-provided ROM. MPT should not silently copy game-derived binary payloads into the repository.

## Code generation and validation

PP64’s event examples use source-level assembly conventions, including game tags and execution mode in comments. MPT can adopt a stricter machine-readable wrapper around that idea:

```yaml
id: mp2-give-coins-v1
game: mario-party-2
region: NTSC-U
base_md5: 04840612A35ECE222AFDB2DFBF926409
byte_order: z64
source: user-project-or-licensed-example
operations:
  - kind: write32
    offset: 0x00123456
    expected_before: [0x00, 0x00, 0x00, 0x00]
    value: 0xXXXXXXXX
postconditions:
  - kind: hash
    scope: modified_ranges
```

Before writing, MPT should:

1. normalize/check byte order;
2. identify the game, region, revision, and full-file hash;
3. reject a mismatch unless the user explicitly selects a compatible target;
4. verify every expected-before signature;
5. write to a new output file, never in place by default;
6. verify output length, modified ranges, and postconditions;
7. emit a manifest containing input/output hashes, operations, and tool versions.

For PP64-created boards, the safest validation is layered:

- PP64 acceptance: the input is one of PP64’s supported NTSC-U bases or an edited derivative PP64 can reopen.
- MPT structural validation: the manifest’s game/revision and byte order match; writes land in declared ranges; no unexpected ranges changed.
- Emulator smoke test: launch the output with 8 MB RAM and record whether it reaches the title/board screen.
- Human gameplay test: verify board traversal, events, and any injected code in a short multiplayer session.

An emulator boot is not proof that a code is semantically correct; it only catches some packaging and catastrophic patch errors.

## Safe interoperability design

### Recommended first integration

Implement a “PP64 handoff” in MPT rather than embedding PP64:

1. MPT validates/selects a user-owned MP1/2/3 ROM.
2. MPT opens PP64’s hosted/local editor or imports a user-exported board artifact if PP64 exposes a stable export format.
3. The user saves a PP64-edited ROM outside the repository.
4. MPT re-identifies the edited ROM by its base identity plus a transformation manifest.
5. MPT applies only compatible codes/patches, writes a new output, verifies it, and launches Mupen64Plus.

This avoids coupling MPT to PP64’s private UI internals and avoids distributing ROM content.

### Do not assume a board file format yet

The official sources inspected here establish PP64’s supported ROMs, symbols, splitter configuration, and event examples, but do not establish a stable public board interchange format suitable for MPT. Before implementing an importer, inspect the current `apps/cli` and `packages/lib` source at a pinned commit and identify an explicit exported schema/API. If no stable format exists, use the ROM handoff plus identity manifest first.

### Emulator integration

MPT should generate a per-output sidecar such as `output.mpt.json` and launch the emulator with the output ROM and the required 8 MB setting. The sidecar should include:

- base and output SHA-256/MD5;
- PP64 identity, if applicable;
- MPT patch/code IDs and versions;
- modified ranges;
- emulator name/version and RAM setting;
- validation results.

This makes bug reports reproducible without sharing the ROM.

## Copyright and repository boundaries

The PP64 MP3 decompilation explicitly requires a user-supplied big-endian `baserom.u.z64`, says the ROM is not distributed, and describes rebuilding from that local input. That is the correct model for MPT as well.

Source: [PartyPlanner64/mp3 README](https://github.com/PartyPlanner64/mp3#readme).

MPT should commit only:

- original application code;
- original metadata, schemas, and validation signatures;
- user-created patch manifests and source where licensing permits;
- links and pinned upstream references;
- tests using synthetic/minimal byte arrays or user-local fixtures.

MPT should not commit:

- ROMs or ROM slices;
- generated patched ROMs;
- extracted Nintendo assets;
- opaque binary payloads copied from a ROM unless their provenance/license is clear.

## Concrete roadmap

1. Add a `RomIdentity` model with title, region, revision, byte order, header CRCs, and full-file hashes.
2. Add a read-only “inspect ROM” command/UI that reports why a ROM is or is not a supported target.
3. Define a versioned patch manifest with expected-before bytes, writes, postconditions, and provenance.
4. Import PP64 symbol files as optional debugger metadata, pinned by upstream commit.
5. Add a PP64-compatible MP1/2/3 validation profile using the three published MD5s.
6. Add a dry-run mode that shows every proposed write and rejects mismatched signatures.
7. Add output sidecars and emulator launch profiles requiring 8 MB RAM.
8. Add fixture tests with synthetic buffers and user-local ROM tests kept outside Git.
9. Only after the identity/manifest layer is stable, investigate a direct PP64 board artifact importer against a pinned upstream source commit.

## Primary sources

- [PartyPlanner64 main repository](https://github.com/PartyPlanner64/PartyPlanner64)
- [PartyPlanner64 README](https://github.com/PartyPlanner64/PartyPlanner64#readme)
- [PartyPlanner64 symbols](https://github.com/PartyPlanner64/symbols)
- [PartyPlanner64 events](https://github.com/PartyPlanner64/events)
- [PartyPlanner64 MP3 decompilation](https://github.com/PartyPlanner64/mp3)
- [Mario Party 1 splitter/layout configuration](https://gist.github.com/PartyPlanner64/93952bc7e1e403fda023d17ecb74bd2a)
