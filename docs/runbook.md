# LIQUIDITY TWIN: OPERATIONAL RUNBOOK & DEMONSTRATION SCRIPT

**System Context**: Regulatory Liquidity Digital Twin, Control Graph and Reporting Compiler  
**Audience**: Risk Controllers, Treasury Analysts, Software Engineers, Internal & External Auditors  

---

## 1. Quick Verification & Execution

### System Health & Status
```bash
# Verify database seeding, calculations, controls, scenarios, and tests
python -m scripts.run_smoke_tests
```

### Launching the Analyst Workstation
1. Start the FastAPI backend:
   ```bash
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. In a second terminal, start the Vite frontend:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.

---

## 2. Five-Minute End-to-End Walkthrough Script

| Step | Workstation Screen | Action to Perform | Observable Result & Audit Confirmation |
| :---: | :--- | :--- | :--- |
| **1** | **Overview** | Observe top KPI row | Verified metrics: **NSFR = 117.64%**, **LCR = 132.49%**, **ASF = $842.3M**, **RSF = $716.0M**, **Controls = 98.0% Passed**, **2 Tracked Exceptions**. |
| **2** | **Overview** | Inspect **What Changed?** Waterfall | Waterfall clearly visualizes prior NSFR, accretive vs dilutive balance-sheet movements, and final ratio. |
| **3** | **Movement Explorer** | Click **Corporate Deposits** driver | Decomposes exact driver contribution (-1.12 pp), displays supporting subledger movement (-$10.0M), and proves exact Shapley mathematical reconciliation. |
| **4** | **Lineage & Audit** | Click **View Metric Birth Certificate** | Interactive React Flow DAG renders 86 nodes and 88 edges. Click **NSFR** to see incoming edges from ASF and RSF contributions down to source events and Rule **RULE-ASF-04** (BCBS 295 §26). |
| **5** | **Scenario Lab** | Select preset **-8% Corporate Outflow** | Sliders adjust to -8.0%. Click **Run Scenario**. Stressed NSFR lands at **113.10%** (-4.54 pp delta) and highlights cash buffer depletion. Base snapshot remains strictly sealed. |
| **6** | **Close Workspace** | View 10-stage sequential close stepper | Displays stages 1 through 6 COMPLETED, stage 7 IN_PROGRESS. Click **Inject $38M Late Adjustment**. |
| **7** | **Close Workspace** | Observe late adjustment blast radius | Stages 5–10 instantly regress to **BLOCKED**. Control **CTRL-REC-008** trips to FAIL. Exception **EXC-CTRL-REC-008** opens with $38M exposure. |
| **8** | **Controls Catalog** | Filter status by **FAIL** | Inspect **CTRL-REC-007** (Interbank confirmation matching pending). Shows expected vs actual results, evidence reference, and downstream blast radius. |
| **9** | **Query Workbench** | Open Query **Q-1048** | Inspect Chief Risk Officer inquiry regarding 118.4% vs 117.9% variance. Displays root cause (preliminary classification mismatch), resolution evidence, and reviewer sign-off. |
| **10** | **Reporting Packs** | Click **Compile Latest Pack** | Automatically generates official regulatory **PDF** (ReportLab) and multi-tab **XLSX** (openpyxl) complete with executive summaries, reconciliation tables, and reviewer signature blocks. |
| **11** | **Analyst Copilot** | Ask *"What drove the NSFR movement?"* | Copilot retrieves grounded data, explains drivers, and displays green **NUMERICALLY VERIFIED** badge. |
| **12** | **Analyst Copilot** | Click **Test Adversarial Attack** | Injects an intentional hallucinated number (claims NSFR is 119.6%). NumericVerifier intercepts it and triggers red **OUTPUT QUARANTINED** banner. Displays **100% Safety Reliability Score**. |
| **13** | **Event Replay** | Step through timeline slider | Replays historical transaction events (deposit inflows, loan originations, bond purchases) with running NSFR impact. |
| **14** | **Public Benchmark** | Review BCBS Pillar 3 mapping | Verifies strict mapping to Basel DIS30 (LCR) and DIS40 (NSFR) templates with 100% synthetic institutional boundary. |

---

## 3. Operational Troubleshooting & Error Recovery

### Database Reset & Re-Seed
If test state or manual adjustments need to be purged:
```bash
python -c "import os; os.remove('liquidity_twin.db') if os.path.exists('liquidity_twin.db') else None"
python -m scripts.run_seed
python -m scripts.run_controls
```

### Static Analysis & Type Checking
```bash
ruff check backend
python -m pytest backend/tests -v
```
