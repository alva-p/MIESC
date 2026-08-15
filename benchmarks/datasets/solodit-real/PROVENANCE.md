# Solodit-Real — Provenance & Ground Truth Methodology

Pilot corpus for MEJORAS2.md items #1/#2: real audited contracts + real,
complete (not curated-subset) audit findings as ground truth, sourced via the
Solodit MCP server (`mcp__solodit__search_findings`/`get_finding`).

## Upstream sources

| Protocol | Contest | Repo | Findings used |
|---|---|---|---|
| NextGen | Code4rena, 2023-10 | https://github.com/code-423n4/2023-10-nextgen | 18 (H-01..H-05, M-01..M-12) |
| Y2K Finance | Code4rena, 2022-09 | https://github.com/code-423n4/2022-09-y2k-finance | 27 (H-01..H-09 minus H-07, M-01..M-16 minus M-09*) |

\* `rewards/StakingRewards.sol` (and its 3 findings: M-09, M-10 partially, M-15)
was removed from this pilot — the `peculiar` adapter hangs indefinitely on it
(confirmed twice, ignores `--timeout`). Logged as a new finding in
`MEJORAS2.md`, not fixed in this pass.

Contracts are the official **in-scope** files per each contest's own README
scope table (NextGen) or `src/` layout (Y2K Finance) — not the full repo, which
also includes tests, scripts, and vendored dependencies out of scope for the
audit itself.

## Ground truth methodology (`ground_truth.json`)

Unlike SmartBugs-curated (one category inferred from the containing folder,
per contract), this manifest lists **every individual HIGH/MEDIUM finding**
from each contest's full report, with its real file and a category assigned
by hand from the finding's actual title/description/PoC (not automated).
GAS and LOW findings are excluded (not security vulnerabilities in the sense
this benchmark measures). Completeness was verified before curation: both
contests' finding IDs are sequential with zero gaps (e.g. NextGen: H-01..H-05,
M-01..M-12, G-01..G-06 = exactly 23, matching the total `search_findings`
returned) — a strong signal each is the *complete* report, not a curated
highlight reel like the ground truth SmartBugs-curated (and, likely, EVMBench)
uses.

Categories include both the 10 classic `SMARTBUGS_CATEGORIES` (from
`miesc/cli/commands/evaluate.py`) and the 5 new `MODERN_CATEGORIES` added
alongside this corpus (`business_logic`, `oracle`, `rounding`,
`fee_on_transfer`, `erc4626`) — see MEJORAS2.md item #2 for why the classic
taxonomy (SmartBugs-curated is ~2018-2020 research) misses most of what
actually shows up in real 2022+ DeFi audits.

## Known limitation: Slither/Aderyn couldn't fully compile this corpus

MIESC's Slither/Aderyn adapters copy the single target file into an isolated
temp directory before invoking the compiler — they do not preserve sibling
files or `lib/`/remapping context. Every file in this corpus that imports
another project file (OpenZeppelin, Solmate, Chainlink, or even a sibling
interface in the same original repo) fails to compile for those two tools
specifically; other tools (pattern-based: fouranalyzer, smartbugs_detector,
peculiar, threat_model, gas_analyzer, etc.) are unaffected and still ran.
This is a real MIESC limitation surfaced by testing against genuine
multi-file audited code (SmartBugs-curated's single-file, dependency-free
contracts never exercise it) — logged as a new finding, not fixed here.

## Licensing

Contracts retain their original project licenses (see each contest repo).
No additional license is asserted by MIESC over this third-party code; it is
included solely for benchmark reproducibility, same policy as
`../smartbugs-curated/PROVENANCE.md`.

## Reproducing / extending

```bash
python -m miesc.cli.main evaluate corpus benchmarks/datasets/solodit-real \
    --layers 1,6,7 -o result.json
```

To add another protocol: pick one with a verifiably complete report
(sequential finding IDs, no gaps — check via
`mcp__solodit__search_findings(protocol=..., firms=[...])`), copy its
official in-scope files, and append entries to `ground_truth.json` with real
file/category per finding (see MEJORAS2.md item #1 for the full recipe).
