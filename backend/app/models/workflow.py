from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Numeric,
    ForeignKey,
    Index,
    Text,
)
from backend.app.core.database import Base


class CloseCycle(Base):
    __tablename__ = "close_cycle"

    cycle_id = Column(String(64), primary_key=True)
    period = Column(String(16), unique=True, nullable=False, index=True)  # e.g. '2026-Q3'
    status = Column(String(32), nullable=False, default="NOT_STARTED")  # NOT_STARTED, IN_PROGRESS, COMPLETED, BLOCKED
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    approved_by = Column(String(64), nullable=True)
    locked = Column(Boolean, default=False, nullable=False)


class CloseStep(Base):
    __tablename__ = "close_step"

    step_id = Column(String(64), primary_key=True)
    cycle_id = Column(String(64), ForeignKey("close_cycle.cycle_id"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)  # 1 to 10
    step_name = Column(String(128), nullable=False)
    # NOT_STARTED, IN_PROGRESS, COMPLETED, BLOCKED, FAILED
    status = Column(String(32), nullable=False, default="NOT_STARTED", index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    owner = Column(String(64), nullable=False)
    evidence = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    dependencies = Column(String(128), nullable=True)

    __table_args__ = (
        Index("idx_close_step_cycle_num", "cycle_id", "step_number"),
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    audit_id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    actor_role = Column(String(64), nullable=False)  # Analyst, Reviewer, Controller, System
    action = Column(String(64), nullable=False, index=True)  # SNAPSHOT_CREATED, CONTROL_RUN, EXCEPTION_RESOLVED, etc.
    object_type = Column(String(64), nullable=False)
    object_id = Column(String(64), nullable=False, index=True)
    before_state = Column(Text, nullable=True)
    after_state = Column(Text, nullable=True)
    result = Column(String(32), nullable=False, default="SUCCESS")
    metadata_json = Column(Text, nullable=True)


class AdjustmentEvent(Base):
    __tablename__ = "adjustment_event"

    adjustment_id = Column(String(64), primary_key=True)
    cycle_id = Column(String(64), ForeignKey("close_cycle.cycle_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    account_id = Column(String(64), ForeignKey("dim_account.account_id"), nullable=False, index=True)
    adjustment_type = Column(String(32), nullable=False)  # LATE_FUNDING, RECLASSIFICATION, BALANCE_CORRECTION
    amount = Column(Numeric(24, 4), nullable=False)
    rationale = Column(Text, nullable=False)
    approver_role = Column(String(64), nullable=False, default="Lead Controller")
    status = Column(String(32), nullable=False, default="APPLIED")  # PENDING, APPLIED, REVERTED
