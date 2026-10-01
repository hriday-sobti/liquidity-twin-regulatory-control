from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from backend.app.models.dimensions import DimAccount
from backend.app.models.facts import FactBalanceSheet, FactOffBalanceExposure


class RsfCalculationEngine:
    """
    Deterministic Required Stable Funding (RSF) calculation engine conforming to BCBS 295.
    Calculates weighted illiquidity funding requirements across assets and off-balance-sheet commitments.
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_rsf(self, snapshot_id: str) -> dict[str, Any]:
        balances = self.db.query(FactBalanceSheet).filter_by(snapshot_id=snapshot_id).all()
        obs_items = self.db.query(FactOffBalanceExposure).filter_by(snapshot_id=snapshot_id).all()

        categories: dict[str, dict[str, Any]] = {
            "Cash & Central Bank Reserves (0%)": {"raw_amount": Decimal("0.0"), "rsf_amount": Decimal("0.0"), "factor": 0.00, "positions_count": 0},
            "Level 1 Sovereign Securities (5%)": {"raw_amount": Decimal("0.0"), "rsf_amount": Decimal("0.0"), "factor": 0.05, "positions_count": 0},
            "Loans to Financial Institutions Secured by L1 (10%)": {"raw_amount": Decimal("0.0"), "rsf_amount": Decimal("0.0"), "factor": 0.10, "positions_count": 0},
            "Level 2A Assets & Short Financial Loans (15%)": {"raw_amount": Decimal("0.0"), "rsf_amount": Decimal("0.0"), "factor": 0.15, "positions_count": 0},
            "Prime Residential Mortgages & Short Loans (50%)": {"raw_amount": Decimal("0.0"), "rsf_amount": Decimal("0.0"), "factor": 0.50, "positions_count": 0},
            "Non-Prime Mortgages & Corporate Loans Low RW (65%)": {"raw_amount": Decimal("0.0"), "rsf_amount": Decimal("0.0"), "factor": 0.65, "positions_count": 0},
            "Standard Long Corporate & Retail Loans (85%)": {"raw_amount": Decimal("0.0"), "rsf_amount": Decimal("0.0"), "factor": 0.85, "positions_count": 0},
            "Other Assets, NPLs & Fixed Premises (100%)": {"raw_amount": Decimal("0.0"), "rsf_amount": Decimal("0.0"), "factor": 1.00, "positions_count": 0},
            "Committed Undrawn Off-Balance Facilities (5%)": {"raw_amount": Decimal("0.0"), "rsf_amount": Decimal("0.0"), "factor": 0.05, "positions_count": 0},
        }

        total_rsf = Decimal("0.0000")
        total_funded_assets = Decimal("0.0000")
        total_obs = Decimal("0.0000")
        position_details = []

        for b in balances:
            acc = self.db.query(DimAccount).filter_by(account_id=b.account_id).first()
            side = acc.product.balance_sheet_side if acc and acc.product else "UNKNOWN"
            pcode = acc.product.product_code if acc and acc.product else "UNKNOWN"

            if side != "ASSET":
                continue

            total_funded_assets += b.closing_balance_usd
            rsf_val = b.rsf_amount
            total_rsf += rsf_val

            cat_key = "Other Assets, NPLs & Fixed Premises (100%)"
            if b.rule_id == "RULE-RSF-01":
                cat_key = "Cash & Central Bank Reserves (0%)"
            elif b.rule_id == "RULE-RSF-02":
                cat_key = "Level 1 Sovereign Securities (5%)"
            elif b.rule_id == "RULE-RSF-03":
                cat_key = "Loans to Financial Institutions Secured by L1 (10%)"
            elif b.rule_id == "RULE-RSF-04":
                cat_key = "Level 2A Assets & Short Financial Loans (15%)"
            elif b.rule_id == "RULE-RSF-05":
                cat_key = "Prime Residential Mortgages & Short Loans (50%)"
            elif b.rule_id == "RULE-RSF-06":
                cat_key = "Non-Prime Mortgages & Corporate Loans Low RW (65%)"
            elif b.rule_id == "RULE-RSF-07":
                cat_key = "Standard Long Corporate & Retail Loans (85%)"
            elif b.rule_id == "RULE-RSF-08":
                cat_key = "Other Assets, NPLs & Fixed Premises (100%)"

            categories[cat_key]["raw_amount"] += b.closing_balance_usd
            categories[cat_key]["rsf_amount"] += rsf_val
            categories[cat_key]["positions_count"] += 1

            position_details.append({
                "account_id": b.account_id,
                "product_code": pcode,
                "raw_amount": float(b.closing_balance_usd),
                "factor": float(b.rsf_factor),
                "rsf_amount": float(rsf_val),
                "rule_id": b.rule_id,
            })

        # Add OBS commitments
        for obs in obs_items:
            total_obs += obs.committed_amount_usd
            obs_rsf_val = obs.committed_amount_usd * obs.rsf_factor
            total_rsf += obs_rsf_val

            categories["Committed Undrawn Off-Balance Facilities (5%)"]["raw_amount"] += obs.committed_amount_usd
            categories["Committed Undrawn Off-Balance Facilities (5%)"]["rsf_amount"] += obs_rsf_val
            categories["Committed Undrawn Off-Balance Facilities (5%)"]["positions_count"] += 1

            position_details.append({
                "account_id": obs.account_id,
                "product_code": "COMMITTED_FACILITY",
                "raw_amount": float(obs.committed_amount_usd),
                "factor": float(obs.rsf_factor),
                "rsf_amount": float(obs_rsf_val),
                "rule_id": "RULE-RSF-09",
            })

        category_list = []
        for cat_name, val in categories.items():
            category_list.append({
                "category_name": cat_name,
                "raw_amount": float(val["raw_amount"]),
                "rsf_amount": float(val["rsf_amount"]),
                "factor": val["factor"],
                "positions_count": val["positions_count"],
                "percentage_of_total_rsf": float((val["rsf_amount"] / total_rsf * 100) if total_rsf > 0 else 0),
            })

        return {
            "snapshot_id": snapshot_id,
            "total_funded_assets": float(total_funded_assets),
            "total_off_balance_commitments": float(total_obs),
            "total_rsf": float(total_rsf),
            "effective_rsf_factor": float(total_rsf / (total_funded_assets + total_obs)) if (total_funded_assets + total_obs) > 0 else 0,
            "categories": category_list,
            "position_details": position_details,
        }
