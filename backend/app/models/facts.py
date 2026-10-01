from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)

from backend.app.core.database import Base


class FactReportingSnapshot(Base):
    __tablename__ = "fact_reporting_snapshot"

    snapshot_id = Column(String(64), primary_key=True)
    snapshot_name = Column(String(128), nullable=False)
    period = Column(String(16), nullable=False, index=True)  # e.g., '2026-Q3', '2026-09-30'
    business_date = Column(Date, nullable=False, index=True)
    snapshot_type = Column(String(32), nullable=False, default="BASELINE")  # BASELINE, SCENARIO, ADJUSTED
    status = Column(String(32), nullable=False, default="FROZEN")  # DRAFT, FROZEN, SIGNED_OFF, SUPERSEDED
    
    # Core Calculated Metrics persisted for instant reporting & audit
    nsfr_value = Column(Numeric(10, 4), nullable=True)  # e.g. 117.6250 (%)
    lcr_value = Column(Numeric(10, 4), nullable=True)   # e.g. 132.4100 (%)
    asf_amount = Column(Numeric(24, 4), nullable=True)  # e.g. 842,300,000.00
    rsf_amount = Column(Numeric(24, 4), nullable=True)  # e.g. 716,000,000.00
    hqla_amount = Column(Numeric(24, 4), nullable=True)
    net_outflows_amount = Column(Numeric(24, 4), nullable=True)
    
    control_score = Column(Numeric(6, 2), nullable=True)  # e.g. 98.00 (%)
    open_exceptions_count = Column(Integer, default=0, nullable=False)
    
    rule_version = Column(String(16), nullable=False, default="3.2.0")
    calculation_version = Column(String(16), nullable=False, default="3.2.0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FactEvent(Base):
    __tablename__ = "fact_event"

    event_id = Column(String(64), primary_key=True)
    event_timestamp = Column(DateTime, nullable=False, index=True)
    business_date = Column(Date, nullable=False, index=True)
    entity_id = Column(String(64), ForeignKey("dim_entity.entity_id"), nullable=False, index=True)
    account_id = Column(String(64), ForeignKey("dim_account.account_id"), nullable=False, index=True)
    customer_id = Column(String(64), ForeignKey("dim_customer.customer_id"), nullable=False, index=True)
    
    # Event types: DEPOSIT_INFLOW, DEPOSIT_WITHDRAWAL, LOAN_ORIGINATION, LOAN_REPAYMENT,
    # WHOLESALE_FUNDING_DRAW, WHOLESALE_FUNDING_MATURITY, BOND_PURCHASE, BOND_SALE,
    # CAPITAL_INJECTION, CAPITAL_DISTRIBUTION, COLLATERAL_MOVEMENT, OBS_COMMITMENT_CHANGE
    event_type = Column(String(64), nullable=False, index=True)
    currency = Column(String(3), nullable=False, default="USD")
    amount = Column(Numeric(24, 4), nullable=False)
    amount_usd = Column(Numeric(24, 4), nullable=False)
    maturity_date = Column(Date, nullable=True)
    
    source_system = Column(String(32), nullable=False, default="CORE_BANKING")
    source_record_id = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_fact_event_date_type", "business_date", "event_type"),
    )


class FactBalanceSheet(Base):
    __tablename__ = "fact_balance_sheet"

    balance_id = Column(String(64), primary_key=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    business_date = Column(Date, nullable=False, index=True)
    account_id = Column(String(64), ForeignKey("dim_account.account_id"), nullable=False, index=True)
    
    # Double-entry roll forward: Closing = Opening + Movement
    opening_balance = Column(Numeric(24, 4), nullable=False, default=0.0)
    movement_amount = Column(Numeric(24, 4), nullable=False, default=0.0)
    closing_balance = Column(Numeric(24, 4), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    closing_balance_usd = Column(Numeric(24, 4), nullable=False)
    
    # Maturity tracking
    residual_maturity_days = Column(Integer, nullable=True)
    maturity_bucket = Column(String(32), nullable=False, default="PERPETUAL")  # <6M, 6M-1Y, >=1Y, PERPETUAL
    is_encumbered = Column(Boolean, default=False, nullable=False)
    
    # Regulatory mapping link
    regulatory_category_id = Column(String(64), ForeignKey("dim_regulatory_category.category_id"), nullable=True, index=True)
    rule_id = Column(String(64), ForeignKey("regulatory_rules.rule_id"), nullable=True, index=True)
    
    asf_factor = Column(Numeric(6, 4), nullable=True)
    rsf_factor = Column(Numeric(6, 4), nullable=True)
    asf_amount = Column(Numeric(24, 4), nullable=False, default=0.0)
    rsf_amount = Column(Numeric(24, 4), nullable=False, default=0.0)
    
    lcr_outflow_rate = Column(Numeric(6, 4), nullable=True)
    lcr_inflow_rate = Column(Numeric(6, 4), nullable=True)

    __table_args__ = (
        Index("idx_fact_balance_acc_snap", "snapshot_id", "account_id"),
    )


class FactDeposit(Base):
    __tablename__ = "fact_deposit"

    deposit_id = Column(String(64), primary_key=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    account_id = Column(String(64), ForeignKey("dim_account.account_id"), nullable=False, index=True)
    customer_id = Column(String(64), ForeignKey("dim_customer.customer_id"), nullable=False, index=True)
    deposit_type = Column(String(32), nullable=False)  # RETAIL_DEMAND, RETAIL_TERM, CORP_OPERATIONAL, CORP_NON_OPERATIONAL
    balance_usd = Column(Numeric(24, 4), nullable=False)
    is_operational = Column(Boolean, default=False, nullable=False)
    is_insured = Column(Boolean, default=False, nullable=False)
    residual_maturity_days = Column(Integer, nullable=True)


class FactLoan(Base):
    __tablename__ = "fact_loan"

    loan_id = Column(String(64), primary_key=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    account_id = Column(String(64), ForeignKey("dim_account.account_id"), nullable=False, index=True)
    customer_id = Column(String(64), ForeignKey("dim_customer.customer_id"), nullable=False, index=True)
    loan_type = Column(String(32), nullable=False)  # MORTGAGE_PRIME, MORTGAGE_NON_PRIME, CORP_TERM, RETAIL_UNSECURED
    principal_usd = Column(Numeric(24, 4), nullable=False)
    risk_weight = Column(Numeric(6, 2), nullable=False, default=35.0)
    residual_maturity_days = Column(Integer, nullable=False)
    is_performing = Column(Boolean, default=True, nullable=False)


class FactFunding(Base):
    __tablename__ = "fact_funding"

    funding_id = Column(String(64), primary_key=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    account_id = Column(String(64), ForeignKey("dim_account.account_id"), nullable=False, index=True)
    counterparty_type = Column(String(32), nullable=False)
    funding_type = Column(String(32), nullable=False)  # CD, CP, MTN, SUB_DEBT, INTERBANK
    balance_usd = Column(Numeric(24, 4), nullable=False)
    contractual_maturity_days = Column(Integer, nullable=False)
    residual_maturity_days = Column(Integer, nullable=False)


class FactSecurity(Base):
    __tablename__ = "fact_security"

    holding_id = Column(String(64), primary_key=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    security_id = Column(String(64), ForeignKey("dim_security.security_id"), nullable=False, index=True)
    nominal_value = Column(Numeric(24, 4), nullable=False)
    market_value_usd = Column(Numeric(24, 4), nullable=False)
    hqla_tier = Column(String(16), nullable=False)
    haircut = Column(Numeric(6, 4), nullable=False)
    is_encumbered = Column(Boolean, default=False, nullable=False)


class FactOffBalanceExposure(Base):
    __tablename__ = "fact_off_balance_exposure"

    exposure_id = Column(String(64), primary_key=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    account_id = Column(String(64), ForeignKey("dim_account.account_id"), nullable=False, index=True)
    facility_type = Column(String(32), nullable=False)  # CREDIT_LINE, LIQUIDITY_FACILITY
    committed_amount_usd = Column(Numeric(24, 4), nullable=False)
    undrawn_amount_usd = Column(Numeric(24, 4), nullable=False)
    rsf_factor = Column(Numeric(6, 4), nullable=False, default=0.05)
    lcr_draw_rate = Column(Numeric(6, 4), nullable=False, default=0.10)


class FactLiquidityMetric(Base):
    __tablename__ = "fact_liquidity_metric"

    metric_id = Column(String(64), primary_key=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    business_date = Column(Date, nullable=False, index=True)
    metric_name = Column(String(32), nullable=False, index=True)  # NSFR, LCR, ASF, RSF, HQLA, NET_OUTFLOWS
    numerator = Column(Numeric(24, 4), nullable=True)
    denominator = Column(Numeric(24, 4), nullable=True)
    ratio_value = Column(Numeric(10, 4), nullable=False)
    target_value = Column(Numeric(10, 4), nullable=True)
    regulatory_minimum = Column(Numeric(10, 4), nullable=False, default=100.0)
    calculation_version = Column(String(16), nullable=False, default="3.2.0")
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FactControlResult(Base):
    __tablename__ = "fact_control_result"

    result_id = Column(String(64), primary_key=True)
    run_id = Column(String(64), nullable=False, index=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    control_id = Column(String(32), nullable=False, index=True)
    control_name = Column(String(128), nullable=False)
    control_family = Column(String(32), nullable=False, index=True)
    severity = Column(String(16), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    expected_result = Column(String(256), nullable=False)
    actual_result = Column(String(256), nullable=False)
    status = Column(String(16), nullable=False, index=True)  # PASS, FAIL, WARNING, NOT_APPLICABLE
    evidence_reference = Column(String(256), nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FactException(Base):
    __tablename__ = "fact_exception"

    exception_id = Column(String(64), primary_key=True)
    control_id = Column(String(32), nullable=False, index=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    period = Column(String(16), nullable=False, index=True)
    severity = Column(String(16), nullable=False, index=True)
    description = Column(String(256), nullable=False)
    root_cause = Column(Text, nullable=False)
    affected_metric = Column(String(32), nullable=False, index=True)
    affected_report = Column(String(64), nullable=True)
    estimated_impact_usd = Column(Numeric(24, 4), nullable=True)
    status = Column(String(32), nullable=False, default="OPEN", index=True)  # OPEN, INVESTIGATING, REMEDIATED, AWAITING_REVIEW, RESOLVED, CLOSED
    owner = Column(String(64), nullable=False, default="Finance Control Team")
    resolution = Column(Text, nullable=True)
    reviewer = Column(String(64), nullable=True)
    resolved_at = Column(DateTime, nullable=True)


class FactStakeholderQuery(Base):
    __tablename__ = "fact_stakeholder_query"

    query_id = Column(String(64), primary_key=True)
    question = Column(String(512), nullable=False)
    requester = Column(String(64), nullable=False)  # e.g., 'Chief Risk Officer', 'Treasury Reviewer'
    requested_period = Column(String(16), nullable=False)
    metric = Column(String(32), nullable=False)
    reported_value = Column(Numeric(10, 4), nullable=False)
    recalculated_value = Column(Numeric(10, 4), nullable=False)
    variance = Column(Numeric(10, 4), nullable=False)
    investigation_status = Column(String(32), nullable=False, default="OPEN")  # OPEN, INVESTIGATING, RESOLVED, CLOSED
    root_cause = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)
    resolution = Column(Text, nullable=False)
    reviewer = Column(String(64), nullable=False, default="Lead Reviewer")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)


class FactReportingLine(Base):
    __tablename__ = "fact_reporting_line"

    line_id = Column(String(64), primary_key=True)
    snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False, index=True)
    report_code = Column(String(32), nullable=False, index=True)  # e.g., 'EXEC_SUMMARY', 'NSFR_TABLE', 'LCR_TABLE'
    schedule_code = Column(String(32), nullable=False)
    line_number = Column(String(16), nullable=False)
    label = Column(String(256), nullable=False)
    value_source = Column(String(64), nullable=False)
    metric = Column(String(32), nullable=True)
    raw_value = Column(Numeric(24, 4), nullable=False)
    weighted_value = Column(Numeric(24, 4), nullable=False)
    unit = Column(String(16), nullable=False, default="USD")
    validation_status = Column(String(16), nullable=False, default="VERIFIED")
    lineage_reference = Column(String(128), nullable=True)


class FactScenario(Base):
    __tablename__ = "fact_scenario"

    scenario_id = Column(String(64), primary_key=True)
    scenario_name = Column(String(128), nullable=False)
    description = Column(String(512), nullable=False)
    base_snapshot_id = Column(String(64), ForeignKey("fact_reporting_snapshot.snapshot_id"), nullable=False)
    parameters_json = Column(Text, nullable=False)  # JSON-encoded scenario shifts
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FactScenarioResult(Base):
    __tablename__ = "fact_scenario_result"

    result_id = Column(String(64), primary_key=True)
    scenario_id = Column(String(64), ForeignKey("fact_scenario.scenario_id"), nullable=False, index=True)
    metric_name = Column(String(32), nullable=False)
    base_value = Column(Numeric(10, 4), nullable=False)
    scenario_value = Column(Numeric(10, 4), nullable=False)
    delta_value = Column(Numeric(10, 4), nullable=False)
    delta_percent = Column(Numeric(10, 4), nullable=False)
    driver_summary = Column(Text, nullable=True)
