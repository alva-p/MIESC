import json

from miesc.cli.commands.evaluate import _load_ground_truth, _normalize_category


def test_smartbugs_access_control_aliases_from_intelligence_patterns():
    assert _normalize_category("incorrect_constructor_name") == "access_control"
    assert _normalize_category("delegatecall_unprotected") == "access_control"
    assert _normalize_category("delegatecall_to_untrusted") == "access_control"
    assert _normalize_category("mapping_write_arbitrary") == "access_control"
    assert _normalize_category("constructor_mismatch") == "access_control"
    assert _normalize_category("withdraw_no_balance_update") == "access_control"
    assert _normalize_category("confused_comparison") == "access_control"


class TestModernCategories:
    """MEJORAS2.md #2 — categories real 2022+ DeFi audits actually report,
    absent from SmartBugs-curated's ~2018-2020 taxonomy."""

    def test_oracle_alias_and_keyword_fallback(self):
        assert _normalize_category("oracle_manipulation") == "oracle"
        assert _normalize_category("finding", description="stale price feed") == "oracle"

    def test_rounding_alias_and_keyword_fallback(self):
        assert _normalize_category("loss_of_precision") == "rounding"
        assert _normalize_category("finding", description="loss of precision") == "rounding"

    def test_business_logic_keyword_fallback(self):
        assert _normalize_category("finding", description="breaks a core invariant") == "business_logic"

    def test_fee_on_transfer_alias(self):
        assert _normalize_category("fee_on_transfer") == "fee_on_transfer"

    def test_erc4626_alias(self):
        assert _normalize_category("erc4626") == "erc4626"

    def test_classic_category_not_shadowed_by_new_keywords(self):
        # "timestamp" must still resolve to the classic category, not get
        # reclassified by the newer oracle/rounding keyword fallbacks.
        assert _normalize_category("finding", description="block.timestamp dependence") == "time_manipulation"


class TestGroundTruthJsonManifest:
    """MEJORAS2.md #1 — Solodit-sourced per-finding ground truth, an
    alternative to SmartBugs-curated's one-category-per-folder inference."""

    def test_loads_and_aggregates_categories_per_file(self, tmp_path):
        (tmp_path / "Vault.sol").write_text("contract Vault {}")
        (tmp_path / "ground_truth.json").write_text(
            json.dumps(
                {
                    "findings": [
                        {"file": "Vault.sol", "category": "oracle"},
                        {"file": "Vault.sol", "category": "rounding"},
                    ]
                }
            )
        )

        gt = _load_ground_truth(tmp_path)

        assert gt == {"Vault.sol": {"oracle", "rounding"}}

    def test_skips_findings_whose_file_does_not_exist(self, tmp_path):
        (tmp_path / "ground_truth.json").write_text(
            json.dumps({"findings": [{"file": "Missing.sol", "category": "oracle"}]})
        )

        gt = _load_ground_truth(tmp_path)

        assert gt == {}

    def test_manifest_takes_precedence_over_folder_structure(self, tmp_path):
        # A folder named "reentrancy" would normally be read as SmartBugs-style
        # ground truth — the manifest, when present, wins instead.
        (tmp_path / "reentrancy").mkdir()
        (tmp_path / "reentrancy" / "C.sol").write_text("contract C {}")
        (tmp_path / "ground_truth.json").write_text(
            json.dumps({"findings": [{"file": "reentrancy/C.sol", "category": "oracle"}]})
        )

        gt = _load_ground_truth(tmp_path)

        assert gt == {"reentrancy/C.sol": {"oracle"}}
