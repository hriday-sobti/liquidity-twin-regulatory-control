from backend.app.core.database import SessionLocal
from backend.app.reporting.compiler import ReportingCompiler


def main():
    db = SessionLocal()
    try:
        snap_id = "SNAP-2026-Q3-BASE"
        print(f"Compiling regulatory reporting packs for {snap_id}...")
        rc = ReportingCompiler(db)
        res = rc.compile_reporting_pack(snap_id)
        print(f"  -> Generated PDF:  {res['pdf_path']}")
        print(f"  -> Generated XLSX: {res['xlsx_path']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
