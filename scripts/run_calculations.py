from backend.app.core.database import SessionLocal
from backend.app.calculators.nsfr import NsfrCalculationEngine
from backend.app.calculators.lcr import LcrCalculationEngine


def main():
    db = SessionLocal()
    try:
        snap_id = "SNAP-2026-Q3-BASE"
        print(f"Executing official liquidity calculations on {snap_id}...")
        nsfr_eng = NsfrCalculationEngine(db)
        nsfr_res = nsfr_eng.calculate_nsfr(snap_id, persist=True)
        print(f"  -> NSFR: {nsfr_res['nsfr_percentage']:.2f}% (ASF: ${nsfr_res['asf_amount']:,.2f}, RSF: ${nsfr_res['rsf_amount']:,.2f})")

        lcr_eng = LcrCalculationEngine(db)
        lcr_res = lcr_eng.calculate_lcr(snap_id, persist=True)
        print(f"  -> LCR:  {lcr_res['lcr_percentage']:.2f}% (HQLA: ${lcr_res['total_hqla']:,.2f}, Net Outflows: ${lcr_res['net_cash_outflows']:,.2f})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
