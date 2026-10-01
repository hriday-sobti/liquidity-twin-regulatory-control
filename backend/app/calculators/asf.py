from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from backend.app.models.dimensions import DimAccount
from backend.app.models.facts import FactBalanceSheet


class AsfCalculationEngine:
    """
    Deterministic Available Stable Funding (ASF) calculation engine conforming to BCBS 295.
    Calculates weighted stable funding contributions across liabilities and equity.
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_asf(self, snapshot_id: str) -> dict[str, Any]:
        balances = self.db.query(FactBalanceSheet).filter_by(snapshot_id=snapshot_id).all()
        
        # Aggregate by high-level Basel category
        categories: dict[str, dict[str, Any]] = {
            "Capital & Qualifying Liabilities >= 1Y": {"raw_amount": Decimal("0.0"), "asf_amount": Decimal("0.0"), "factor": 1.00, "positions_count": 0},
            "Stable Retail Deposits": {"raw_amount": Decimal("0.0"), "asf_amount": Decimal("0.0"), "factor": 0.95, "positions_count": 0},
            "Less Stable Retail Deposits": {"raw_amount": Decimal("0.0"), "asf_amount": Decimal("0.0"), "factor": 0.90, "positions_count": 0},
            "Operational Wholesale Deposits": {"raw_amount": Decimal("0.0"), "asf_amount": Decimal("0.0"), "factor": 0.50, "positions_count": 0},
            "Non-Operational Corporate Funding < 1Y": {"raw_amount": Decimal("0.0"), "asf_amount": Decimal("0.0"), "factor": 0.50, "positions_count": 0},
            "Other Liabilities & Funding 6M to < 1Y": {"raw_amount": Decimal("0.0"), "asf_amount": Decimal("0.0"), "factor": 0.50, "positions_count": 0},
            "Short-Term Financial Counterparty Funding < 6M": {"raw_amount": Decimal("0.0"), "asf_amount": Decimal("0.0"), "factor": 0.00, "positions_count": 0},
        }

        total_asf = Decimal("0.0000")
        total_raw_liabilities = Decimal("0.0000")
        position_details = []

        for b in balances:
            if b.asf_factor is not None and b.closing_balance_usd > 0:
                acc = self.db.query(DimAccount).filter_by(account_id=b.account_id).first()
                pcode = acc.product.product_code if acc and acc.product else "UNKNOWN"
                side = acc.product.balance_sheet_side if acc and acc.product else "UNKNOWN"
                
                if side not in ("LIABILITY", "EQUITY"):
                    continue

                total_raw_liabilities += b.closing_balance_usd
                asf_val = b.asf_amount
                total_asf += asf_val

                # Assign to display bucket
                cat_key = "Short-Term Financial Counterparty Funding < 6M"
                if b.rule_id == "RULE-ASF-01":
                    cat_key = "Capital & Qualifying Liabilities >= 1Y"
                elif b.rule_id == "RULE-ASF-02":
                    cat_key = "Stable Retail Deposits"
                elif b.rule_id == "RULE-ASF-03":
                    cat_key = "Less Stable Retail Deposits"
                elif b.rule_id == "RULE-ASF-05":
                    cat_key = "Operational Wholesale Deposits"
                elif b.rule_id == "RULE-ASF-04":
                    cat_key = "Non-Operational Corporate Funding < 1Y"
                elif b.rule_id == "RULE-ASF-06":
                    cat_key = "Other Liabilities & Funding 6M to < 1Y"

                categories[cat_key]["raw_amount"] += b.closing_balance_usd
                categories[cat_key]["asf_amount"] += asf_val
                categories[cat_key]["positions_count"] += 1

                position_details.append({
                    "account_id": b.account_id,
                    "product_code": pcode,
                    "raw_amount": float(b.closing_balance_usd),
                    "factor": float(b.asf_factor),
                    "asf_amount": float(asf_val),
                    "rule_id": b.rule_id,
                })

        category_list = []
        for cat_name, val in categories.items():
            category_list.append({
                "category_name": cat_name,
                "raw_amount": float(val["raw_amount"]),
                "asf_amount": float(val["asf_amount"]),
                "factor": val["factor"],
                "positions_count": val["positions_count"],
                "percentage_of_total_asf": float((val["asf_amount"] / total_asf * 100) if total_asf > 0 else 0),
            })

        return {
            "snapshot_id": snapshot_id,
            "total_raw_liabilities": float(total_raw_liabilities),
            "total_asf": float(total_asf),
            "effective_asf_factor": float(total_asf / total_raw_liabilities) if total_raw_liabilities > 0 else 0,
            "categories": category_list,
            "position_details": position_details,
        }
