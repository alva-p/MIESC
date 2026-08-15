# Vyper-Real — Provenance & Ground Truth Methodology

Pilot corpus for the MEJORAS2.md backlog item "Vyper: profundizar contra auditorías
reales" — `miesc/adapters/vyper_adapter.py` (MEJORAS.md #6, PR #19) is pattern-based
and had never been validated against a real audited Vyper contract; only confirmed
not to crash. Same methodology as `../solodit-real/` (item #1/#2): real audited
contracts, real complete audit findings as ground truth, sourced via the Solodit MCP
server.

## Upstream source

| Protocol | Contest | Repo | Findings used |
|---|---|---|---|
| Fair Funding (Alchemix & Unstoppable) | Sherlock, 2023-02 | https://github.com/sherlock-audit/2023-02-fair-funding | 5 (H-1, H-2, M-1..M-3) |

Contracts are the official audit scope per the contest's own README:
`fair-funding/contracts/AuctionHouse.vy`, `fair-funding/contracts/Vault.vy` (both
Vyper 0.3.7), `fair-funding/contracts/solidity/MintableERC721.sol` (Solidity — kept
for corpus completeness, out of scope for the Vyper adapter itself).

Completeness verified before curation, same signal as `solodit-real`: finding IDs
are sequential with zero gaps (H-1, H-2, M-1, M-2, M-3 — exactly the 5
`search_findings(protocol="Fair Funding")` returned), a strong signal this is the
complete report, not a curated highlight reel.

## Ground truth methodology (`ground_truth.json`)

Same per-finding format as `solodit-real/ground_truth.json`: each of the 5
HIGH/MEDIUM findings, with its real file and a category assigned by hand from the
finding's actual title/description (not automated). No GAS/LOW findings existed in
this small report to exclude.

## Measured result (2026-08-15, pilot — 1 protocol, 2 Vyper files)

Ran `VyperAnalyzer` (the actual production adapter, not a synthetic fixture)
directly against `Vault.vy`/`AuctionHouse.vy` — `evaluate corpus` can't be used
here, its `run_layer()` path is Solidity-only (no `.vy` routing at all; a separate,
smaller gap worth knowing about, not fixed here) — and matched detected categories
against `ground_truth.json` the same way `_evaluate_contract` does.

| Contract | Ground truth | Detected | TP | FP | FN |
|---|---|---|---|---|---|
| `Vault.vy` | access_control, denial_of_service, business_logic | reentrancy, access_control | access_control | reentrancy | denial_of_service, business_logic |
| `AuctionHouse.vy` | time_manipulation | reentrancy, access_control | — | reentrancy, access_control | time_manipulation |

**Aggregate: TP=1, FP=3, FN=3 → precision 25%, recall 25%, F1 25%.**

The adapter's entire detector vocabulary (`VyperVulnerability` enum:
`broken_reentrancy_lock_compiler`, `missing_reentrancy_guard`,
`selfdestruct_usage`, `dangerous_delegatecall`, `unsafe_proxy_creation`,
`tx_origin_auth`, `missing_access_control`, `unsafe_arithmetic`) has **no detector
at all** for 3 of this real audit's 5 findings' categories (business_logic,
denial_of_service, time_manipulation) — recall on those is structurally 0%, not a
tuning problem. The 1 TP (`access_control` on `Vault.vy`, matching real finding
M-1 about `migrate()`) is a partial/coincidental hit: the adapter's
`missing_access_control` detector flagged the same function (line 546) for a
different reason than the real bug — it noted `migrate()` has no `msg.sender`
check, while the real M-1 issue is that `migrate()` doesn't grant the migrator
contract sufficient share permissions. Same location, different substance — real
credit for landing on the right function, not for identifying the actual bug.
The `reentrancy` FPs (both files, `missing_reentrancy_guard` on external-call
functions) were not independently verified against the real contract's actual
safety — could be genuine misses by the human auditors, or genuine noise; not
claimed as either without deeper review.

**Not a verdict on the adapter, a first real data point.** One protocol, 2 files,
5 ground-truth findings — same small-sample caveat every other pilot in this
project carries. Before deciding whether to invest in extending detector coverage
(business_logic/DoS/time_manipulation for Vyper) or accept the current scope,
more real Vyper audits should go through the same process — Solodit has 418
Vyper-tagged findings total, this pilot used exactly one small contest's worth.

## Licensing

Contracts retain their original project license (see the contest repo). No
additional license is asserted by MIESC over this third-party code; included
solely for benchmark reproducibility, same policy as `../smartbugs-curated/` and
`../solodit-real/`.
