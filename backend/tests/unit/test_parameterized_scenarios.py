
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.copilot.verifier import NumericVerifier
from backend.app.core.database import Base
from backend.app.scenarios.engine import ScenarioLabEngine
from backend.app.services.generator import SyntheticBankGenerator


@pytest.fixture(scope="module")
def stress_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    gen = SyntheticBankGenerator(db, seed=42)
    snap = gen.seed_all()
    yield db, snap.snapshot_id
    db.close()


# Parametrize 20 discrete corporate deposit outflow shock tiers (-1% to -20%)
@pytest.mark.parametrize("shock_pct", [-1.0 * i for i in range(1, 21)])
def test_scenario_corporate_deposit_shocks_monotonic(stress_db, shock_pct):
    db, snap_id = stress_db
    lab = ScenarioLabEngine(db)
    res = lab.run_scenario(snap_id, f"Stress Test {shock_pct}%", corporate_deposit_pct=shock_pct)
    # Stressed NSFR must be strictly less than base NSFR (117.64%)
    assert res["metrics"]["NSFR"]["scenario"] < res["metrics"]["NSFR"]["base"]
    assert res["metrics"]["NSFR"]["delta_pp"] < 0


# Parametrize 15 discrete loan growth expansion tiers (+1% to +15%)
@pytest.mark.parametrize("growth_pct", [1.0 * i for i in range(1, 16)])
def test_scenario_loan_growth_shocks_rsf_expansion(stress_db, growth_pct):
    db, snap_id = stress_db
    lab = ScenarioLabEngine(db)
    res = lab.run_scenario(snap_id, f"Loan Growth +{growth_pct}%", loan_growth_pct=growth_pct)
    assert res["metrics"]["NSFR"]["stressed_rsf_usd"] > res["metrics"]["NSFR"]["base_rsf_usd"]


# Parametrize 10 term funding injection tiers ($10M to $100M)
@pytest.mark.parametrize("funding_m", [10.0 * i for i in range(1, 11)])
def test_scenario_term_funding_injections_asf_increase(stress_db, funding_m):
    db, snap_id = stress_db
    lab = ScenarioLabEngine(db)
    res = lab.run_scenario(snap_id, f"Funding +${funding_m}M", new_term_funding_usd=funding_m * 1e6)
    assert res["metrics"]["NSFR"]["stressed_asf_usd"] > res["metrics"]["NSFR"]["base_asf_usd"]
    assert res["metrics"]["NSFR"]["scenario"] > res["metrics"]["NSFR"]["base"]


# Parametrize 10 asset reallocation tiers ($5M to $50M)
@pytest.mark.parametrize("realloc_m", [5.0 * i for i in range(1, 11)])
def test_scenario_asset_reallocation_rsf_impact(stress_db, realloc_m):
    db, snap_id = stress_db
    lab = ScenarioLabEngine(db)
    res = lab.run_scenario(snap_id, f"Reallocate ${realloc_m}M", asset_reallocation_usd=realloc_m * 1e6)
    # Selling Level 1 bonds (5% RSF) to buy commercial loans (85% RSF) increases total RSF
    assert res["metrics"]["NSFR"]["stressed_rsf_usd"] > res["metrics"]["NSFR"]["base_rsf_usd"]


# Parametrize 8 adversarial numeric verifier test cases
@pytest.mark.parametrize("fake_nsfr", [119.6, 122.5, 130.0, 99.5, 145.2, 110.0, 150.0, 85.0])
def test_verifier_blocks_arbitrary_unverified_percentages(fake_nsfr):
    verifier = NumericVerifier()
    grounding = {"current_nsfr_percentage": 117.64, "total_movement_pp": 0.63, "largest_driver": "Corporate Deposits"}
    text = f"Reported NSFR for this quarter is {fake_nsfr:.2f}%."
    passed, violations, status = verifier.verify_narrative(text, grounding)
    assert passed is False
    assert status == "BLOCKED_NUMERIC_MISMATCH"
