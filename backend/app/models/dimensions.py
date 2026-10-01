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
)
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class DimDate(Base):
    __tablename__ = "dim_date"

    date_key = Column(Integer, primary_key=True)  # YYYYMMDD
    date = Column(Date, unique=True, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    day_name = Column(String(16), nullable=False)
    is_month_end = Column(Boolean, default=False, nullable=False)
    is_quarter_end = Column(Boolean, default=False, nullable=False)
    is_business_day = Column(Boolean, default=True, nullable=False)


class DimEntity(Base):
    __tablename__ = "dim_entity"

    entity_id = Column(String(64), primary_key=True)
    entity_code = Column(String(32), unique=True, nullable=False)
    entity_name = Column(String(128), nullable=False)
    jurisdiction = Column(String(32), nullable=False)
    base_currency = Column(String(3), nullable=False, default="USD")
    is_consolidated = Column(Boolean, default=True, nullable=False)


class DimProduct(Base):
    __tablename__ = "dim_product"

    product_id = Column(String(64), primary_key=True)
    product_code = Column(String(32), unique=True, nullable=False)
    product_name = Column(String(128), nullable=False)
    # DEPOSIT, LOAN, SECURITY, FUNDING, CAPITAL, OBS
    product_group = Column(String(32), nullable=False, index=True)
    # ASSET, LIABILITY, EQUITY, OFF_BALANCE_SHEET
    balance_sheet_side = Column(String(32), nullable=False, index=True)


class DimCustomer(Base):
    __tablename__ = "dim_customer"

    customer_id = Column(String(64), primary_key=True)
    customer_name = Column(String(128), nullable=False)
    # RETAIL, SMALL_BUSINESS, NON_FINANCIAL_CORPORATE, FINANCIAL_INSTITUTION, SOVEREIGN, PSE
    customer_type = Column(String(32), nullable=False, index=True)
    country = Column(String(3), nullable=False)  # ISO-3166 alpha-3
    credit_rating = Column(String(8), nullable=False, default="NR")
    relationship_start_date = Column(Date, nullable=False)

    accounts = relationship("DimAccount", back_populates="customer")


class DimAccount(Base):
    __tablename__ = "dim_account"

    account_id = Column(String(64), primary_key=True)
    account_number = Column(String(64), unique=True, nullable=False, index=True)
    customer_id = Column(String(64), ForeignKey("dim_customer.customer_id"), nullable=False, index=True)
    entity_id = Column(String(64), ForeignKey("dim_entity.entity_id"), nullable=False, index=True)
    product_id = Column(String(64), ForeignKey("dim_product.product_id"), nullable=False, index=True)
    currency = Column(String(3), nullable=False, default="USD")
    open_date = Column(Date, nullable=False)
    status = Column(String(16), nullable=False, default="ACTIVE")
    is_operational = Column(Boolean, default=False, nullable=False)
    is_insured = Column(Boolean, default=False, nullable=False)

    customer = relationship("DimCustomer", back_populates="accounts")
    entity = relationship("DimEntity")
    product = relationship("DimProduct")

    __table_args__ = (
        Index("idx_account_lookup", "customer_id", "product_id", "status"),
    )


class DimCurrency(Base):
    __tablename__ = "dim_currency"

    currency_code = Column(String(3), primary_key=True)  # USD, EUR, GBP, SGD, INR
    currency_name = Column(String(64), nullable=False)
    fx_rate_to_usd = Column(Numeric(18, 6), nullable=False, default=1.0)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)


class DimFundingType(Base):
    __tablename__ = "dim_funding_type"

    funding_type_id = Column(String(64), primary_key=True)
    code = Column(String(32), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(256), nullable=True)
    behavioral_tenor_months = Column(Integer, nullable=False, default=1)


class DimRegulatoryCategory(Base):
    __tablename__ = "dim_regulatory_category"

    category_id = Column(String(64), primary_key=True)
    framework = Column(String(16), nullable=False)  # NSFR, LCR
    code = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    factor = Column(Numeric(6, 4), nullable=False)  # 0.0000 to 1.0000
    description = Column(String(512), nullable=True)


class DimSecurity(Base):
    __tablename__ = "dim_security"

    security_id = Column(String(64), primary_key=True)
    isin = Column(String(12), unique=True, nullable=False, index=True)
    security_name = Column(String(128), nullable=False)
    asset_class = Column(String(32), nullable=False)  # SOVEREIGN, AGENCY, CORPORATE, EQUITY
    issuer_type = Column(String(32), nullable=False)
    credit_rating = Column(String(8), nullable=False)
    hqla_tier = Column(String(16), nullable=False, default="NON_HQLA")  # LEVEL_1, LEVEL_2A, LEVEL_2B, NON_HQLA
    haircut = Column(Numeric(6, 4), nullable=False, default=0.0)
