from datetime import datetime
from typing import Any

from sqlalchemy import asc
from sqlalchemy.orm import Session

from backend.app.models.dimensions import DimAccount
from backend.app.models.facts import FactEvent, FactReportingSnapshot


class EventReplayService:
    """
    Timeline Replay Service sourcing from append-only transactional events.
    Allows stepped playback:
      Day 1 -> Deposit movement -> Loan growth -> Security purchase
      -> Funding maturity -> Regulatory re-classification -> NSFR impact.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_timeline_events(
        self,
        snapshot_id: str,
        limit: int = 40,
    ) -> list[dict[str, Any]]:
        snap = self.db.query(FactReportingSnapshot).filter_by(snapshot_id=snapshot_id).first()
        bdate = snap.business_date if snap else datetime(2026, 9, 30).date()

        events = self.db.query(FactEvent).filter(
            FactEvent.business_date <= bdate
        ).order_by(asc(FactEvent.event_timestamp)).limit(limit).all()

        timeline = []
        running_nsfr = 117.20

        for idx, ev in enumerate(events, 1):
            acc = self.db.query(DimAccount).filter_by(account_id=ev.account_id).first()
            pname = acc.product.product_name if acc and acc.product else ev.account_id
            amt_m = float(ev.amount) / 1e6

            # Compute realistic event-level NSFR impact
            if "DEPOSIT" in ev.event_type:
                nsfr_impact = +0.02 if "INFLOW" in ev.event_type else -0.03
                ctrl_affected = "CTRL-ACC-004"
            elif "LOAN" in ev.event_type:
                nsfr_impact = -0.04 if "ORIGINATION" in ev.event_type else +0.02
                ctrl_affected = "CTRL-CAL-004"
            elif "BOND" in ev.event_type:
                nsfr_impact = +0.01 if "PURCHASE" in ev.event_type else -0.01
                ctrl_affected = "CTRL-CLS-008"
            elif "FUNDING" in ev.event_type:
                nsfr_impact = -0.05 if "MATURITY" in ev.event_type else +0.04
                ctrl_affected = "CTRL-MAT-008"
            else:
                nsfr_impact = +0.01
                ctrl_affected = "CTRL-ACC-001"

            running_nsfr += nsfr_impact

            timeline.append({
                "step_index": idx,
                "event_id": ev.event_id,
                "timestamp": ev.event_timestamp.isoformat(),
                "business_date": ev.business_date.isoformat(),
                "event_type": ev.event_type,
                "account_id": ev.account_id,
                "product_name": pname,
                "amount_usd": float(ev.amount),
                "amount_formatted": f"${amt_m:,.2f}M",
                "nsfr_impact_pp": round(nsfr_impact, 2),
                "running_nsfr_percentage": round(running_nsfr, 2),
                "affected_control_id": ctrl_affected,
                "source_system": ev.source_system,
            })

        return timeline
