from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from backend.app.core.config import get_settings
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.api.v1.router import router as api_v1_router
from backend.app.services.generator import SyntheticBankGenerator

settings = get_settings()

app = FastAPI(
    title="LIQUIDITY TWIN API",
    description="Regulatory Liquidity Digital Twin, Control Graph and Reporting Compiler",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_v1_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def startup_event():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed if database is empty
    db = SessionLocal()
    try:
        from backend.app.models.facts import FactReportingSnapshot
        existing = db.query(FactReportingSnapshot).first()
        if not existing:
            gen = SyntheticBankGenerator(db, seed=settings.RANDOM_SEED)
            gen.seed_all()
            from backend.app.controls.engine import ControlEngine
            ce = ControlEngine(db)
            ce.run_all_controls("SNAP-2026-Q3-BASE")
            from backend.app.services.query_workbench import StakeholderQueryWorkbench
            qw = StakeholderQueryWorkbench(db)
            qw.seed_demo_query()
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Liquidity Twin Backend",
        "calculation_version": settings.CALCULATION_VERSION,
        "rule_version": settings.RULE_VERSION,
    }


# Serve generated report artifacts if directory exists
os.makedirs("reports/generated", exist_ok=True)
app.mount("/static/reports", StaticFiles(directory="reports/generated"), name="reports")
