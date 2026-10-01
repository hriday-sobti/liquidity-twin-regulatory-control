from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.models.facts import FactReportingSnapshot, FactControlResult, FactException
from backend.app.calculators.asf import AsfCalculationEngine
from backend.app.calculators.rsf import RsfCalculationEngine
from backend.app.calculators.nsfr import NsfrCalculationEngine
from backend.app.calculators.lcr import LcrCalculationEngine
from backend.app.scenarios.movement import MovementAnalyzer
from backend.app.scenarios.engine import ScenarioLabEngine
from backend.app.lineage.builder import LineageGraphBuilder
from backend.app.controls.engine import ControlEngine
from backend.app.controls.exceptions import ExceptionManagementService
from backend.app.controls.catalog import CONTROL_DEFINITIONS
from backend.app.reporting.compiler import ReportingCompiler
from backend.app.services.close_workflow import ShadowCloseWorkflowEngine
from backend.app.services.query_workbench import StakeholderQueryWorkbench
from backend.app.services.event_replay import EventReplayService
from backend.app.copilot.engine import CopilotEngine
from backend.app.copilot.red_team import RedTeamRunner

router = APIRouter()


@router.get("/overview")
def get_overview(snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    snap = db.query(FactReportingSnapshot).filter_by(snapshot_id=snapshot_id).first()
    if not snap:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    mov_engine = MovementAnalyzer(db)
    mov = mov_engine.analyze_movement(snapshot_id)

    return {
        "snapshot": {
            "snapshot_id": snap.snapshot_id,
            "period": snap.period,
            "business_date": snap.business_date.isoformat(),
            "status": snap.status,
            "rule_version": snap.rule_version,
            "calculation_version": snap.calculation_version,
            "created_at": snap.created_at.isoformat(),
        },
        "kpis": {
            "nsfr": float(snap.nsfr_value or 0),
            "lcr": float(snap.lcr_value or 0),
            "asf_usd": float(snap.asf_amount or 0),
            "rsf_usd": float(snap.rsf_amount or 0),
            "hqla_usd": float(snap.hqla_amount or 0),
            "net_outflows_usd": float(snap.net_outflows_amount or 0),
            "control_score": float(snap.control_score or 0),
            "open_exceptions_count": snap.open_exceptions_count,
        },
        "movement": mov,
    }


@router.get("/metrics/nsfr")
def get_nsfr_detail(snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    engine = NsfrCalculationEngine(db)
    return engine.calculate_nsfr(snapshot_id)


@router.get("/metrics/lcr")
def get_lcr_detail(snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    engine = LcrCalculationEngine(db)
    return engine.calculate_lcr(snapshot_id)


@router.get("/lineage/{metric_name}")
def get_lineage(metric_name: str = "NSFR", snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    builder = LineageGraphBuilder(db)
    return builder.get_metric_birth_certificate(snapshot_id, metric_name.upper())


@router.get("/lineage/blast-radius/{control_id}")
def get_blast_radius(control_id: str, snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    builder = LineageGraphBuilder(db)
    return builder.get_control_blast_radius(snapshot_id, control_id)


@router.get("/movements")
def get_movements(snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    analyzer = MovementAnalyzer(db)
    return analyzer.analyze_movement(snapshot_id)


@router.post("/scenarios/run")
def run_scenario(
    body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    lab = ScenarioLabEngine(db)
    return lab.run_scenario(
        base_snapshot_id=body.get("base_snapshot_id", "SNAP-2026-Q3-BASE"),
        scenario_name=body.get("scenario_name", "Custom Stress Scenario"),
        corporate_deposit_pct=float(body.get("corporate_deposit_pct", 0.0)),
        retail_deposit_pct=float(body.get("retail_deposit_pct", 0.0)),
        loan_growth_pct=float(body.get("loan_growth_pct", 0.0)),
        wholesale_maturity_pct=float(body.get("wholesale_maturity_pct", 0.0)),
        new_term_funding_usd=float(body.get("new_term_funding_usd", 0.0)),
        asset_reallocation_usd=float(body.get("asset_reallocation_usd", 0.0)),
    )


@router.get("/controls")
def get_controls(snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    results = db.query(FactControlResult).filter_by(snapshot_id=snapshot_id).all()
    if not results:
        engine = ControlEngine(db)
        engine.run_all_controls(snapshot_id)
        results = db.query(FactControlResult).filter_by(snapshot_id=snapshot_id).all()

    items = []
    for r in results:
        items.append({
            "control_id": r.control_id,
            "control_name": r.control_name,
            "control_family": r.control_family,
            "severity": r.severity,
            "expected_result": r.expected_result,
            "actual_result": r.actual_result,
            "status": r.status,
            "evidence_reference": r.evidence_reference,
            "executed_at": r.executed_at.isoformat(),
        })

    passed = sum(1 for x in items if x["status"] == "PASS")
    failed = sum(1 for x in items if x["status"] == "FAIL")
    warning = sum(1 for x in items if x["status"] == "WARNING")
    score = round((passed / len(items)) * 100.0, 1) if items else 0.0

    return {
        "snapshot_id": snapshot_id,
        "total_controls": len(items),
        "passed_count": passed,
        "failed_count": failed,
        "warning_count": warning,
        "control_score": score,
        "controls": items,
    }


@router.get("/exceptions")
def get_exceptions(snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    svc = ExceptionManagementService(db)
    return svc.list_exceptions(snapshot_id=snapshot_id)


@router.get("/exceptions/{exception_id}")
def get_exception_detail(exception_id: str, db: Session = Depends(get_db)):
    svc = ExceptionManagementService(db)
    exc = svc.get_exception_detail(exception_id)
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
    return exc


@router.post("/exceptions/{exception_id}/update")
def update_exception(
    exception_id: str,
    body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    svc = ExceptionManagementService(db)
    return svc.update_exception_status(
        exception_id=exception_id,
        new_status=body.get("status", "REMEDIATED"),
        resolution_notes=body.get("resolution", "Updated via workstation"),
        actor_role=body.get("actor_role", "Analyst"),
    )


@router.get("/close/status")
def get_close_status(period: str = "2026-Q3", db: Session = Depends(get_db)):
    engine = ShadowCloseWorkflowEngine(db)
    return engine.get_close_status(period)


@router.post("/close/advance")
def advance_close_step(
    body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    engine = ShadowCloseWorkflowEngine(db)
    return engine.advance_step(
        period=body.get("period", "2026-Q3"),
        step_number=int(body.get("step_number", 1)),
        actor_role=body.get("actor_role", "Controller"),
    )


@router.post("/close/late-adjustment")
def inject_late_adjustment(
    body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    engine = ShadowCloseWorkflowEngine(db)
    return engine.inject_late_adjustment(
        snapshot_id=body.get("snapshot_id", "SNAP-2026-Q3-BASE"),
        account_id=body.get("account_id", "ACC-CORP_NON_OPERATIONAL"),
        adjustment_amount_usd=float(body.get("adjustment_amount_usd", 38000000.0)),
        rationale=body.get("rationale", "Late corporate wire discovery"),
        actor_role=body.get("actor_role", "Lead Controller"),
    )


@router.post("/reports/compile")
def compile_reports(snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    compiler = ReportingCompiler(db)
    return compiler.compile_reporting_pack(snapshot_id)


@router.get("/queries")
def get_queries(db: Session = Depends(get_db)):
    qw = StakeholderQueryWorkbench(db)
    return qw.list_queries()


@router.get("/queries/{query_id}")
def get_query_detail(query_id: str, db: Session = Depends(get_db)):
    qw = StakeholderQueryWorkbench(db)
    q = qw.get_query_detail(query_id)
    if not q:
        raise HTTPException(status_code=404, detail="Query not found")
    return q


@router.get("/replay")
def get_event_replay(snapshot_id: str = "SNAP-2026-Q3-BASE", limit: int = 40, db: Session = Depends(get_db)):
    er = EventReplayService(db)
    return er.get_timeline_events(snapshot_id, limit=limit)


@router.post("/copilot/ask")
def copilot_ask(
    body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    copilot = CopilotEngine(db)
    return copilot.ask(
        question=body.get("question", "What drove the NSFR movement?"),
        snapshot_id=body.get("snapshot_id", "SNAP-2026-Q3-BASE"),
        force_adversarial_error=body.get("force_adversarial_error"),
    )


@router.get("/copilot/red-team")
def get_red_team_results(snapshot_id: str = "SNAP-2026-Q3-BASE", db: Session = Depends(get_db)):
    runner = RedTeamRunner(db)
    return runner.run_red_team_suite(snapshot_id)
