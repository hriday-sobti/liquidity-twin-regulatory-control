import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models import *
from backend.app.services.generator import SyntheticBankGenerator
from backend.app.services.accounting import AccountingRollupService
from backend.app.calculators.classifier import RegulatoryClassifier
from backend.app.calculators.asf import AsfCalculationEngine
from backend.app.calculators.rsf import RsfCalculationEngine
from backend.app.calculators.nsfr import NsfrCalculationEngine
from backend.app.calculators.lcr import LcrCalculationEngine
from backend.app.scenarios.movement import MovementAnalyzer
from backend.app.scenarios.engine import ScenarioLabEngine
from backend.app.lineage.builder import LineageGraphBuilder
from backend.app.services.close_workflow import ShadowCloseWorkflowEngine
from backend.app.services.query_workbench import StakeholderQueryWorkbench
from backend.app.services.event_replay import EventReplayService
from backend.app.copilot.engine import CopilotEngine
from backend.app.copilot.verifier import NumericVerifier
from backend.app.copilot.red_team import RedTeamRunner
from backend.app.reporting.compiler import ReportingCompiler


@pytest.fixture(scope="module")
def shared_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    gen = SyntheticBankGenerator(db, seed=42)
    snap = gen.seed_all()
    yield db, snap.snapshot_id
    db.close()


# =============================================================================
# 1. ACCOUNTING INVARIANTS & RECONCILIATION TESTS (10 TESTS)
# =============================================================================
def test_accounting_balance_sheet_identity_exact(shared_db):
    db, snap_id = shared_db
    svc = AccountingRollupService(db)
    res = svc.verify_balance_sheet_identity(snap_id)
    assert res["is_balanced"] is True
    assert res["variance"] == 0.0
    assert res["total_assets"] == 1050000000.0
    assert res["total_liabilities_and_equity"] == 1050000000.0


def test_accounting_roll_forward_zero_breaks(shared_db):
    db, snap_id = shared_db
    svc = AccountingRollupService(db)
    passed, breaks = svc.verify_roll_forward(snap_id)
    assert passed is True
    assert len(breaks) == 0


def test_gl_reconciliation_status(shared_db):
    db, snap_id = shared_db
    svc = AccountingRollupService(db)
    res = svc.reconcile_gl_to_subledger(snap_id)
    assert res["reconciliation_status"] == "MATCHED"
    assert res["reconciliation_variance"] == 0.0


def test_currency_master_completeness(shared_db):
    db, _ = shared_db
    currencies = db.query(DimCurrency).all()
    codes = [c.currency_code for c in currencies]
    for expected in ["USD", "EUR", "GBP", "SGD", "INR"]:
        assert expected in codes


def test_fx_rate_positive(shared_db):
    db, _ = shared_db
    currencies = db.query(DimCurrency).all()
    for c in currencies:
        assert c.fx_rate_to_usd > Decimal("0.0")


def test_entity_master_jurisdictions(shared_db):
    db, _ = shared_db
    entities = db.query(DimEntity).all()
    assert len(entities) >= 3
    codes = [e.entity_code for e in entities]
    assert "SYN-BANK-US" in codes


def test_product_master_balance_sheet_sides(shared_db):
    db, _ = shared_db
    products = db.query(DimProduct).all()
    for p in products:
        assert p.balance_sheet_side in ["ASSET", "LIABILITY", "EQUITY", "OFF_BALANCE_SHEET"]


def test_security_master_hqla_tiers(shared_db):
    db, _ = shared_db
    securities = db.query(DimSecurity).all()
    assert len(securities) >= 5
    for s in securities:
        assert s.hqla_tier in ["LEVEL_1", "LEVEL_2A", "LEVEL_2B", "NON_HQLA"]
        assert Decimal("0.0") <= s.haircut <= Decimal("1.0")


def test_account_master_validity(shared_db):
    db, _ = shared_db
    accounts = db.query(DimAccount).all()
    assert len(accounts) >= 20
    for a in accounts:
        assert a.status == "ACTIVE"
        assert a.currency == "USD"


def test_event_log_positive_amounts(shared_db):
    db, _ = shared_db
    events = db.query(FactEvent).limit(100).all()
    assert len(events) > 0
    for ev in events:
        assert ev.amount > Decimal("0.0")
        assert ev.currency == "USD"


# =============================================================================
# 2. REGULATORY CLASSIFICATION TESTS (8 TESTS)
# =============================================================================
def test_classifier_capital_100_percent(shared_db):
    db, _ = shared_db
    classifier = RegulatoryClassifier(db)
    res = classifier.classify_position("EQUITY_CET1", "EQUITY", "SOVEREIGN", 9999)
    assert res["ASF"].factor == Decimal("1.0000")


def test_classifier_less_stable_retail_90_percent(shared_db):
    db, _ = shared_db
    classifier = RegulatoryClassifier(db)
    res = classifier.classify_position("RET_DEMAND_UNINS", "LIABILITY", "RETAIL", 1, is_insured=False)
    assert res["ASF"].factor == Decimal("0.9000")


def test_classifier_corp_operational_50_percent(shared_db):
    db, _ = shared_db
    classifier = RegulatoryClassifier(db)
    res = classifier.classify_position("CORP_OPERATIONAL", "LIABILITY", "NON_FINANCIAL_CORPORATE", 30, is_operational=True)
    assert res["ASF"].factor == Decimal("0.5000")


def test_classifier_wholesale_short_0_percent(shared_db):
    db, _ = shared_db
    classifier = RegulatoryClassifier(db)
    res = classifier.classify_position("INTERBANK_BORROW", "LIABILITY", "FINANCIAL_INSTITUTION", 20)
    assert res["ASF"].factor == Decimal("0.0000")


def test_classifier_cash_rsf_0_percent(shared_db):
    db, _ = shared_db
    classifier = RegulatoryClassifier(db)
    res = classifier.classify_position("CASH_RESERVES", "ASSET", "CENTRAL_BANK", 1)
    assert res["RSF"].factor == Decimal("0.0000")


def test_classifier_corp_bond_l2a_15_percent(shared_db):
    db, _ = shared_db
    classifier = RegulatoryClassifier(db)
    res = classifier.classify_position("CORP_BOND_L2A", "ASSET", "CORPORATE", 1095)
    assert res["RSF"].factor == Decimal("0.1500")


def test_classifier_standard_corp_loan_85_percent(shared_db):
    db, _ = shared_db
    classifier = RegulatoryClassifier(db)
    res = classifier.classify_position("CORP_LONG_STD_RW", "ASSET", "NON_FINANCIAL_CORPORATE", 1460)
    assert res["RSF"].factor == Decimal("0.8500")


def test_classifier_committed_credit_obs_5_percent(shared_db):
    db, _ = shared_db
    classifier = RegulatoryClassifier(db)
    res = classifier.classify_position("COMMITTED_CREDIT", "OFF_BALANCE_SHEET", "NON_FINANCIAL_CORPORATE", 365)
    assert res["RSF"].factor == Decimal("0.0500")


# =============================================================================
# 3. NSFR & LCR CALCULATION ENGINE TESTS (8 TESTS)
# =============================================================================
def test_asf_total_accuracy(shared_db):
    db, snap_id = shared_db
    engine = AsfCalculationEngine(db)
    res = engine.calculate_asf(snap_id)
    assert res["total_asf"] == 842300000.0


def test_rsf_total_accuracy(shared_db):
    db, snap_id = shared_db
    engine = RsfCalculationEngine(db)
    res = engine.calculate_rsf(snap_id)
    assert abs(res["total_rsf"] - 716000000.0) < 10.0


def test_nsfr_ratio_baseline_target(shared_db):
    db, snap_id = shared_db
    engine = NsfrCalculationEngine(db)
    res = engine.calculate_nsfr(snap_id)
    assert abs(res["nsfr_percentage"] - 117.64) < 0.2
    assert res["is_compliant"] is True
    assert res["buffer_percentage"] > 0


def test_hqla_buffer_calculation(shared_db):
    db, snap_id = shared_db
    engine = LcrCalculationEngine(db)
    res = engine.calculate_lcr(snap_id)
    assert res["total_hqla"] == 219000000.0
    assert res["level1_hqla"] == 185000000.0
    assert res["level2a_hqla"] == 34000000.0


def test_lcr_ratio_baseline_target(shared_db):
    db, snap_id = shared_db
    engine = LcrCalculationEngine(db)
    res = engine.calculate_lcr(snap_id)
    assert abs(res["lcr_percentage"] - 132.49) < 0.5
    assert res["is_compliant"] is True
    assert res["eligible_inflows"] <= res["inflow_cap_limit"]


def test_lcr_inflow_75_percent_cap_enforcement(shared_db):
    db, snap_id = shared_db
    engine = LcrCalculationEngine(db)
    res = engine.calculate_lcr(snap_id)
    assert res["eligible_inflows"] <= 0.75 * res["gross_cash_outflows"]


def test_asf_category_percentages_sum_to_100(shared_db):
    db, snap_id = shared_db
    engine = AsfCalculationEngine(db)
    res = engine.calculate_asf(snap_id)
    pct_sum = sum(c["percentage_of_total_asf"] for c in res["categories"])
    assert abs(pct_sum - 100.0) < 0.01


def test_rsf_category_percentages_sum_to_100(shared_db):
    db, snap_id = shared_db
    engine = RsfCalculationEngine(db)
    res = engine.calculate_rsf(snap_id)
    pct_sum = sum(c["percentage_of_total_rsf"] for c in res["categories"])
    assert abs(pct_sum - 100.0) < 0.01


# =============================================================================
# 4. LINEAGE GRAPH & BLAST RADIUS TESTS (8 TESTS)
# =============================================================================
def test_lineage_graph_dag_acyclicity(shared_db):
    db, snap_id = shared_db
    builder = LineageGraphBuilder(db)
    graph = builder.build_lineage_graph(snap_id, persist=False)
    import networkx as nx
    assert nx.is_directed_acyclic_graph(graph) is True


def test_lineage_metric_birth_certificate_structure(shared_db):
    db, snap_id = shared_db
    builder = LineageGraphBuilder(db)
    cert = builder.get_metric_birth_certificate(snap_id, "NSFR")
    assert cert["metric_name"] == "NSFR"
    assert cert["node_count"] > 20
    assert cert["is_acyclic"] is True


def test_lineage_birth_certificate_contains_rules(shared_db):
    db, snap_id = shared_db
    builder = LineageGraphBuilder(db)
    cert = builder.get_metric_birth_certificate(snap_id, "NSFR")
    types = [n["type"] for n in cert["nodes"]]
    assert "RULE" in types
    assert "ACCOUNTING_POSITION" in types
    assert "ASF_CONTRIBUTION" in types


def test_lineage_blast_radius_failed_control(shared_db):
    db, snap_id = shared_db
    builder = LineageGraphBuilder(db)
    blast = builder.get_control_blast_radius(snap_id, "CTRL-REC-007")
    assert blast["control_id"] == "CTRL-REC-007"
    assert blast["estimated_monetary_exposure_usd"] == 1200000.0
    assert blast["impact_classification"] == "DIRECT"


def test_lineage_blast_radius_reports_impacted(shared_db):
    db, snap_id = shared_db
    builder = LineageGraphBuilder(db)
    blast = builder.get_control_blast_radius(snap_id, "CTRL-REC-007")
    assert len(blast["affected_reports"]) > 0


def test_lineage_node_types_invariance(shared_db):
    db, snap_id = shared_db
    builder = LineageGraphBuilder(db)
    graph = builder.build_lineage_graph(snap_id, persist=False)
    valid_types = {
        "SOURCE_RECORD", "ACCOUNTING_POSITION", "REGULATORY_CATEGORY", "RULE",
        "ASF_CONTRIBUTION", "RSF_CONTRIBUTION", "METRIC", "CONTROL", "REPORT_LINE", "EXCEPTION"
    }
    for _, data in graph.nodes(data=True):
        assert data.get("type") in valid_types


def test_lineage_metric_has_incoming_contributions(shared_db):
    db, snap_id = shared_db
    builder = LineageGraphBuilder(db)
    graph = builder.build_lineage_graph(snap_id, persist=False)
    in_edges = list(graph.in_edges(f"METRIC-NSFR-{snap_id}"))
    assert len(in_edges) >= 2


def test_lineage_report_line_outgoing_terminal(shared_db):
    db, snap_id = shared_db
    builder = LineageGraphBuilder(db)
    graph = builder.build_lineage_graph(snap_id, persist=False)
    out_edges = list(graph.out_edges(f"REP-LINE-EXEC-1.1-{snap_id}"))
    assert len(out_edges) == 0  # Terminal node in reporting DAG


# =============================================================================
# 5. MOVEMENT ATTRIBUTION & SCENARIO LAB TESTS (8 TESTS)
# =============================================================================
def test_movement_attribution_exact_sum(shared_db):
    db, snap_id = shared_db
    analyzer = MovementAnalyzer(db)
    mov = analyzer.analyze_movement(snap_id)
    delta = Decimal(str(mov["total_movement_pp"]))
    sum_contrib = sum(Decimal(str(d["contribution_pp"])) for d in mov["drivers"])
    assert abs(delta - sum_contrib) < Decimal("0.0001")


def test_movement_primary_driver_identified(shared_db):
    db, snap_id = shared_db
    analyzer = MovementAnalyzer(db)
    mov = analyzer.analyze_movement(snap_id)
    assert mov["largest_driver"] == "Corporate Deposits"


def test_scenario_corporate_outflow_8_percent_nsfr(shared_db):
    db, snap_id = shared_db
    lab = ScenarioLabEngine(db)
    scn = lab.run_scenario(snap_id, "Test -8%", corporate_deposit_pct=-8.0)
    assert abs(scn["metrics"]["NSFR"]["scenario"] - 113.1) < 0.2
    assert scn["metrics"]["NSFR"]["delta_pp"] < 0


def test_scenario_loan_growth_rsf_expansion(shared_db):
    db, snap_id = shared_db
    lab = ScenarioLabEngine(db)
    scn = lab.run_scenario(snap_id, "Test Loan Growth +5%", loan_growth_pct=5.0)
    assert scn["metrics"]["NSFR"]["stressed_rsf_usd"] > scn["metrics"]["NSFR"]["base_rsf_usd"]
    assert scn["metrics"]["NSFR"]["delta_pp"] < 0  # NSFR falls when RSF expands


def test_scenario_term_funding_injection_asf_increase(shared_db):
    db, snap_id = shared_db
    lab = ScenarioLabEngine(db)
    scn = lab.run_scenario(snap_id, "Test Funding +$50M", new_term_funding_usd=50000000.0)
    assert scn["metrics"]["NSFR"]["stressed_asf_usd"] > scn["metrics"]["NSFR"]["base_asf_usd"]
    assert scn["metrics"]["NSFR"]["delta_pp"] > 0  # NSFR rises when ASF increases


def test_scenario_baseline_immutability(shared_db):
    db, snap_id = shared_db
    snap_before = db.query(FactReportingSnapshot).filter_by(snapshot_id=snap_id).first()
    nsfr_before = snap_before.nsfr_value
    
    lab = ScenarioLabEngine(db)
    lab.run_scenario(snap_id, "Immutability Test", corporate_deposit_pct=-15.0)

    snap_after = db.query(FactReportingSnapshot).filter_by(snapshot_id=snap_id).first()
    assert snap_after.nsfr_value == nsfr_before  # Baseline never mutated


def test_scenario_combined_stress(shared_db):
    db, snap_id = shared_db
    lab = ScenarioLabEngine(db)
    scn = lab.run_scenario(
        snap_id,
        "Combined Stress",
        corporate_deposit_pct=-10.0,
        retail_deposit_pct=-5.0,
        loan_growth_pct=10.0,
    )
    assert scn["metrics"]["NSFR"]["scenario"] < scn["metrics"]["NSFR"]["base"]
    assert scn["metrics"]["LCR"]["scenario"] < scn["metrics"]["LCR"]["base"]


def test_scenario_record_persistence(shared_db):
    db, snap_id = shared_db
    lab = ScenarioLabEngine(db)
    scn = lab.run_scenario(snap_id, "Persistence Test", corporate_deposit_pct=-5.0)
    scn_row = db.query(FactScenario).filter_by(scenario_id=scn["scenario_id"]).first()
    assert scn_row is not None
    assert "corporate_deposit_pct" in scn_row.parameters_json


# =============================================================================
# 6. SHADOW CLOSE & LATE ADJUSTMENTS (5 TESTS)
# =============================================================================
def test_close_workflow_10_stages_exist(shared_db):
    db, _ = shared_db
    engine = ShadowCloseWorkflowEngine(db)
    status = engine.get_close_status("2026-Q3")
    assert len(status["steps"]) == 10
    step_names = [s["step_name"] for s in status["steps"]]
    assert "Freeze source data" in step_names
    assert "Reviewer sign-off" in step_names


def test_close_workflow_advance_step(shared_db):
    db, _ = shared_db
    engine = ShadowCloseWorkflowEngine(db)
    status = engine.advance_step("2026-Q3", 1, actor_role="Controller")
    assert status["steps"][0]["status"] == "COMPLETED"


def test_late_adjustment_38m_break_detection(shared_db):
    db, snap_id = shared_db
    engine = ShadowCloseWorkflowEngine(db)
    res = engine.inject_late_adjustment(
        snapshot_id=snap_id,
        account_id="ACC-CORP_NON_OPERATIONAL",
        adjustment_amount_usd=38000000.0,
    )
    assert res["amount_usd"] == 38000000.0
    assert "Stages 5 through 10 marked BLOCKED" in res["impacted_steps"]
    assert res["report_regeneration_required"] is True


def test_late_adjustment_exception_opened(shared_db):
    db, snap_id = shared_db
    exc = db.query(FactException).filter_by(snapshot_id=snap_id, control_id="CTRL-REC-008").first()
    assert exc is not None
    assert exc.severity == "CRITICAL"


def test_late_adjustment_event_logged(shared_db):
    db, _ = shared_db
    adj = db.query(AdjustmentEvent).filter_by(account_id="ACC-CORP_NON_OPERATIONAL").first()
    assert adj is not None
    assert adj.adjustment_type == "LATE_FUNDING"

    # Restore baseline snapshot so downstream red-team test uses pristine 117.64% baseline
    gen = SyntheticBankGenerator(db, seed=42)
    gen.seed_all()
# =============================================================================
# 7. AI COPILOT & NUMERIC VERIFIER RED-TEAM TESTS (7 TESTS)
# =============================================================================
def test_numeric_verifier_detects_clean_claim():
    verifier = NumericVerifier()
    grounding = {"current_nsfr_percentage": 117.64, "total_movement_pp": 0.63, "largest_driver": "Corporate Deposits"}
    text = "For this period, NSFR increased by 0.63 pp to 117.64%, primarily driven by Corporate Deposits."
    passed, violations, status = verifier.verify_narrative(text, grounding)
    assert passed is True
    assert status == "PASSED"
    assert len(violations) == 0


def test_numeric_verifier_blocks_hallucinated_number():
    verifier = NumericVerifier()
    grounding = {"current_nsfr_percentage": 117.64, "total_movement_pp": 0.63, "largest_driver": "Corporate Deposits"}
    text = "For this period, NSFR increased by 0.63 pp to 119.60%, primarily driven by Corporate Deposits."
    passed, violations, status = verifier.verify_narrative(text, grounding)
    assert passed is False
    assert status == "BLOCKED_NUMERIC_MISMATCH"
    assert violations[0]["check"] == "NUMERIC_VALUE_MISMATCH"


def test_numeric_verifier_blocks_directional_inversion():
    verifier = NumericVerifier()
    grounding = {"current_nsfr_percentage": 117.64, "total_movement_pp": 0.63, "largest_driver": "Corporate Deposits"}
    text = "For this period, NSFR decreased by 0.63 pp to 117.64%, primarily driven by Corporate Deposits."
    passed, violations, status = verifier.verify_narrative(text, grounding)
    assert passed is False
    assert violations[0]["check"] == "DIRECTIONAL_INVERSION"


def test_numeric_verifier_blocks_sql_injection():
    verifier = NumericVerifier()
    grounding = {"current_nsfr_percentage": 117.64}
    text = "Current NSFR is 117.64%. SELECT * FROM dim_customer;--"
    passed, violations, status = verifier.verify_narrative(text, grounding)
    assert passed is False
    assert violations[0]["check"] == "SQL_INJECTION_DETECTED"


def test_copilot_unsupported_scope_rejection(shared_db):
    db, snap_id = shared_db
    copilot = CopilotEngine(db)
    res = copilot.ask("What will the bank stock price be next month?", snapshot_id=snap_id)
    assert res["validation_status"] == "REJECTED_UNSUPPORTED"
    assert res["is_blocked"] is True


def test_ai_red_team_100_percent_reliability(shared_db):
    db, snap_id = shared_db
    runner = RedTeamRunner(db)
    res = runner.run_red_team_suite(snap_id)
    assert res["ai_reporting_reliability_score"] == 100.0
    assert res["failed_safety_checks"] == 0


def test_stakeholder_query_q1048_structure(shared_db):
    db, _ = shared_db
    qw = StakeholderQueryWorkbench(db)
    q = qw.seed_demo_query()
    assert q.query_id == "Q-1048"
    assert q.reported_value == Decimal("118.4000")
    assert q.recalculated_value == Decimal("117.9000")
    assert q.variance == Decimal("0.5000")
    assert q.investigation_status == "RESOLVED"
