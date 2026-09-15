# Mario Party code catalog research

Research date: 2026-09-15

The import contains 38 executable candidates in
[`data/web-code-candidates.jsonl`](../../data/web-code-candidates.jsonl), with
the normalized database in
[`data/normalized-web-codes.json`](../../data/normalized-web-codes.json).
Every record includes a description, author, platform code family, region,
revision/serial, source URL, evidence, and confidence.

## Version matrix

| Game | Imported version | Family | Candidates |
| --- | --- | --- | ---: |
| Mario Party 1 | USA `CLBE` | GameShark | 5 |
| Mario Party 2 | USA `NMWE` | GameShark | 2 |
| Mario Party 3 | — | — | 0 executable candidates from the reviewed pages |
| Mario Party 4 | USA v1.00 `GMPE01` | Gecko | 8 |
| Mario Party 5 | USA `GP5E01` | Gecko | 3 exact profile codes |
| Mario Party 6 | USA `GP6E01` | Gecko | 7 |
| Mario Party 7 | USA `GP7E01` | — | 0 executable candidates; reviewed entries were ARMax or wildcard templates |
| Mario Party 8 | USA `RM8E01` | Gecko | 2 |
| Mario Party 9 | USA `SSQE01` | Gecko | 11 |

PartyPlanner64 identifies the supported N64 USA ROMs and their hashes, while
its symbols repository provides region-specific Mario Party 1–3 address
references: [PartyPlanner64](https://github.com/PartyPlanner64/PartyPlanner64),
[symbols](https://github.com/PartyPlanner64/symbols). Its README states that
the editor supports NTSC USA files, including MP1–3, and requires 8 MB RAM in
the emulator.

The imported N64 entries come from the version-labeled Mario Party pages for
[MP1](https://gamehacking.org/game/20602),
[MP2](https://gamehacking.org/game/20605), and
[MP3](https://gamehacking.org/game/20608). The MP2 page explicitly notes that
its code set requires a version 3.0+ cheat device.

The GameCube/Wii entries come from the USA version pages for
[MP4 v1.00](https://gamehacking.org/game/54720),
[MP5](https://gamehacking.org/game/54644),
[MP6 Gecko format](https://gamehacking.org/?format=gko&game=54645&hacker=all),
[MP8](https://gamehacking.org/game/132990), and
[MP9](https://gamehacking.org/game/116316). MP8's address correction and
controller conditions are cross-checked against the
[WiiRD RM8E01 thread](https://wiird.gamehacking.org/forum/index.php?topic=1463.0).

## Selection rules

- Included only complete hexadecimal code lines accepted by the existing
  normalizer.
- Kept source version/serial with each record; no cross-version address
  inference was performed.
- Excluded ARMax-only codes because the current runners accept GameShark or
  Gecko text, not ARMax encodings.
- Excluded wildcard/template codes such as `00??`, `00000XXX`, and
  `????????`; these need a value-selection UI or deterministic expansion
  before they can enter the executable test queue.
- Descriptions are source-name-grounded summaries. They are not proof that a
  code works; the phase-3/4 runner contract still requires emulator load/boot
  evidence and manual or oracle-based behavioral confirmation.

Local-LLM assistance: Devstral drafted concise descriptions from the sourced
names. Ling-family batch review supplied risk/test hints. Code text, version
metadata, source evidence, filtering, and normalization were checked
deterministically.
