from datetime import date

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Index,
    Numeric,
    String,
    Text,
)

from backend.app.core.database import Base


class RegulatoryRule(Base):
    __tablename__ = "regulatory_rules"

    rule_id = Column(String(64), primary_key=True)
    rule_name = Column(String(128), nullable=False)
    rule_version = Column(String(16), nullable=False, default="3.2.0")
    framework = Column(String(16), nullable=False, index=True)  # NSFR, LCR
    rule_type = Column(String(32), nullable=False)  # ASF, RSF, HQLA, OUTFLOW, INFLOW
    
    # Classification conditions and predicates
    instrument_condition = Column(String(128), nullable=False)
    counterparty_condition = Column(String(128), nullable=True)
    maturity_condition = Column(String(64), nullable=True)  # e.g., '<180D', '180D-365D', '>=365D'
    encumbrance_condition = Column(String(32), nullable=True)  # UNENCUMBERED, ENCUMBERED, ANY
    
    # Quantitative regulatory factor (e.g. 0.9500 for stable retail, 0.0500 for level 1)
    factor = Column(Numeric(6, 4), nullable=False)
    
    # Effective validity window
    effective_from = Column(Date, nullable=False, default=date(2026, 1, 1))
    effective_to = Column(Date, nullable=True)
    
    # Audit and provenance fields (Rule 2 adherence)
    source_reference = Column(String(128), nullable=False)  # e.g., 'BCBS 295 §18'
    source_name = Column(String(128), nullable=False, default="Basel Committee on Banking Supervision")
    source_url = Column(String(256), nullable=False)
    source_access_date = Column(Date, nullable=False, default=date(2026, 10, 1))
    methodology_note = Column(Text, nullable=False)
    
    active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("idx_rules_lookup", "framework", "rule_type", "active", "rule_version"),
    )
