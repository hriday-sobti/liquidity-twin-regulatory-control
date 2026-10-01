from decimal import Decimal, ROUND_HALF_EVEN
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.facts import (
    FactBalanceSheet,
    FactOffBalanceExposure,
    FactLiquidityMetric,
    FactReportingSnapshot,
)
from backend.app.models.dimensions import DimAccount, DimProduct


class LcrCalculationEngine:
    """
    Transparent Liquidity Coverage Ratio (LCR) simulation engine conforming to BCBS 238.
    Calculates HQLA buffer (Level 1, 2A, 2B), 30-day gross cash outflows,
    contractual inflows subject to 75% ceiling, net outflows, and final ratio.
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_lcr(self, snapshot_id: str, persist: bool = False) -> Dict[str, Any]:
        balances = self.db.query(FactBalanceSheet).filter_by(snapshot_id=snapshot_id).all()
        obs_items = self.db.query(FactOffBalanceExposure).filter_by(snapshot_id=snapshot_id).all()

        # 1. HQLA Stock
        level1_gross = Decimal("0.0")
        level2a_gross = Decimal("0.0")
        level2b_gross = Decimal("0.0")

        # 2. Outflows
        outflows: Dict[str, Dict[str, Any]] = {
            "Stable Retail Deposits (5%)": {"raw": Decimal("0.0"), "rate": 0.05, "weighted": Decimal("0.0")},
            "Less Stable Retail Deposits (10%)": {"raw": Decimal("0.0"), "rate": 0.10, "weighted": Decimal("0.0")},
            "Operational Wholesale Deposits (25%)": {"raw": Decimal("0.0"), "rate": 0.25, "weighted": Decimal("0.0")},
            "Non-Operational Corporate Funding (40%)": {"raw": Decimal("0.0"), "rate": 0.40, "weighted": Decimal("0.0")},
            "Maturing Wholesale & Short Interbank Funding (100%)": {"raw": Decimal("0.0"), "rate": 1.00, "weighted": Decimal("0.0")},
            "Committed Undrawn Facilities Drawdown (10%)": {"raw": Decimal("0.0"), "rate": 0.10, "weighted": Decimal("0.0")},
        }

        # 3. Inflows
        inflows: Dict[str, Dict[str, Any]] = {
            "Retail & Corporate Performing Loan Repayments (50%)": {"raw": Decimal("0.0"), "rate": 0.50, "weighted": Decimal("0.0")},
            "Financial Counterparty Inflows < 30D (100%)": {"raw": Decimal("0.0"), "rate": 1.00, "weighted": Decimal("0.0")},
        }

        for b in balances:
            acc = self.db.query(DimAccount).filter_by(account_id=b.account_id).first()
            pcode = acc.product.product_code if acc and acc.product else ""
            side = acc.product.balance_sheet_side if acc and acc.product else ""

            # HQLA aggregation
            if side == "ASSET":
                if pcode in ("CASH_RESERVES", "SOV_BOND_L1"):
                    level1_gross += b.closing_balance_usd
                elif pcode == "CORP_BOND_L2A":
                    level2a_gross += b.closing_balance_usd

                # Inflow estimation for 30D window
                if pcode == "INTERBANK_REV_REPO":
                    inflows["Financial Counterparty Inflows < 30D (100%)"]["raw"] += b.closing_balance_usd * Decimal("0.10")
                elif pcode in ("CORP_SHORT_LOAN", "PRIME_MORTGAGE"):
                    inflows["Retail & Corporate Performing Loan Repayments (50%)"]["raw"] += b.closing_balance_usd * Decimal("0.02")

            # Outflows aggregation
            elif side in ("LIABILITY", "EQUITY"):
                if pcode == "RET_DEMAND_INS":
                    outflows["Stable Retail Deposits (5%)"]["raw"] += b.closing_balance_usd
                elif pcode == "RET_DEMAND_UNINS":
                    outflows["Less Stable Retail Deposits (10%)"]["raw"] += b.closing_balance_usd
                elif pcode == "CORP_OPERATIONAL":
                    outflows["Operational Wholesale Deposits (25%)"]["raw"] += b.closing_balance_usd
                elif pcode == "CORP_NON_OPERATIONAL":
                    outflows["Non-Operational Corporate Funding (40%)"]["raw"] += b.closing_balance_usd
                elif pcode == "CERT_OF_DEPOSIT":
                    # 13.5% of medium-term CDs mature within the 30-day LCR stress window
                    outflows["Maturing Wholesale & Short Interbank Funding (100%)"]["raw"] += b.closing_balance_usd * Decimal("0.1350")
                elif pcode in ("INTERBANK_BORROW", "OTHER_SHORT_LIAB"):
                    outflows["Maturing Wholesale & Short Interbank Funding (100%)"]["raw"] += b.closing_balance_usd

        # Committed facilities drawdown
        for obs in obs_items:
            outflows["Committed Undrawn Facilities Drawdown (10%)"]["raw"] += obs.committed_amount_usd

        # Calculate weighted outflows
        total_gross_outflows = Decimal("0.0")
        outflow_breakdown = []
        for name, data in outflows.items():
            w = data["raw"] * Decimal(str(data["rate"]))
            data["weighted"] = w
            total_gross_outflows += w
            outflow_breakdown.append({
                "category": name,
                "raw_amount": float(data["raw"]),
                "run_off_rate": data["rate"],
                "outflow_amount": float(w),
            })

        # Calculate weighted inflows
        total_gross_inflows = Decimal("0.0")
        inflow_breakdown = []
        for name, data in inflows.items():
            w = data["raw"] * Decimal(str(data["rate"]))
            data["weighted"] = w
            total_gross_inflows += w
            inflow_breakdown.append({
                "category": name,
                "raw_amount": float(data["raw"]),
                "inflow_rate": data["rate"],
                "inflow_amount": float(w),
            })

        # HQLA haircuts: Level 1 (0%), Level 2A (15%), Level 2B (50%)
        level1_post_haircut = level1_gross * Decimal("1.00")
        level2a_post_haircut = level2a_gross * Decimal("0.85")
        level2b_post_haircut = level2b_gross * Decimal("0.50")
        total_hqla = level1_post_haircut + level2a_post_haircut + level2b_post_haircut

        # Inflow cap: max 75% of total gross outflows
        inflow_cap = total_gross_outflows * Decimal("0.75")
        eligible_inflows = min(total_gross_inflows, inflow_cap)
        net_cash_outflows = total_gross_outflows - eligible_inflows

        if net_cash_outflows <= Decimal("0.0"):
            lcr_ratio = Decimal("0.0000")
        else:
            lcr_ratio = (total_hqla / net_cash_outflows) * Decimal("100.0")

        lcr_ratio_quant = lcr_ratio.quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        buffer_margin = lcr_ratio_quant - Decimal("100.0000")
        is_compliant = (lcr_ratio_quant >= Decimal("100.0000"))

        result = {
            "snapshot_id": snapshot_id,
            "metric_name": "LCR",
            "total_hqla": float(total_hqla),
            "level1_hqla": float(level1_post_haircut),
            "level2a_hqla": float(level2a_post_haircut),
            "level2b_hqla": float(level2b_post_haircut),
            "gross_cash_outflows": float(total_gross_outflows),
            "gross_cash_inflows": float(total_gross_inflows),
            "inflow_cap_limit": float(inflow_cap),
            "eligible_inflows": float(eligible_inflows),
            "net_cash_outflows": float(net_cash_outflows),
            "lcr_percentage": float(lcr_ratio_quant),
            "regulatory_minimum_percentage": 100.0,
            "buffer_percentage": float(buffer_margin),
            "is_compliant": is_compliant,
            "outflow_breakdown": outflow_breakdown,
            "inflow_breakdown": inflow_breakdown,
            "calculated_at": datetime.utcnow().isoformat(),
        }

        if persist:
            snap = self.db.query(FactReportingSnapshot).filter_by(snapshot_id=snapshot_id).first()
            if snap:
                snap.hqla_amount = total_hqla
                snap.net_outflows_amount = net_cash_outflows
                snap.lcr_value = lcr_ratio_quant

                metric_id = f"METRIC-{snapshot_id}-LCR"
                existing_m = self.db.query(FactLiquidityMetric).filter_by(metric_id=metric_id).first()
                if not existing_m:
                    m = FactLiquidityMetric(
                        metric_id=metric_id,
                        snapshot_id=snapshot_id,
                        business_date=snap.business_date,
                        metric_name="LCR",
                        numerator=total_hqla,
                        denominator=net_cash_outflows,
                        ratio_value=lcr_ratio_quant,
                        target_value=Decimal("132.4000"),
                        regulatory_minimum=Decimal("100.0000"),
                        calculation_version="3.2.0",
                        calculated_at=datetime.utcnow(),
                    )
                    self.db.add(m)
                else:
                    existing_m.numerator = total_hqla
                    existing_m.denominator = net_cash_outflows
                    existing_m.ratio_value = lcr_ratio_quant
                    existing_m.calculated_at = datetime.utcnow()

                self.db.commit()

        return result
