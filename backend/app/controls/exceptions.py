from datetime import datetime
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.app.models.facts import FactControlResult, FactException, FactReportingSnapshot
from backend.app.models.workflow import AuditLog


class ExceptionManagementService:
    """
    Manages the lifecycle of regulatory control breaks and exceptions:
    OPEN -> INVESTIGATING -> REMEDIATED -> AWAITING_REVIEW -> RESOLVED -> CLOSED.
    Provides structured root cause documentation, impact quantification, and sign-offs.
    """

    VALID_STATUSES = [
        "OPEN",
        "INVESTIGATING",
        "REMEDIATED",
        "AWAITING_REVIEW",
        "RESOLVED",
        "CLOSED",
    ]

    def __init__(self, db: Session):
        self.db = db

    def list_exceptions(
        self,
        snapshot_id: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        affected_metric: str | None = None,
    ) -> list[dict[str, Any]]:
        query = self.db.query(FactException)
        if snapshot_id:
            query = query.filter(FactException.snapshot_id == snapshot_id)
        if severity:
            query = query.filter(FactException.severity == severity)
        if status:
            query = query.filter(FactException.status == status)
        if affected_metric:
            query = query.filter(FactException.affected_metric == affected_metric)

        exceptions = query.order_by(desc(FactException.detected_at)).all()
        return [self._to_dict(e) for e in exceptions]

    def get_exception_detail(self, exception_id: str) -> dict[str, Any] | None:
        exc = self.db.query(FactException).filter_by(exception_id=exception_id).first()
        if not exc:
            return None

        # Correlate with underlying control result
        ctrl_res = self.db.query(FactControlResult).filter_by(
            snapshot_id=exc.snapshot_id, control_id=exc.control_id
        ).first()

        detail = self._to_dict(exc)
        detail["control_detail"] = {
            "control_name": ctrl_res.control_name if ctrl_res else "N/A",
            "control_family": ctrl_res.control_family if ctrl_res else "N/A",
            "expected_result": ctrl_res.expected_result if ctrl_res else "N/A",
            "actual_result": ctrl_res.actual_result if ctrl_res else "N/A",
            "evidence_reference": ctrl_res.evidence_reference if ctrl_res else "N/A",
            "executed_at": ctrl_res.executed_at.isoformat() if ctrl_res else None,
        }
        detail["remediation_plan"] = {
            "action_required": "Match pending broker confirmation against counterparty clearing ledger." if exc.control_id == "CTRL-REC-007" else "Review annual contract.",
            "responsible_role": exc.owner,
            "target_resolution_window": "24 Hours" if exc.severity in ("CRITICAL", "HIGH") else "5 Business Days",
        }
        return detail

    def update_exception_status(
        self,
        exception_id: str,
        new_status: str,
        resolution_notes: str | None = None,
        actor_role: str = "Analyst",
    ) -> dict[str, Any]:
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid exception status '{new_status}'. Must be one of {self.VALID_STATUSES}")

        exc = self.db.query(FactException).filter_by(exception_id=exception_id).first()
        if not exc:
            raise KeyError(f"Exception ID '{exception_id}' not found.")

        old_status = exc.status
        exc.status = new_status
        if resolution_notes:
            exc.resolution = resolution_notes

        if new_status in ("RESOLVED", "CLOSED"):
            exc.resolved_at = datetime.utcnow()
            exc.reviewer = actor_role

        # Log action to audit log
        audit = AuditLog(
            audit_id=f"AUDIT-EXC-{exception_id}-{datetime.utcnow().strftime('%H%M%S')}",
            timestamp=datetime.utcnow(),
            actor_role=actor_role,
            action="EXCEPTION_STATUS_UPDATE",
            object_type="FactException",
            object_id=exception_id,
            before_state=f"status={old_status}",
            after_state=f"status={new_status}, resolution={resolution_notes}",
            result="SUCCESS",
        )
        self.db.add(audit)

        # Update snapshot open exceptions count
        snap = self.db.query(FactReportingSnapshot).filter_by(snapshot_id=exc.snapshot_id).first()
        if snap:
            open_count = self.db.query(FactException).filter(
                FactException.snapshot_id == snap.snapshot_id,
                FactException.status.in_(["OPEN", "INVESTIGATING", "AWAITING_REVIEW"])
            ).count()
            snap.open_exceptions_count = open_count

        self.db.commit()
        return self._to_dict(exc)

    def _to_dict(self, e: FactException) -> dict[str, Any]:
        return {
            "exception_id": e.exception_id,
            "control_id": e.control_id,
            "snapshot_id": e.snapshot_id,
            "detected_at": e.detected_at.isoformat() if e.detected_at else None,
            "period": e.period,
            "severity": e.severity,
            "description": e.description,
            "root_cause": e.root_cause,
            "affected_metric": e.affected_metric,
            "affected_report": e.affected_report,
            "estimated_impact_usd": float(e.estimated_impact_usd) if e.estimated_impact_usd else 0.0,
            "status": e.status,
            "owner": e.owner,
            "resolution": e.resolution,
            "reviewer": e.reviewer,
            "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
        }
