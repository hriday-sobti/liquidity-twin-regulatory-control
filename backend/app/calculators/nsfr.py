from datetime import datetime
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Any

from sqlalchemy.orm import Session

from backend.app.calculators.asf import AsfCalculationEngine
from backend.app.calculators.rsf import RsfCalculationEngine
from backend.app.models.facts import FactLiquidityMetric, FactReportingSnapshot


class NsfrCalculationEngine:
    """
    Official Net Stable Funding Ratio (NSFR) engine under BCBS 295.
    Calculates NSFR = (ASF / RSF) * 100%, surplus/deficit, and buffer margins.
    """

    def __init__(self, db: Session):
        self.db = db
        self.asf_engine = AsfCalculationEngine(db)
        self.rsf_engine = RsfCalculationEngine(db)

    def calculate_nsfr(self, snapshot_id: str, persist: bool = False) -> dict[str, Any]:
        asf_res = self.asf_engine.calculate_asf(snapshot_id)
        rsf_res = self.rsf_engine.calculate_rsf(snapshot_id)

        asf_amt = Decimal(str(asf_res["total_asf"]))
        rsf_amt = Decimal(str(rsf_res["total_rsf"]))

        if rsf_amt == Decimal("0.0"):
            nsfr_ratio = Decimal("0.0000")
        else:
            nsfr_ratio = (asf_amt / rsf_amt) * Decimal("100.0")

        nsfr_ratio_quant = nsfr_ratio.quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        surplus_deficit = asf_amt - rsf_amt
        regulatory_buffer = nsfr_ratio_quant - Decimal("100.0000")
        is_compliant = (nsfr_ratio_quant >= Decimal("100.0000"))

        result = {
            "snapshot_id": snapshot_id,
            "metric_name": "NSFR",
            "asf_amount": float(asf_amt),
            "rsf_amount": float(rsf_amt),
            "nsfr_percentage": float(nsfr_ratio_quant),
            "regulatory_minimum_percentage": 100.0,
            "buffer_percentage": float(regulatory_buffer),
            "surplus_deficit_usd": float(surplus_deficit),
            "is_compliant": is_compliant,
            "rule_version": "3.2.0",
            "calculation_version": "3.2.0",
            "asf_breakdown": asf_res["categories"],
            "rsf_breakdown": rsf_res["categories"],
            "calculated_at": datetime.utcnow().isoformat(),
        }

        if persist:
            snap = self.db.query(FactReportingSnapshot).filter_by(snapshot_id=snapshot_id).first()
            if snap:
                snap.asf_amount = asf_amt
                snap.rsf_amount = rsf_amt
                snap.nsfr_value = nsfr_ratio_quant

                # Upsert FactLiquidityMetric
                metric_id = f"METRIC-{snapshot_id}-NSFR"
                existing_m = self.db.query(FactLiquidityMetric).filter_by(metric_id=metric_id).first()
                if not existing_m:
                    m = FactLiquidityMetric(
                        metric_id=metric_id,
                        snapshot_id=snapshot_id,
                        business_date=snap.business_date,
                        metric_name="NSFR",
                        numerator=asf_amt,
                        denominator=rsf_amt,
                        ratio_value=nsfr_ratio_quant,
                        target_value=Decimal("117.6000"),
                        regulatory_minimum=Decimal("100.0000"),
                        calculation_version="3.2.0",
                        calculated_at=datetime.utcnow(),
                    )
                    self.db.add(m)
                else:
                    existing_m.numerator = asf_amt
                    existing_m.denominator = rsf_amt
                    existing_m.ratio_value = nsfr_ratio_quant
                    existing_m.calculated_at = datetime.utcnow()

                self.db.commit()

        return result
