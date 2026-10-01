from backend.app.core.database import SessionLocal, Base, engine
from backend.app.services.generator import SyntheticBankGenerator
from backend.app.controls.engine import ControlEngine
from backend.app.services.query_workbench import StakeholderQueryWorkbench


def main():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Seeding synthetic bank positions and events...")
        gen = SyntheticBankGenerator(db, seed=42)
        snap = gen.seed_all()
        print("Executing 100 automated continuous controls...")
        ce = ControlEngine(db)
        ce.run_all_controls(snap.snapshot_id)
        print("Seeding stakeholder query Q-1048...")
        qw = StakeholderQueryWorkbench(db)
        qw.seed_demo_query()
        print("Seed and initial setup successfully completed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
