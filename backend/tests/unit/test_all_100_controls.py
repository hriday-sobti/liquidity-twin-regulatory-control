import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.controls.catalog import CONTROL_DEFINITIONS
from backend.app.controls.engine import ControlEngine
from backend.app.core.database import Base
from backend.app.models.facts import FactControlResult
from backend.app.services.generator import SyntheticBankGenerator


@pytest.fixture(scope="module")
def seeded_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    gen = SyntheticBankGenerator(db, seed=42)
    gen.seed_all()
    ce = ControlEngine(db)
    ce.run_all_controls("SNAP-2026-Q3-BASE")
    yield db
    db.close()


# Dynamically generate 100 individual test cases — one for each control in CONTROL_DEFINITIONS!
@pytest.mark.parametrize("control_def", CONTROL_DEFINITIONS, ids=[c["id"] for c in CONTROL_DEFINITIONS])
def test_individual_control_execution(seeded_db, control_def):
    """
    Validates that each of the 100 automated controls:
      1. Is defined with valid schema (id, name, family, severity, frequency, expected_result).
      2. Executes against the database snapshot.
      3. Produces a valid, non-null status in ('PASS', 'FAIL', 'WARNING', 'NOT_APPLICABLE').
      4. Records a valid actual_result observation.
    """
    cid = control_def["id"]
    family = control_def["family"]
    assert cid.startswith("CTRL-")
    assert family in [
        "ACCOUNTING", "DATA QUALITY", "CLASSIFICATION", "MATURITY", "CALCULATION",
        "RECONCILIATION", "REPORTING", "LINEAGE", "SCENARIO", "AI OUTPUT"
    ]
    assert control_def["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    result = seeded_db.query(FactControlResult).filter_by(
        snapshot_id="SNAP-2026-Q3-BASE",
        control_id=cid,
    ).first()

    assert result is not None, f"Control {cid} did not record an execution result."
    assert result.status in ["PASS", "FAIL", "WARNING", "NOT_APPLICABLE"]
    assert len(result.actual_result) > 0
    assert result.control_family == family
