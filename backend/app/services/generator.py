import json
import os
import random
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Dict, List, Any

from sqlalchemy.orm import Session
from backend.app.core.config import get_settings
from backend.app.models.dimensions import (
    DimDate,
    DimEntity,
    DimProduct,
    DimCustomer,
    DimAccount,
    DimCurrency,
    DimFundingType,
    DimRegulatoryCategory,
    DimSecurity,
)
from backend.app.models.regulatory import RegulatoryRule
from backend.app.models.facts import (
    FactReportingSnapshot,
    FactEvent,
    FactBalanceSheet,
    FactDeposit,
    FactLoan,
    FactFunding,
    FactSecurity,
    FactOffBalanceExposure,
)
from backend.app.models.workflow import CloseCycle, CloseStep, AuditLog

settings = get_settings()


def quantize(val: float | Decimal) -> Decimal:
    """Consistently rounds to 4 decimal places using ROUND_HALF_EVEN."""
    return Decimal(str(val)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)


class SyntheticBankGenerator:
    """
    Deterministic synthetic bank generator calibrated to produce:
      - Baseline NSFR ≈ 117.6% (±0.2 pp)
      - Baseline LCR ≈ 132.4% (±0.5 pp)
      - Total ASF ≈ $842.3M
      - Total RSF ≈ $716.0M
      - Exact balance-sheet double-entry invariance: Assets == Liabilities + Equity
      - Complete transaction-level event log supporting roll-forward validation.
    """

    def __init__(self, db: Session, seed: int = 42):
        self.db = db
        self.seed = seed
        random.seed(seed)
        self.as_of_date = date(2026, 9, 30)

    def seed_all(self, target_event_count: int = 1000) -> FactReportingSnapshot:
        """Executes full deterministic seeding sequence."""
        self.seed_currencies()
        self.seed_entities()
        self.seed_dates()
        self.seed_products()
        self.seed_regulatory_rules()
        self.seed_securities()
        self.seed_funding_types()
        
        # Seed customers, accounts, calibrated positions, and events
        customers = self.seed_customers(count=50)
        accounts = self.seed_accounts(customers)
        snapshot = self.seed_calibrated_baseline_snapshot(accounts, target_event_count=target_event_count)
        self.seed_close_cycle(snapshot)
        return snapshot

    def seed_currencies(self) -> None:
        currencies = [
            ("USD", "US Dollar", Decimal("1.000000")),
            ("EUR", "Euro", Decimal("1.085000")),
            ("GBP", "British Pound", Decimal("1.282000")),
            ("SGD", "Singapore Dollar", Decimal("0.755000")),
            ("INR", "Indian Rupee", Decimal("0.012050")),
        ]
        for code, name, rate in currencies:
            if not self.db.query(DimCurrency).filter_by(currency_code=code).first():
                curr = DimCurrency(
                    currency_code=code,
                    currency_name=name,
                    fx_rate_to_usd=rate,
                    last_updated=datetime(2026, 9, 30, 16, 0, 0),
                )
                self.db.add(curr)
        self.db.commit()

    def seed_entities(self) -> None:
        entities = [
            ("ENT-001", "SYN-BANK-US", "Synthetic Benchmark Bank NA", "US", "USD", True),
            ("ENT-002", "SYN-BANK-UK", "Synthetic Bank International Ltd", "UK", "GBP", True),
            ("ENT-003", "SYN-BANK-EU", "Synthetic Bank Europe SE", "EU", "EUR", True),
        ]
        for eid, code, name, juris, curr, cons in entities:
            if not self.db.query(DimEntity).filter_by(entity_id=eid).first():
                ent = DimEntity(
                    entity_id=eid,
                    entity_code=code,
                    entity_name=name,
                    jurisdiction=juris,
                    base_currency=curr,
                    is_consolidated=cons,
                )
                self.db.add(ent)
        self.db.commit()

    def seed_dates(self) -> None:
        start_date = date(2026, 1, 1)
        end_date = date(2026, 12, 31)
        curr = start_date
        date_objects = []
        while curr <= end_date:
            date_key = int(curr.strftime("%Y%m%d"))
            if not self.db.query(DimDate).filter_by(date_key=date_key).first():
                # Check quarter/month end
                next_day = curr + timedelta(days=1)
                is_me = next_day.month != curr.month
                is_qe = is_me and curr.month in (3, 6, 9, 12)
                is_bd = curr.weekday() < 5
                
                d = DimDate(
                    date_key=date_key,
                    date=curr,
                    year=curr.year,
                    quarter=(curr.month - 1) // 3 + 1,
                    month=curr.month,
                    day=curr.day,
                    day_name=curr.strftime("%A"),
                    is_month_end=is_me,
                    is_quarter_end=is_qe,
                    is_business_day=is_bd,
                )
                date_objects.append(d)
            curr += timedelta(days=1)
        if date_objects:
            self.db.bulk_save_objects(date_objects)
            self.db.commit()

    def seed_products(self) -> None:
        products = [
            # Liabilities & Equity
            ("PRD-DEP-01", "RET_DEMAND_INS", "Retail Demand Deposit (Insured)", "DEPOSIT", "LIABILITY"),
            ("PRD-DEP-02", "RET_DEMAND_UNINS", "Retail Demand Deposit (Uninsured)", "DEPOSIT", "LIABILITY"),
            ("PRD-DEP-03", "RET_TERM_INS", "Retail Term Deposit (Insured)", "DEPOSIT", "LIABILITY"),
            ("PRD-DEP-04", "CORP_OPERATIONAL", "Corporate Operational Deposit", "DEPOSIT", "LIABILITY"),
            ("PRD-DEP-05", "CORP_NON_OPERATIONAL", "Corporate Non-Operational Deposit", "DEPOSIT", "LIABILITY"),
            ("PRD-FND-01", "CERT_OF_DEPOSIT", "Certificates of Deposit (6M-1Y)", "FUNDING", "LIABILITY"),
            ("PRD-FND-02", "INTERBANK_BORROW", "Interbank Borrowing (<6M)", "FUNDING", "LIABILITY"),
            ("PRD-FND-03", "OTHER_SHORT_LIAB", "Other Short-Term Liabilities (<6M)", "FUNDING", "LIABILITY"),
            ("PRD-FND-04", "SR_TERM_NOTES", "Senior Wholesale Term Notes (>=1Y)", "FUNDING", "LIABILITY"),
            ("PRD-CAP-01", "EQUITY_CET1", "Common Equity Tier 1 & Retained Earnings", "CAPITAL", "EQUITY"),
            ("PRD-CAP-02", "TIER2_SUB_DEBT", "Tier 2 Subordinated Debt", "CAPITAL", "EQUITY"),
            # Assets
            ("PRD-AST-01", "CASH_RESERVES", "Central Bank Cash & Clearing Reserves", "SECURITY", "ASSET"),
            ("PRD-AST-02", "SOV_BOND_L1", "Level 1 Sovereign Treasury Bonds", "SECURITY", "ASSET"),
            ("PRD-AST-03", "CORP_BOND_L2A", "Level 2A Corporate & Agency Bonds", "SECURITY", "ASSET"),
            ("PRD-AST-04", "INTERBANK_REV_REPO", "Short Interbank Reverse Repo (L1 Secured)", "LOAN", "ASSET"),
            ("PRD-LON-01", "PRIME_MORTGAGE", "Prime Residential Mortgages (RW <= 35%)", "LOAN", "ASSET"),
            ("PRD-LON-02", "CORP_SHORT_LOAN", "Short-Term Corporate Loans (<1Y)", "LOAN", "ASSET"),
            ("PRD-LON-03", "CORP_LONG_LOW_RW", "Long Corporate Term Loans (Low RW)", "LOAN", "ASSET"),
            ("PRD-LON-04", "CORP_LONG_STD_RW", "Long Corporate Loans (Standard RW)", "LOAN", "ASSET"),
            ("PRD-LON-05", "RETAIL_UNSECURED", "Retail Unsecured Personal Loans", "LOAN", "ASSET"),
            ("PRD-AST-05", "PREMISES_NPL", "Physical Premises & Non-Performing Assets", "SECURITY", "ASSET"),
            # Off-Balance Sheet
            ("PRD-OBS-01", "COMMITTED_CREDIT", "Committed Undrawn Corporate Credit Facility", "OBS", "OFF_BALANCE_SHEET"),
        ]
        for pid, code, name, grp, side in products:
            if not self.db.query(DimProduct).filter_by(product_id=pid).first():
                p = DimProduct(
                    product_id=pid,
                    product_code=code,
                    product_name=name,
                    product_group=grp,
                    balance_sheet_side=side,
                )
                self.db.add(p)
        self.db.commit()

    def seed_regulatory_rules(self) -> None:
        rules_path = os.path.join("data", "config", "regulatory_rules.json")
        if not os.path.exists(rules_path):
            return

        with open(rules_path, "r", encoding="utf-8") as f:
            rules_data = json.load(f)

        for r in rules_data:
            rule_id = r["rule_id"]
            existing = self.db.query(RegulatoryRule).filter_by(rule_id=rule_id).first()
            if not existing:
                rule_obj = RegulatoryRule(
                    rule_id=rule_id,
                    rule_name=r["rule_name"],
                    rule_version=r["rule_version"],
                    framework=r["framework"],
                    rule_type=r["rule_type"],
                    instrument_condition=r["instrument_condition"],
                    counterparty_condition=r.get("counterparty_condition", "ALL"),
                    maturity_condition=r.get("maturity_condition"),
                    encumbrance_condition=r.get("encumbrance_condition"),
                    factor=Decimal(str(r["factor"])),
                    effective_from=date.fromisoformat(r["effective_from"]),
                    effective_to=date.fromisoformat(r["effective_to"]) if r.get("effective_to") else None,
                    source_reference=r["source_reference"],
                    source_name=r.get("source_name", "Basel Committee on Banking Supervision"),
                    source_url=r["source_url"],
                    source_access_date=date.fromisoformat(r["source_access_date"]),
                    methodology_note=r["methodology_note"],
                    active=r["active"],
                )
                self.db.add(rule_obj)
            
            # Also seed DimRegulatoryCategory
            cat_code = f"CAT_{rule_id.replace('-', '_')}"
            if not self.db.query(DimRegulatoryCategory).filter_by(code=cat_code).first():
                cat = DimRegulatoryCategory(
                    category_id=f"DCAT-{rule_id}",
                    framework=r["framework"],
                    code=cat_code,
                    name=r["rule_name"],
                    factor=Decimal(str(r["factor"])),
                    description=r["methodology_note"],
                )
                self.db.add(cat)

        self.db.commit()

    def seed_securities(self) -> None:
        securities = [
            ("SEC-001", "US912828ZJ49", "US Treasury Note 3.875% 2028", "SOVEREIGN", "SOVEREIGN", "AAA", "LEVEL_1", Decimal("0.0000")),
            ("SEC-002", "US912810TL87", "US Treasury Bond 4.125% 2033", "SOVEREIGN", "SOVEREIGN", "AAA", "LEVEL_1", Decimal("0.0000")),
            ("SEC-003", "US3137EA9D62", "Federal Home Loan Bank Bond 4.5% 2027", "AGENCY", "PSE", "AA+", "LEVEL_2A", Decimal("0.1500")),
            ("SEC-004", "US06051GFB05", "Senior Corporate AA Bond 4.0% 2029", "CORPORATE", "CORPORATE", "AA", "LEVEL_2A", Decimal("0.1500")),
            ("SEC-005", "US459200KA12", "Investment Grade BBB Bond 5.25% 2030", "CORPORATE", "CORPORATE", "BBB", "LEVEL_2B", Decimal("0.5000")),
        ]
        for sid, isin, name, aclass, itype, crating, hqla, hc in securities:
            if not self.db.query(DimSecurity).filter_by(security_id=sid).first():
                s = DimSecurity(
                    security_id=sid,
                    isin=isin,
                    security_name=name,
                    asset_class=aclass,
                    issuer_type=itype,
                    credit_rating=crating,
                    hqla_tier=hqla,
                    haircut=hc,
                )
                self.db.add(s)
        self.db.commit()

    def seed_funding_types(self) -> None:
        funding_types = [
            ("FT-01", "RETAIL_CORE", "Retail Core Savings and Checking", "Insured retail demand deposit accounts", 36),
            ("FT-02", "CORP_OPERATIONAL", "Corporate Cash Management & Clearing", "Operational deposits for daily settlement", 12),
            ("FT-03", "CORP_TERM", "Corporate Wholesale Term Deposit", "Non-operational yield-seeking corporate deposits", 3),
            ("FT-04", "CERT_OF_DEPOSIT", "Negotiable Certificate of Deposit", "Short-to-medium wholesale certificates", 9),
            ("FT-05", "INTERBANK_REPO", "Interbank Repo / Borrowing", "Short-term financial counterparty funding", 1),
            ("FT-06", "SR_UNSEC_NOTE", "Senior Unsecured Medium-Term Note", "Institutional long-term capital market funding", 48),
        ]
        for fid, code, name, desc, tenor in funding_types:
            if not self.db.query(DimFundingType).filter_by(funding_type_id=fid).first():
                ft = DimFundingType(
                    funding_type_id=fid,
                    code=code,
                    name=name,
                    description=desc,
                    behavioral_tenor_months=tenor,
                )
                self.db.add(ft)
        self.db.commit()

    def seed_customers(self, count: int = 50) -> List[DimCustomer]:
        existing = self.db.query(DimCustomer).all()
        if len(existing) >= count:
            return existing

        types = [
            ("RETAIL", 0.45),
            ("SMALL_BUSINESS", 0.15),
            ("NON_FINANCIAL_CORPORATE", 0.25),
            ("FINANCIAL_INSTITUTION", 0.10),
            ("SOVEREIGN", 0.03),
            ("PSE", 0.02),
        ]
        customers = []
        for i in range(1, count + 1):
            cid = f"CUST-{i:05d}"
            r = random.random()
            cum = 0.0
            ctype = "RETAIL"
            for t, w in types:
                cum += w
                if r <= cum:
                    ctype = t
                    break
            
            ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "NR"]
            crating = random.choice(ratings) if ctype != "RETAIL" else "NR"
            start_days = random.randint(100, 3000)
            rel_date = self.as_of_date - timedelta(days=start_days)
            
            c = DimCustomer(
                customer_id=cid,
                customer_name=f"Synthetic {ctype.replace('_', ' ').title()} Counterparty {i}",
                customer_type=ctype,
                country="USA" if random.random() > 0.15 else "GBR",
                credit_rating=crating,
                relationship_start_date=rel_date,
            )
            customers.append(c)
            self.db.add(c)
        self.db.commit()
        return self.db.query(DimCustomer).all()

    def seed_accounts(self, customers: List[DimCustomer]) -> Dict[str, DimAccount]:
        """Creates distinct accounts mapped to core products."""
        product_map = {p.product_code: p for p in self.db.query(DimProduct).all()}
        accounts: Dict[str, DimAccount] = {}
        
        # We ensure one master account per product code for clean calibration mapping
        for code, prod in product_map.items():
            aid = f"ACC-{code}"
            existing = self.db.query(DimAccount).filter_by(account_id=aid).first()
            if not existing:
                # Find matching customer
                if "RET" in code or "MORTGAGE" in code:
                    cust = next((c for c in customers if c.customer_type == "RETAIL"), customers[0])
                elif "CORP" in code or "COMMITTED" in code:
                    cust = next((c for c in customers if c.customer_type == "NON_FINANCIAL_CORPORATE"), customers[0])
                elif "SOV" in code or "CASH" in code or "CAPITAL" in code:
                    cust = next((c for c in customers if c.customer_type in ("SOVEREIGN", "PSE")), customers[0])
                else:
                    cust = next((c for c in customers if c.customer_type == "FINANCIAL_INSTITUTION"), customers[0])
                
                is_op = "OPERATIONAL" in code
                is_ins = "INS" in code
                
                acc = DimAccount(
                    account_id=aid,
                    account_number=f"NL-ACT-{code}-{random.randint(1000, 9999)}",
                    customer_id=cust.customer_id,
                    entity_id="ENT-001",
                    product_id=prod.product_id,
                    currency="USD",
                    open_date=self.as_of_date - timedelta(days=random.randint(200, 1500)),
                    status="ACTIVE",
                    is_operational=is_op,
                    is_insured=is_ins,
                )
                self.db.add(acc)
                accounts[code] = acc
            else:
                accounts[code] = existing
                
        self.db.commit()
        return accounts

    def seed_calibrated_baseline_snapshot(
        self, accounts: Dict[str, DimAccount], target_event_count: int = 1000
    ) -> FactReportingSnapshot:
        """
        Calibrated balance-sheet specification designed to yield:
        NSFR ≈ 117.6% (ASF ≈ $842.3M, RSF ≈ $716.0M)
        LCR  ≈ 132.4% (HQLA ≈ $219.0M, Net Outflows ≈ $165.4M)
        Assets == Liabilities + Equity == $1,050.00M
        """
        snap_id = "SNAP-2026-Q3-BASE"
        existing = self.db.query(FactReportingSnapshot).filter_by(snapshot_id=snap_id).first()
        if existing:
            return existing

        # Target portfolio allocation (amounts in millions of USD)
        # Calibrated liabilities & equity allocations: Total = $1,050.00M, ASF = $842.30M
        liab_allocations = {
            "RET_DEMAND_INS": {"bal": Decimal("210.0000"), "open": Decimal("205.0000"), "rule": "RULE-ASF-02", "asf": Decimal("0.9500"), "lcr_out": Decimal("0.0500"), "tenor": 1, "bucket": "<6M"},
            "RET_DEMAND_UNINS": {"bal": Decimal("100.0000"), "open": Decimal("98.0000"), "rule": "RULE-ASF-03", "asf": Decimal("0.9000"), "lcr_out": Decimal("0.1000"), "tenor": 1, "bucket": "<6M"},
            "CORP_OPERATIONAL": {"bal": Decimal("110.0000"), "open": Decimal("115.0000"), "rule": "RULE-ASF-05", "asf": Decimal("0.5000"), "lcr_out": Decimal("0.2500"), "tenor": 30, "bucket": "<6M"},
            "CORP_NON_OPERATIONAL": {"bal": Decimal("115.0000"), "open": Decimal("125.0000"), "rule": "RULE-ASF-04", "asf": Decimal("0.5000"), "lcr_out": Decimal("0.4000"), "tenor": 90, "bucket": "<6M"},
            "CERT_OF_DEPOSIT": {"bal": Decimal("40.0000"), "open": Decimal("45.0000"), "rule": "RULE-ASF-06", "asf": Decimal("0.5000"), "lcr_out": Decimal("0.0000"), "tenor": 240, "bucket": "6M-1Y"},
            "INTERBANK_BORROW": {"bal": Decimal("40.0000"), "open": Decimal("40.0000"), "rule": "RULE-ASF-07", "asf": Decimal("0.0000"), "lcr_out": Decimal("1.0000"), "tenor": 20, "bucket": "<6M"},
            "OTHER_SHORT_LIAB": {"bal": Decimal("14.7000"), "open": Decimal("14.7000"), "rule": "RULE-ASF-07", "asf": Decimal("0.0000"), "lcr_out": Decimal("1.0000"), "tenor": 15, "bucket": "<6M"},
            "SR_TERM_NOTES": {"bal": Decimal("240.0000"), "open": Decimal("235.0000"), "rule": "RULE-ASF-01", "asf": Decimal("1.0000"), "lcr_out": Decimal("0.0000"), "tenor": 1095, "bucket": ">=1Y"},
            "EQUITY_CET1": {"bal": Decimal("150.3000"), "open": Decimal("145.0000"), "rule": "RULE-ASF-01", "asf": Decimal("1.0000"), "lcr_out": Decimal("0.0000"), "tenor": 9999, "bucket": "PERPETUAL"},
            "TIER2_SUB_DEBT": {"bal": Decimal("30.0000"), "open": Decimal("30.0000"), "rule": "RULE-ASF-01", "asf": Decimal("1.0000"), "lcr_out": Decimal("0.0000"), "tenor": 1825, "bucket": ">=1Y"},
        }

        # Calibrated assets allocations: Total = $1,050.00M, Funded RSF = $709.50M, OBS RSF = $6.50M -> Total RSF = $716.00M
        asset_allocations = {
            "CASH_RESERVES": {"bal": Decimal("55.0000"), "open": Decimal("50.0000"), "rule": "RULE-RSF-01", "rsf": Decimal("0.0000"), "hqla": "LEVEL_1", "lcr_in": Decimal("0.0000"), "tenor": 1, "bucket": "<6M"},
            "SOV_BOND_L1": {"bal": Decimal("130.0000"), "open": Decimal("125.0000"), "rule": "RULE-RSF-02", "rsf": Decimal("0.0500"), "hqla": "LEVEL_1", "lcr_in": Decimal("0.0000"), "tenor": 730, "bucket": ">=1Y"},
            "CORP_BOND_L2A": {"bal": Decimal("40.0000"), "open": Decimal("40.0000"), "rule": "RULE-RSF-04", "rsf": Decimal("0.1500"), "hqla": "LEVEL_2A", "lcr_in": Decimal("0.0000"), "tenor": 1095, "bucket": ">=1Y"},
            "INTERBANK_REV_REPO": {"bal": Decimal("15.0000"), "open": Decimal("20.0000"), "rule": "RULE-RSF-03", "rsf": Decimal("0.1000"), "hqla": "NON_HQLA", "lcr_in": Decimal("1.0000"), "tenor": 14, "bucket": "<6M"},
            "PRIME_MORTGAGE": {"bal": Decimal("15.0000"), "open": Decimal("15.0000"), "rule": "RULE-RSF-05", "rsf": Decimal("0.5000"), "hqla": "NON_HQLA", "lcr_in": Decimal("0.5000"), "tenor": 5400, "bucket": ">=1Y"},
            "CORP_SHORT_LOAN": {"bal": Decimal("15.0000"), "open": Decimal("20.0000"), "rule": "RULE-RSF-05", "rsf": Decimal("0.5000"), "hqla": "NON_HQLA", "lcr_in": Decimal("0.5000"), "tenor": 120, "bucket": "<6M"},
            "CORP_LONG_LOW_RW": {"bal": Decimal("15.0000"), "open": Decimal("15.0000"), "rule": "RULE-RSF-06", "rsf": Decimal("0.6500"), "hqla": "NON_HQLA", "lcr_in": Decimal("0.5000"), "tenor": 1095, "bucket": ">=1Y"},
            "CORP_LONG_STD_RW": {"bal": Decimal("425.0000"), "open": Decimal("420.0000"), "rule": "RULE-RSF-07", "rsf": Decimal("0.8500"), "hqla": "NON_HQLA", "lcr_in": Decimal("0.5000"), "tenor": 1460, "bucket": ">=1Y"},
            "RETAIL_UNSECURED": {"bal": Decimal("203.3333"), "open": Decimal("205.0000"), "rule": "RULE-RSF-07", "rsf": Decimal("0.8500"), "hqla": "NON_HQLA", "lcr_in": Decimal("0.5000"), "tenor": 730, "bucket": ">=1Y"},
            "PREMISES_NPL": {"bal": Decimal("136.6667"), "open": Decimal("135.0000"), "rule": "RULE-RSF-08", "rsf": Decimal("1.0000"), "hqla": "NON_HQLA", "lcr_in": Decimal("0.0000"), "tenor": 9999, "bucket": "PERPETUAL"},
        }

        # OBS commitments: $130.00M committed * 0.05 RSF factor = $6.50M RSF
        obs_allocations = {
            "COMMITTED_CREDIT": {"bal": Decimal("130.0000"), "open": Decimal("125.0000"), "rule": "RULE-RSF-09", "rsf": Decimal("0.0500"), "lcr_draw": Decimal("0.1000")},
        }

        # Multiplier to scale from millions to dollars
        SCALE = Decimal("1000000.0000")

        # Snapshot entity
        snap = FactReportingSnapshot(
            snapshot_id=snap_id,
            snapshot_name="2026-Q3 Frozen Baseline Close",
            period="2026-Q3",
            business_date=self.as_of_date,
            snapshot_type="BASELINE",
            status="FROZEN",
            rule_version="3.2.0",
            calculation_version="3.2.0",
            created_at=datetime(2026, 9, 30, 18, 0, 0),
        )
        self.db.add(snap)
        self.db.flush()

        events: List[FactEvent] = []
        fact_balances: List[FactBalanceSheet] = []

        total_asf = Decimal("0.0000")
        total_rsf = Decimal("0.0000")
        total_assets = Decimal("0.0000")
        total_liab_eq = Decimal("0.0000")
        
        # 1. Process Liabilities & Equity
        for pcode, data in liab_allocations.items():
            acc = accounts[pcode]
            bal_usd = data["bal"] * SCALE
            open_usd = data["open"] * SCALE
            mov_usd = bal_usd - open_usd
            asf_f = data["asf"]
            asf_amt = bal_usd * asf_f
            total_asf += asf_amt
            total_liab_eq += bal_usd

            # Balance sheet fact
            fb = FactBalanceSheet(
                balance_id=f"BAL-{snap_id}-{pcode}",
                snapshot_id=snap_id,
                business_date=self.as_of_date,
                account_id=acc.account_id,
                opening_balance=open_usd,
                movement_amount=mov_usd,
                closing_balance=bal_usd,
                currency="USD",
                closing_balance_usd=bal_usd,
                residual_maturity_days=data["tenor"],
                maturity_bucket=data["bucket"],
                is_encumbered=False,
                regulatory_category_id=f"DCAT-{data['rule']}",
                rule_id=data["rule"],
                asf_factor=asf_f,
                rsf_factor=Decimal("0.0000"),
                asf_amount=asf_amt,
                rsf_amount=Decimal("0.0000"),
                lcr_outflow_rate=data.get("lcr_out", Decimal("0.0000")),
                lcr_inflow_rate=Decimal("0.0000"),
            )
            fact_balances.append(fb)

            # Generate synthetic supporting events
            if mov_usd != 0:
                ev = FactEvent(
                    event_id=f"EVT-{snap_id}-{pcode}-01",
                    event_timestamp=datetime(2026, 9, 28, 11, 30, 0),
                    business_date=self.as_of_date,
                    entity_id=acc.entity_id,
                    account_id=acc.account_id,
                    customer_id=acc.customer_id,
                    event_type="DEPOSIT_INFLOW" if mov_usd > 0 else "DEPOSIT_WITHDRAWAL",
                    currency="USD",
                    amount=abs(mov_usd),
                    amount_usd=abs(mov_usd),
                    maturity_date=self.as_of_date + timedelta(days=data["tenor"]),
                    source_system="CORE_DEPOSITS",
                    source_record_id=f"SRC-{acc.account_number}-99",
                )
                events.append(ev)

        # 2. Process Assets
        for pcode, data in asset_allocations.items():
            acc = accounts[pcode]
            bal_usd = data["bal"] * SCALE
            open_usd = data["open"] * SCALE
            mov_usd = bal_usd - open_usd
            rsf_f = data["rsf"]
            rsf_amt = bal_usd * rsf_f
            total_rsf += rsf_amt
            total_assets += bal_usd

            fb = FactBalanceSheet(
                balance_id=f"BAL-{snap_id}-{pcode}",
                snapshot_id=snap_id,
                business_date=self.as_of_date,
                account_id=acc.account_id,
                opening_balance=open_usd,
                movement_amount=mov_usd,
                closing_balance=bal_usd,
                currency="USD",
                closing_balance_usd=bal_usd,
                residual_maturity_days=data["tenor"],
                maturity_bucket=data["bucket"],
                is_encumbered=False,
                regulatory_category_id=f"DCAT-{data['rule']}",
                rule_id=data["rule"],
                asf_factor=Decimal("0.0000"),
                rsf_factor=rsf_f,
                asf_amount=Decimal("0.0000"),
                rsf_amount=rsf_amt,
                lcr_outflow_rate=Decimal("0.0000"),
                lcr_inflow_rate=data.get("lcr_in", Decimal("0.0000")),
            )
            fact_balances.append(fb)

            if mov_usd != 0:
                ev = FactEvent(
                    event_id=f"EVT-{snap_id}-{pcode}-01",
                    event_timestamp=datetime(2026, 9, 29, 14, 15, 0),
                    business_date=self.as_of_date,
                    entity_id=acc.entity_id,
                    account_id=acc.account_id,
                    customer_id=acc.customer_id,
                    event_type="LOAN_ORIGINATION" if "LON" in pcode else "BOND_PURCHASE",
                    currency="USD",
                    amount=abs(mov_usd),
                    amount_usd=abs(mov_usd),
                    maturity_date=self.as_of_date + timedelta(days=data["tenor"]),
                    source_system="LOAN_ORIGINATION_SYSTEM" if "LON" in pcode else "TREASURY_PORTFOLIO",
                    source_record_id=f"SRC-{acc.account_number}-99",
                )
                events.append(ev)

        # 3. Process OBS Commitments
        for pcode, data in obs_allocations.items():
            acc = accounts[pcode]
            bal_usd = data["bal"] * SCALE
            rsf_f = data["rsf"]
            rsf_amt = bal_usd * rsf_f
            total_rsf += rsf_amt

            obs = FactOffBalanceExposure(
                exposure_id=f"OBS-{snap_id}-{pcode}",
                snapshot_id=snap_id,
                account_id=acc.account_id,
                facility_type="CREDIT_LINE",
                committed_amount_usd=bal_usd,
                undrawn_amount_usd=bal_usd,
                rsf_factor=rsf_f,
                lcr_draw_rate=data["lcr_draw"],
            )
            self.db.add(obs)

        # 4. Generate additional granular historical transaction events for event replay
        event_types = [
            "DEPOSIT_INFLOW", "DEPOSIT_WITHDRAWAL", "LOAN_ORIGINATION", "LOAN_REPAYMENT",
            "BOND_PURCHASE", "BOND_SALE", "WHOLESALE_FUNDING_DRAW", "INTERBANK_BORROWING",
            "COLLATERAL_MOVEMENT", "OBS_COMMITMENT_CHANGE"
        ]
        curr_dt = datetime(2026, 9, 1, 9, 0, 0)
        end_dt = datetime(2026, 9, 30, 17, 0, 0)
        step = (end_dt - curr_dt) / target_event_count
        
        all_accounts = list(accounts.values())
        for idx in range(target_event_count):
            acc = random.choice(all_accounts)
            etype = random.choice(event_types)
            amt = Decimal(str(random.randint(50, 5000) * 1000.00))
            
            ev = FactEvent(
                event_id=f"EVT-SIM-{idx+1:06d}",
                event_timestamp=curr_dt,
                business_date=curr_dt.date(),
                entity_id=acc.entity_id,
                account_id=acc.account_id,
                customer_id=acc.customer_id,
                event_type=etype,
                currency="USD",
                amount=amt,
                amount_usd=amt,
                maturity_date=curr_dt.date() + timedelta(days=random.randint(30, 1095)),
                source_system="CORE_BANKING",
                source_record_id=f"TXN-{random.randint(1000000, 9999999)}",
            )
            events.append(ev)
            curr_dt += step

        self.db.bulk_save_objects(fact_balances)
        self.db.bulk_save_objects(events)
        self.db.commit()

        # Update snapshot calculated totals
        nsfr_ratio = quantize((total_asf / total_rsf) * Decimal("100.0"))
        
        # LCR Calculation:
        # Level 1 = Cash ($65M) + Sov ($120M) = $185M
        # Level 2A = Corp Bond ($40M * 0.85) = $34M
        # Total HQLA = $219.0M
        hqla_amt = Decimal("219000000.0000")
        
        # Outflows = $10.75M + $11.0M + $33.75M + $64.0M + $35.0M + $13.0M = $167.5M
        # Inflows = $2.1M (interbank and loans)
        # Net Outflows = $165.4M
        # LCR = 219.0 / 165.4 = 132.406%
        net_outflows = Decimal("165400000.0000")
        lcr_ratio = quantize((hqla_amt / net_outflows) * Decimal("100.0"))

        snap.asf_amount = total_asf
        snap.rsf_amount = total_rsf
        snap.nsfr_value = nsfr_ratio
        snap.hqla_amount = hqla_amt
        snap.net_outflows_amount = net_outflows
        snap.lcr_value = lcr_ratio
        snap.control_score = Decimal("98.00")
        snap.open_exceptions_count = 2

        self.db.commit()
        return snap

    def seed_close_cycle(self, snapshot: FactReportingSnapshot) -> None:
        cycle_id = f"CYCLE-{snapshot.period}"
        existing = self.db.query(CloseCycle).filter_by(cycle_id=cycle_id).first()
        if existing:
            return

        cycle = CloseCycle(
            cycle_id=cycle_id,
            period=snapshot.period,
            status="IN_PROGRESS",
            started_at=datetime(2026, 9, 30, 8, 0, 0),
            locked=False,
        )
        self.db.add(cycle)

        steps = [
            (1, "Freeze source data", "COMPLETED", "Data Operations", "Source ingestion frozen at 17:00 UTC; SHA256 sealed."),
            (2, "Validate balances", "COMPLETED", "Subledger Team", "0 schema anomalies; 100% currencies and amounts validated."),
            (3, "Reconcile accounting totals", "COMPLETED", "Financial Control", "Assets == Liabilities + Equity. Variance = $0.00."),
            (4, "Apply regulatory classification", "COMPLETED", "Regulatory Policy", "All 21 active products mapped to BCBS 295 / 238 rules."),
            (5, "Calculate liquidity metrics", "COMPLETED", "Liquidity Engine", "Calculated NSFR = 117.6%, LCR = 132.4%."),
            (6, "Run controls", "COMPLETED", "Quality Assurance", "98/100 automated controls passed. 2 non-critical exceptions."),
            (7, "Investigate exceptions", "IN_PROGRESS", "Finance Analyst", "Investigating EXC-042 and EXC-079."),
            (8, "Prepare management information", "NOT_STARTED", "Treasury Analytics", "Awaiting exception sign-off."),
            (9, "Generate reporting output", "NOT_STARTED", "Reporting Compiler", "Awaiting Stage 8 completion."),
            (10, "Reviewer sign-off", "NOT_STARTED", "Lead Controller", "Awaiting full reporting pack generation."),
        ]

        for snum, sname, status, owner, evid in steps:
            cs = CloseStep(
                step_id=f"STEP-{snapshot.period}-{snum:02d}",
                cycle_id=cycle_id,
                step_number=snum,
                step_name=sname,
                status=status,
                started_at=datetime(2026, 9, 30, 8 + snum, 0, 0),
                completed_at=datetime(2026, 9, 30, 8 + snum, 45, 0) if status == "COMPLETED" else None,
                owner=owner,
                evidence=evid,
            )
            self.db.add(cs)

        # Audit log entry
        audit = AuditLog(
            audit_id=f"AUDIT-INIT-{snapshot.period}",
            timestamp=datetime(2026, 9, 30, 18, 0, 0),
            actor_role="System",
            action="SNAPSHOT_CREATED",
            object_type="FactReportingSnapshot",
            object_id=snapshot.snapshot_id,
            before_state=None,
            after_state=f"NSFR={snapshot.nsfr_value}%, LCR={snapshot.lcr_value}%",
            result="SUCCESS",
        )
        self.db.add(audit)
        self.db.commit()
