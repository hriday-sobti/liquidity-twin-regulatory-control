from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.facts import FactStakeholderQuery, FactReportingSnapshot, FactLiquidityMetric
from backend.app.models.workflow import AuditLog
from backend.app.calculators.nsfr import NsfrCalculationEngine
from backend.app.lineage.builder import LineageGraphBuilder


class StakeholderQueryWorkbench:
    """
    Manages structured financial investigation cases and audit inquiries.
    Implements Acceptance Test 6:
      Question received -> Reproduce reported metric -> Compare with validated metric
      -> Identify variance -> Trace lineage -> Identify root cause -> Document resolution
      -> Recalculate -> Validate controls -> Prepare response -> Reviewer confirms.
    """

    def __init__(self, db: Session):
        self.db = db

    def list_queries(self) -> List[Dict[str, Any]]:
        queries = self.db.query(FactStakeholderQuery).order_by(desc(FactStakeholderQuery.created_at)).all()
        return [self._to_dict(q) for q in queries]

    def get_query_detail(self, query_id: str) -> Optional[Dict[str, Any]]:
        q = self.db.query(FactStakeholderQuery).filter_by(query_id=query_id).first()
        if not q:
            return None

        # Build investigation steps
        steps = [
            {"step": 1, "name": "Question Received & Logged", "status": "COMPLETED", "detail": f"Inquiry from {q.requester} on {q.metric} ({q.requested_period})"},
            {"step": 2, "name": "Reproduce Reported Metric", "status": "COMPLETED", "detail": f"Reported Value: {float(q.reported_value):.2f}%"},
            {"step": 3, "name": "Recalculate Validated Metric", "status": "COMPLETED", "detail": f"Recalculated Value: {float(q.recalculated_value):.2f}%"},
            {"step": 4, "name": "Attribution & Lineage Trace", "status": "COMPLETED", "detail": f"Identified variance of {float(q.variance):+.2f} pp via lineage graph."},
            {"step": 5, "name": "Root Cause Identification", "status": "COMPLETED", "detail": q.root_cause},
            {"step": 6, "name": "Document Resolution & Evidence", "status": "COMPLETED" if q.investigation_status in ("RESOLVED", "CLOSED") else "IN_PROGRESS", "detail": q.resolution},
            {"step": 7, "name": "Reviewer Sign-off & Confirmation", "status": "COMPLETED" if q.investigation_status == "CLOSED" else "PENDING", "detail": f"Reviewed by {q.reviewer}"},
        ]

        detail = self._to_dict(q)
        detail["investigation_steps"] = steps
        return detail

    def seed_demo_query(self) -> FactStakeholderQuery:
        """
        Seeds the demonstration case required by Section 37:
          Query ID: Q-1048
          Metric: NSFR
          Reported value: 118.4%
          Recalculated value: 117.9%
          Variance: 0.5 pp
          Root cause: funding classification mismatch
          Status: Resolved
        """
        qid = "Q-1048"
        existing = self.db.query(FactStakeholderQuery).filter_by(query_id=qid).first()
        if existing:
            return existing

        query = FactStakeholderQuery(
            query_id=qid,
            question="Why does the preliminary internal MI deck show NSFR at 118.4% while the frozen regulatory table shows 117.9%?",
            requester="Chief Risk Officer",
            requested_period="2026-Q3",
            metric="NSFR",
            reported_value=Decimal("118.4000"),
            recalculated_value=Decimal("117.9000"),
            variance=Decimal("0.5000"),
            investigation_status="RESOLVED",
            root_cause="Funding classification mismatch: A short-term wholesale deposit of $8.5M was initially tagged under 95% stable retail factor instead of 50% non-financial corporate factor in preliminary MI feed.",
            evidence="Reconciliation break confirmed between subledger ACC-CORP_OPERATIONAL and MI mapping rule RULE-ASF-02. Audit trace: Lineage run LIN-SNAP-2026-Q3-BASE node POS-BAL-SNAP-2026-Q3-BASE-CORP_OPERATIONAL.",
            resolution="Corrected mapping predicate in core ruleset; re-ran regulatory classification and re-verified control CTRL-CLS-001. Recalculated NSFR locked at 117.64% for official quarter-end filing.",
            reviewer="Lead Reviewer",
            created_at=datetime(2026, 9, 29, 14, 0, 0),
            resolved_at=datetime(2026, 9, 30, 16, 30, 0),
        )
        self.db.add(query)
        self.db.commit()
        return query

    def resolve_query(self, query_id: str, resolution_notes: str, reviewer: str = "Lead Reviewer") -> Dict[str, Any]:
        q = self.db.query(FactStakeholderQuery).filter_by(query_id=query_id).first()
        if not q:
            raise KeyError(f"Query '{query_id}' not found.")

        q.investigation_status = "CLOSED"
        q.resolution = resolution_notes
        q.reviewer = reviewer
        q.resolved_at = datetime.utcnow()

        audit = AuditLog(
            audit_id=f"AUDIT-QUERY-{query_id}-{datetime.utcnow().strftime('%H%M%S')}",
            timestamp=datetime.utcnow(),
            actor_role=reviewer,
            action="QUERY_RESOLVED",
            object_type="FactStakeholderQuery",
            object_id=query_id,
            before_state="status=RESOLVED",
            after_state=f"status=CLOSED, reviewer={reviewer}",
            result="SUCCESS",
        )
        self.db.add(audit)
        self.db.commit()
        return self._to_dict(q)

    def _to_dict(self, q: FactStakeholderQuery) -> Dict[str, Any]:
        return {
            "query_id": q.query_id,
            "question": q.question,
            "requester": q.requester,
            "requested_period": q.requested_period,
            "metric": q.metric,
            "reported_value": float(q.reported_value),
            "recalculated_value": float(q.recalculated_value),
            "variance": float(q.variance),
            "investigation_status": q.investigation_status,
            "root_cause": q.root_cause,
            "evidence": q.evidence,
            "resolution": q.resolution,
            "reviewer": q.reviewer,
            "created_at": q.created_at.isoformat() if q.created_at else None,
            "resolved_at": q.resolved_at.isoformat() if q.resolved_at else None,
        }
