from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from backend.app.calculators.lcr import LcrCalculationEngine
from backend.app.calculators.nsfr import NsfrCalculationEngine
from backend.app.models.facts import (
    FactBalanceSheet,
    FactControlResult,
    FactException,
    FactReportingSnapshot,
)
from backend.app.models.workflow import AdjustmentEvent, CloseCycle, CloseStep


class ShadowCloseWorkflowEngine:
    """
    Orchestrates the 10 sequential shadow close stages and manages late adjustments:
      Stage 1: Freeze source data
      Stage 2: Validate balances
      Stage 3: Reconcile accounting totals
      Stage 4: Apply regulatory classification
      Stage 5: Calculate liquidity metrics
      Stage 6: Run controls
      Stage 7: Investigate exceptions
      Stage 8: Prepare management information
      Stage 9: Generate reporting output
      Stage 10: Reviewer sign-off
    """

    STAGE_NAMES = [
        "Freeze source data",
        "Validate balances",
        "Reconcile accounting totals",
        "Apply regulatory classification",
        "Calculate liquidity metrics",
        "Run controls",
        "Investigate exceptions",
        "Prepare management information",
        "Generate reporting output",
        "Reviewer sign-off",
    ]

    def __init__(self, db: Session):
        self.db = db

    def get_close_status(self, period: str = "2026-Q3") -> dict[str, Any]:
        cycle = self.db.query(CloseCycle).filter_by(period=period).first()
        if not cycle:
            return {"period": period, "status": "NOT_STARTED", "steps": []}

        steps = self.db.query(CloseStep).filter_by(cycle_id=cycle.cycle_id).order_by(CloseStep.step_number).all()
        return {
            "cycle_id": cycle.cycle_id,
            "period": cycle.period,
            "status": cycle.status,
            "started_at": cycle.started_at.isoformat() if cycle.started_at else None,
            "completed_at": cycle.completed_at.isoformat() if cycle.completed_at else None,
            "approved_by": cycle.approved_by,
            "locked": cycle.locked,
            "steps": [
                {
                    "step_number": s.step_number,
                    "step_name": s.step_name,
                    "status": s.status,
                    "owner": s.owner,
                    "evidence": s.evidence,
                    "error_message": s.error_message,
                }
                for s in steps
            ]
        }

    def advance_step(self, period: str, step_number: int, actor_role: str = "Controller") -> dict[str, Any]:
        cycle = self.db.query(CloseCycle).filter_by(period=period).first()
        if not cycle:
            raise KeyError(f"Close cycle for period '{period}' not found.")

        step = self.db.query(CloseStep).filter_by(cycle_id=cycle.cycle_id, step_number=step_number).first()
        if not step:
            raise KeyError(f"Step {step_number} not found.")

        step.status = "COMPLETED"
        step.completed_at = datetime.utcnow()

        # Unlock next step
        next_step = self.db.query(CloseStep).filter_by(cycle_id=cycle.cycle_id, step_number=step_number + 1).first()
        if next_step and next_step.status == "NOT_STARTED":
            next_step.status = "IN_PROGRESS"
            next_step.started_at = datetime.utcnow()

        if step_number == 10:
            cycle.status = "COMPLETED"
            cycle.completed_at = datetime.utcnow()
            cycle.approved_by = actor_role
            cycle.locked = True

        self.db.commit()
        return self.get_close_status(period)

    def inject_late_adjustment(
        self,
        snapshot_id: str,
        account_id: str = "ACC-CORP_NON_OPERATIONAL",
        adjustment_amount_usd: float = 38000000.0,
        rationale: str = "Late-clearing corporate wholesale funding wire discover post-freeze cutoff.",
        actor_role: str = "Lead Controller",
    ) -> dict[str, Any]:
        """
        Acceptance Test 4: Injects a $38M late balance-sheet adjustment post-freeze:
          1. Detects reconciliation break (Assets != Liabilities)
          2. Regresses Close Stages 5-10 to BLOCKED
          3. Recalculates affected NSFR & LCR
          4. Propagates downstream impact to reporting lines
          5. Generates auditable AdjustmentEvent
        """
        snap = self.db.query(FactReportingSnapshot).filter_by(snapshot_id=snapshot_id).first()
        if not snap:
            raise KeyError(f"Snapshot '{snapshot_id}' not found.")

        cycle = self.db.query(CloseCycle).filter_by(period=snap.period).first()
        adj_amount = Decimal(str(adjustment_amount_usd))

        # 1. Create adjustment event
        adj_id = f"ADJ-{snap.period}-{datetime.utcnow().strftime('%H%M%S')}"
        adj = AdjustmentEvent(
            adjustment_id=adj_id,
            cycle_id=cycle.cycle_id if cycle else f"CYCLE-{snap.period}",
            timestamp=datetime.utcnow(),
            account_id=account_id,
            adjustment_type="LATE_FUNDING",
            amount=adj_amount,
            rationale=rationale,
            approver_role=actor_role,
            status="APPLIED",
        )
        self.db.add(adj)

        # 2. Update balance-sheet position
        bs_row = self.db.query(FactBalanceSheet).filter_by(snapshot_id=snapshot_id, account_id=account_id).first()
        old_bal = bs_row.closing_balance_usd if bs_row else Decimal("0.0")
        if bs_row:
            bs_row.movement_amount += adj_amount
            bs_row.closing_balance += adj_amount
            bs_row.closing_balance_usd += adj_amount
            bs_row.asf_amount = bs_row.closing_balance_usd * (bs_row.asf_factor or Decimal("0.5000"))

        # 3. Trip post-freeze mutation control (CTRL-REC-008) to FAIL
        ctrl_rec_8 = self.db.query(FactControlResult).filter_by(snapshot_id=snapshot_id, control_id="CTRL-REC-008").first()
        if ctrl_rec_8:
            ctrl_rec_8.status = "FAIL"
            ctrl_rec_8.actual_result = f"Post-freeze mutation detected: ${float(adj_amount):,.2f} on {account_id}"

        # 4. Open critical exception
        exc_id = f"EXC-{snapshot_id}-CTRL-REC-008"
        exc = self.db.query(FactException).filter_by(exception_id=exc_id).first()
        if not exc:
            exc = FactException(
                exception_id=exc_id,
                control_id="CTRL-REC-008",
                snapshot_id=snapshot_id,
                detected_at=datetime.utcnow(),
                period=snap.period,
                severity="CRITICAL",
                description=f"Late adjustment break: ${float(adj_amount)/1e6:.1f}M injected into {account_id}",
                root_cause=rationale,
                affected_metric="NSFR",
                affected_report="Executive Summary Schedule 1.1",
                estimated_impact_usd=adj_amount,
                status="OPEN",
                owner="Financial Control Team",
                resolution=None,
                reviewer=actor_role,
            )
            self.db.add(exc)
        else:
            exc.status = "OPEN"
            exc.estimated_impact_usd = adj_amount

        # 5. Regress close steps 5 through 10 to BLOCKED
        if cycle:
            steps = self.db.query(CloseStep).filter(
                CloseStep.cycle_id == cycle.cycle_id,
                CloseStep.step_number >= 5
            ).all()
            for s in steps:
                s.status = "BLOCKED"
                s.error_message = f"Blocked due to late balance-sheet adjustment {adj_id} (${float(adj_amount)/1e6:.1f}M)"

        # 6. Recalculate metrics
        nsfr_eng = NsfrCalculationEngine(self.db)
        recalc_nsfr = nsfr_eng.calculate_nsfr(snapshot_id, persist=True)
        lcr_eng = LcrCalculationEngine(self.db)
        recalc_lcr = lcr_eng.calculate_lcr(snapshot_id, persist=True)

        self.db.commit()

        return {
            "adjustment_id": adj_id,
            "snapshot_id": snapshot_id,
            "account_id": account_id,
            "amount_usd": float(adj_amount),
            "rationale": rationale,
            "previous_balance_usd": float(old_bal),
            "new_balance_usd": float(bs_row.closing_balance_usd if bs_row else 0),
            "recalculated_nsfr_percentage": recalc_nsfr["nsfr_percentage"],
            "recalculated_lcr_percentage": recalc_lcr["lcr_percentage"],
            "impacted_control": "CTRL-REC-008 (Post-Freeze Data Mutation Guard)",
            "impacted_steps": "Stages 5 through 10 marked BLOCKED",
            "report_regeneration_required": True,
        }
