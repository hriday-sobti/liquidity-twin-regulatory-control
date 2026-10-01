from backend.app.core.database import SessionLocal
from backend.app.controls.engine import ControlEngine


def main():
    db = SessionLocal()
    try:
        snap_id = "SNAP-2026-Q3-BASE"
        print(f"Executing 100 continuous controls on {snap_id}...")
        ce = ControlEngine(db)
        res = ce.run_all_controls(snap_id)
        print(f"  -> Total Controls: {res['total_controls']}")
        print(f"  -> Passed: {res['passed_count']} | Failed: {res['failed_count']} | Warning: {res['warning_count']}")
        print(f"  -> Control Score: {res['control_score']}%")
    finally:
        db.close()


if __name__ == "__main__":
    main()
