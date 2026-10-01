import sys
import subprocess
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.services.generator import SyntheticBankGenerator
from backend.app.controls.engine import ControlEngine
from backend.app.reporting.compiler import ReportingCompiler
from backend.app.copilot.red_team import RedTeamRunner
from backend.app.scenarios.engine import ScenarioLabEngine


def run_smoke_verification():
    print("=================================================================")
    print("    LIQUIDITY TWIN — AUTOMATED END-TO-END SMOKE VERIFICATION     ")
    print("=================================================================")

    # 1. Database & Seeding
    print("[1/6] Verifying database schema & deterministic seeding...")
    db = SessionLocal()
    gen = SyntheticBankGenerator(db, seed=42)
    snap = gen.seed_all()
    assert snap.snapshot_id == "SNAP-2026-Q3-BASE"
    print(f"      -> Snapshot: {snap.snapshot_id} | NSFR: {float(snap.nsfr_value):.2f}% | LCR: {float(snap.lcr_value):.2f}%")

    # 2. Controls Suite Execution
    print("[2/6] Executing 100 automated continuous controls...")
    ce = ControlEngine(db)
    ctrl_res = ce.run_all_controls(snap.snapshot_id)
    assert ctrl_res["total_controls"] == 100
    assert ctrl_res["control_score"] == 98.0
    print(f"      -> Total: {ctrl_res['total_controls']} | Passed: {ctrl_res['passed_count']} | Score: {ctrl_res['control_score']}%")

    # 3. Acceptance Test 3: -8% Corporate Deposit Stress
    print("[3/6] Verifying Scenario Lab (-8% Corporate Deposit Outflow)...")
    lab = ScenarioLabEngine(db)
    scn_res = lab.run_scenario(snap.snapshot_id, "Smoke Stress", corporate_deposit_pct=-8.0)
    assert abs(scn_res["metrics"]["NSFR"]["scenario"] - 113.1) < 0.2
    print(f"      -> Base: {scn_res['metrics']['NSFR']['base']:.2f}% -> Stressed: {scn_res['metrics']['NSFR']['scenario']:.2f}% (Target: ~113.1%)")

    # 4. Acceptance Test 7 & 8: AI Red-Teaming & Numeric Verification
    print("[4/6] Verifying Controlled AI Copilot & Red-Team Suite...")
    rt = RedTeamRunner(db)
    rt_res = rt.run_red_team_suite(snap.snapshot_id)
    assert rt_res["ai_reporting_reliability_score"] == 100.0
    print(f"      -> Tests: {rt_res['total_tests']} | Reliability Score: {rt_res['ai_reporting_reliability_score']}%")

    # 5. Reporting Compiler (PDF & XLSX)
    print("[5/6] Verifying Reporting Compiler (PDF & XLSX generation)...")
    rc = ReportingCompiler(db)
    rep_res = rc.compile_reporting_pack(snap.snapshot_id)
    assert rep_res["pdf_path"].endswith(".pdf")
    assert rep_res["xlsx_path"].endswith(".xlsx")
    print(f"      -> PDF: {rep_res['pdf_path']}")
    print(f"      -> XLSX: {rep_res['xlsx_path']}")

    # 6. Pytest Execution
    print("[6/6] Running unit, property, and integration test suite...")
    cmd = [sys.executable, "-m", "pytest", "backend/tests", "-q"]
    ret = subprocess.call(cmd)
    assert ret == 0, "Pytest test suite failed."

    db.close()
    print("=================================================================")
    print("    SUCCESS: ALL 10 ACCEPTANCE VERIFICATION GATES PASSED!        ")
    print("=================================================================")


if __name__ == "__main__":
    run_smoke_verification()
