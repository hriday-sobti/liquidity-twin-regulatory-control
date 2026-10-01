from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)

from backend.app.core.database import Base


class LineageRun(Base):
    __tablename__ = "lineage_run"

    run_id = Column(String(64), primary_key=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    calculation_type = Column(String(32), nullable=False)  # NSFR, LCR, FULL_CYCLE
    calculation_version = Column(String(16), nullable=False, default="3.2.0")
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    node_count = Column(Integer, default=0, nullable=False)
    edge_count = Column(Integer, default=0, nullable=False)


class LineageNode(Base):
    __tablename__ = "lineage_node"

    node_id = Column(String(128), primary_key=True)
    run_id = Column(String(64), ForeignKey("lineage_run.run_id"), nullable=False, index=True)
    # Node types: SOURCE_RECORD, ACCOUNTING_POSITION, REGULATORY_CATEGORY, RULE,
    # ASF_CONTRIBUTION, RSF_CONTRIBUTION, METRIC, CONTROL, REPORT_LINE, EXCEPTION
    node_type = Column(String(32), nullable=False, index=True)
    entity_id = Column(String(64), nullable=True, index=True)
    label = Column(String(256), nullable=False)
    properties_json = Column(Text, nullable=True)  # JSON-encoded properties

    __table_args__ = (
        Index("idx_lineage_node_run_type", "run_id", "node_type"),
    )


class LineageEdge(Base):
    __tablename__ = "lineage_edge"

    edge_id = Column(String(128), primary_key=True)
    run_id = Column(String(64), ForeignKey("lineage_run.run_id"), nullable=False, index=True)
    source_node_id = Column(String(128), ForeignKey("lineage_node.node_id"), nullable=False, index=True)
    target_node_id = Column(String(128), ForeignKey("lineage_node.node_id"), nullable=False, index=True)
    # Edge types: AGGREGATES, CLASSIFIED_AS, GOVERNED_BY, CALCULATES, COMPOUNDS_INTO, VALIDATES, DISCLOSES, AFFECTS
    edge_type = Column(String(32), nullable=False, index=True)
    weight = Column(Numeric(24, 4), nullable=True)

    __table_args__ = (
        Index("idx_lineage_edge_src_tgt", "source_node_id", "target_node_id"),
    )
