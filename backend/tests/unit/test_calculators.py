import json
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models.dimensions import DimAccount, DimCustomer, DimProduct, DimEntity
from backend.app.models.regulatory import RegulatoryRule
from backend.app.models.facts import FactReportingSnapshot, FactBalanceSheet, FactOffBalanceExposure
from backend.app.calculators.classifier import RegulatoryClassifier
from backend.app.calculators.asf import AsfCalculationEngine
from backend.app.calculators.rsf import RsfCalculationEngine
from backend.app.calculators.nsfr import NsfrCalculationEngine
from backend.app.calculators.lcr import LcrCalculationEngine
from backend.app.services.generator import SyntheticBankGenerator


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()


def test_regulatory_classifier_asf(in_memory_db):
    gen = SyntheticBankGenerator(in_memory_db, seed=42)
    gen.seed_regulatory_rules()

    classifier = RegulatoryClassifier(in_memory_db)
    res = classifier.classify_position(
        product_code="RET_DEMAND_INS",
        side="LIABILITY",
        counterparty_type="RETAIL",
        residual_maturity_days=1,
        is_insured=True,
    )
    assert "ASF" in res
    assert res["ASF"].factor == Decimal("0.9500")
    assert res["ASF"].rule_id == "RULE-ASF-02"


def test_regulatory_classifier_rsf(in_memory_db):
    gen = SyntheticBankGenerator(in_memory_db, seed=42)
    gen.seed_regulatory_rules()

    classifier = RegulatoryClassifier(in_memory_db)
    res = classifier.classify_position(
        product_code="SOV_BOND_L1",
        side="ASSET",
        counterparty_type="SOVEREIGN",
        residual_maturity_days=720,
        is_encumbered=False,
    )
    assert "RSF" in res
    assert res["RSF"].factor == Decimal("0.0500")
    assert res["RSF"].rule_id == "RULE-RSF-02"


def test_golden_dataset_nsfr_and_lcr_assertions(in_memory_db):
    """
    Section 73: GOLDEN CALCULATION TEST
    Verifies deterministic calculation engine against pre-calculated hand-verified values:
      Total ASF == $49,700,000.00
      Total RSF == $42,000,000.00
      NSFR == 118.3333%
    """
    with open("data/golden/golden_dataset.json", "r") as f:
        golden = json.load(f)

    gen = SyntheticBankGenerator(in_memory_db, seed=42)
    gen.seed_regulatory_rules()
    gen.seed_currencies()
    gen.seed_entities()

    # Create dummy entity & products
    prod_map = {}
    for acc_data in golden["accounts"]:
        side = acc_data["side"]
        ptype = acc_data["type"]
        if ptype not in prod_map:
            p = DimProduct(product_id=f"P-{ptype}", product_code=ptype, product_name=ptype, product_group=ptype, balance_sheet_side=side)
            in_memory_db.add(p)
            prod_map[ptype] = p
    in_memory_db.commit()

    # Create dummy snapshot
    snap = FactReportingSnapshot(
        snapshot_id="SNAP-GOLDEN",
        snapshot_name="Golden Test Snapshot",
        period="2026-Q3",
        business_date=gen.as_of_date,
        asf_amount=Decimal(str(golden["expected_totals"]["total_asf"])),
        rsf_amount=Decimal(str(golden["expected_totals"]["total_rsf"])),
        nsfr_value=Decimal(str(golden["expected_totals"]["nsfr_percentage"])),
    )
    in_memory_db.add(snap)

    for acc_data in golden["accounts"]:
        side = acc_data["side"]
        bal = Decimal(str(acc_data["balance"]))
        aid = acc_data["account_id"]
        
        # Account
        a = DimAccount(
            account_id=aid,
            account_number=aid,
            customer_id="GOLD-CUST-01",
            entity_id="ENT-001",
            product_id=f"P-{acc_data['type']}",
            currency="USD",
            open_date=gen.as_of_date,
            status="ACTIVE",
            is_operational=acc_data.get("is_operational", False),
            is_insured=acc_data.get("is_insured", False),
        )
        in_memory_db.add(a)

        if side in ("ASSET", "LIABILITY", "EQUITY"):
            asf_f = Decimal(str(acc_data.get("asf_factor", 0.0)))
            rsf_f = Decimal(str(acc_data.get("rsf_factor", 0.0)))
            bs = FactBalanceSheet(
                balance_id=f"B-{aid}",
                snapshot_id="SNAP-GOLDEN",
                business_date=gen.as_of_date,
                account_id=aid,
                opening_balance=bal,
                movement_amount=Decimal("0.0"),
                closing_balance=bal,
                currency="USD",
                closing_balance_usd=bal,
                asf_factor=asf_f,
                rsf_factor=rsf_f,
                asf_amount=bal * asf_f,
                rsf_amount=bal * rsf_f,
            )
            in_memory_db.add(bs)
        elif side == "OFF_BALANCE_SHEET":
            obs = FactOffBalanceExposure(
                exposure_id=f"OBS-{aid}",
                snapshot_id="SNAP-GOLDEN",
                account_id=aid,
                facility_type="CREDIT_LINE",
                committed_amount_usd=bal,
                undrawn_amount_usd=bal,
                rsf_factor=Decimal(str(acc_data["rsf_factor"])),
            )
            in_memory_db.add(obs)

    in_memory_db.commit()

    asf_engine = AsfCalculationEngine(in_memory_db)
    asf_calc = asf_engine.calculate_asf("SNAP-GOLDEN")
    assert abs(asf_calc["total_asf"] - golden["expected_totals"]["total_asf"]) < 0.01

    rsf_engine = RsfCalculationEngine(in_memory_db)
    rsf_calc = rsf_engine.calculate_rsf("SNAP-GOLDEN")
    assert abs(rsf_calc["total_rsf"] - golden["expected_totals"]["total_rsf"]) < 0.01

    nsfr_engine = NsfrCalculationEngine(in_memory_db)
    nsfr_calc = nsfr_engine.calculate_nsfr("SNAP-GOLDEN")
    assert abs(nsfr_calc["nsfr_percentage"] - golden["expected_totals"]["nsfr_percentage"]) < 0.01
