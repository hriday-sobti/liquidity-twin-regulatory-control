# LIQUIDITY TWIN
## Regulatory Liquidity Digital Twin, Control Graph and Reporting Compiler

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)](pyproject.toml)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-teal.svg)](https://fastapi.tiangolo.com)
[![React: 18/19](https://img.shields.io/badge/Frontend-React%20%7C%20Vite%20%7C%20Tailwind-blue.svg)](frontend/)
[![BCBS 295 / 238](https://img.shields.io/badge/Regulatory%20Standard-BCBS%20295%20%7C%20238-darkblue.svg)](docs/research/)

> A synthetic bank whose balance-sheet events continuously flow through accounting positions, regulatory classification, liquidity calculations, controls, investigation, reporting, and audit-ready lineage.

---

## 1. Executive Overview: Why the System Exists

When a regulatory liquidity number changes on a bank's executive dashboard or supervisory return, financial analysts and treasury controllers face fundamental operational questions:
- **Why did the metric move?** Which balance-sheet driver or transactional account caused the shift?
- **Can we trust it?** What automated controls validated the data, and are there open reconciliation breaks?
- **Where did it come from?** Can we trace every dollar backward to source ledger records and specific Basel regulatory rules?
- **What happens under stress?** How will ratios behave if wholesale corporate depositors withdraw 8% of balances?
- **Can we reproduce the reporting output?** Does the published PDF and XLSX reporting pack reconcile cell-by-cell to the underlying database?

**Liquidity Twin** provides a bidirectional financial information system that replaces manual spreadsheets and opaque batch processes with deterministic accounting projection, rule-driven regulatory classification, a continuous 100-control validation engine, a directed acyclic lineage graph, a counterfactual scenario lab, an automated reporting compiler, and a controlled natural-language copilot with strict numeric verification.

---

## 2. Core Workflow: Forward & Backward Architecture

```
FORWARD PROVENANCE:
Balance-Sheet / Financial Event
        ↓
Accounting Position (Double-Entry Roll-Forward)
        ↓
Regulatory Classification (Rule-Driven BCBS Engine)
        ↓
Available Stable Funding (ASF) / Required Stable Funding (RSF)
        ↓
NSFR / LCR / Liquidity Buffer Metrics
        ↓
Continuous Control Engine (100 Automated Checks)
        ↓
Regulatory Reporting Compiler (PDF & XLSX)
```

```
BACKWARD AUDITABILITY ("Metric Birth Certificate"):
Reported NSFR Movement (-4.7 pp)
        ↓
Why did it move? (Shapley Driver Attribution)
        ↓
Which balance-sheet bucket changed? (Corporate Non-Operational Deposits -$10M)
        ↓
Which accounts caused it? (ACC-CORP_NON_OPERATIONAL)
        ↓
Which source records support it? (EVT-SNAP-2026-Q3-BASE-CORP_NON_OPERATIONAL-01)
        ↓
Which regulatory rule classified it? (RULE-ASF-04, Factor 50%, BCBS 295 §26)
        ↓
Which controls validated it? (CTRL-ACC-001, CTRL-CAL-003, CTRL-REC-001)
        ↓
Which reports are affected? (Executive Liquidity Summary Schedule 1.1)
```

---

## 3. Financial Methodology & Regulatory Standards

All regulatory calculations are versioned, documented, and conform strictly to official primary standards published by the Basel Committee on Banking Supervision (BCBS):

| Metric | Primary Standard | Supervisory Minimum | Target Demonstration Baseline | Description |
| :--- | :--- | :---: | :---: | :--- |
| **NSFR** | BCBS 295 (Oct 2014) | $\ge 100.00\%$ | **117.64%** ($\pm 0.2\text{ pp}$) | $\frac{\text{Available Stable Funding (ASF)}}{\text{Required Stable Funding (RSF)}} \times 100\%$ |
| **LCR** | BCBS 238 (Jan 2013) | $\ge 100.00\%$ | **132.49%** ($\pm 0.5\text{ pp}$) | $\frac{\text{Stock of HQLA}}{\text{Total Net Cash Outflows over 30 Days}} \times 100\%$ |
| **ASF** | BCBS 295 §§17–31 | N/A | **$842.30M** | Weighted stable capital and customer liabilities |
| **RSF** | BCBS 295 §§32–45 | N/A | **$716.00M** | Weighted asset and off-balance sheet illiquidity |
| **HQLA** | BCBS 238 §§49–64 | N/A | **$219.00M** | Level 1 (0% haircut) and Level 2A (15% haircut) unencumbered buffer |
| **Net Outflows** | BCBS 238 §§67–153 | N/A | **$165.30M** | Gross 30D cash outflows minus eligible inflows (capped at 75%) |

---

## 4. Key Subsystems

### 1. Synthetic Bank Event Generator & Accounting Model
- Commercial bank portfolio calibrated to **$1,050.00M** in assets, matched by liabilities and equity ($Assets = Liabilities + Equity$ with **$0.00 variance**).
- Append-only transactional event log supporting double-entry balance roll-forward ($Closing = Opening + Movement$).
- Multi-currency support (USD, EUR, GBP, SGD, INR) with deterministic foreign exchange rates.

### 2. Continuous Control Engine (100 Automated Checks)
- 10 structured operational families: Accounting, Data Quality, Classification, Maturity, Calculation, Reconciliation, Reporting, Lineage, Scenario, and AI Output.
- Executed results yield an operational score of **98.0% Passed** (98 Pass, 1 Warning, 1 Investigating Break), matching real-world institutional close operations.

### 3. Metric Birth Certificate & Lineage Graph
- Graph-theoretic Directed Acyclic Graph (DAG) built with **NetworkX** and rendered in the workstation UI with **React Flow**.
- Backward traversal from any metric cell down to supporting subledger positions and transaction slips.
- Automated forward **Blast-Radius Analysis** quantifying downstream monetary exposure for control failures.

### 4. "Why Did NSFR Move?" Driver Decomposition
- Mathematically consistent **Shapley attribution** allocating ratio deltas across corporate deposits, retail funding, wholesale debt, and loan growth.
- Guaranteed property: $\sum \text{Driver Contributions} = \Delta \text{NSFR}$ within 0.0001 pp.

### 5. Counterfactual Scenario Lab
- In-memory temporary balance-sheet projections without mutating the frozen baseline snapshot.
- Acceptance Test 3 Target: Shocks corporate deposits by **-8.0%**, yielding a stressed NSFR of **113.10%** and identifying cash buffer depletion.

### 6. Shadow Close Orchestration & Late Adjustment
- 10-stage sequential close workflow (Freeze -> Validate -> Reconcile -> Classify -> Calculate -> Control -> Exceptions -> MI -> Report -> Sign-off).
- Injects a **$38M Late Adjustment** post-freeze, detects the break, halts stages 5–10, and demands authorized re-execution.

### 7. Controlled Analyst Copilot & Numeric Verifier
- Natural-language assistant constrained to an allowlist of 10 analytical intents (zero arbitrary SQL execution).
- **Mandatory Regex & Semantic Numeric Claim Verifier**: Blocked output if any cited percentage, currency value, direction, or driver fails to match database grounding within tolerance.
- Automated AI Red-Teaming Suite achieving **100.0% Reliability Score** across 8 adversarial test patterns.

### 8. Publication-Grade Reporting Compiler
- Generates official regulatory PDF packs (ReportLab) and multi-tab Excel workbooks (openpyxl) complete with executive summaries, reconciliation schedules, and reviewer sign-off blocks.

---

## 5. Quickstart & How to Run

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Installation & Environment Setup
```bash
# Clone the repository
git clone https://github.com/synthetic-bank-lab/liquidity-twin-regulatory-control.git
cd liquidity-twin-regulatory-control

# Install backend dependencies
python -m pip install -e ".[dev]"

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Single-Command Turnkey Demo
```bash
# Windows / POSIX
python -m scripts.run_smoke_tests
```
This single command:
1. Initializes database tables (SQLite out-of-the-box; PostgreSQL compatible).
2. Seeds calibrated balance-sheet entities, accounts, and 1,000+ transaction events.
3. Computes baseline NSFR (117.6%) and LCR (132.4%).
4. Executes the 100 automated continuous controls.
5. Verifies the -8% corporate deposit stress test.
6. Runs the AI Red-Team safety suite.
7. Compiles the PDF and XLSX regulatory reporting packs.
8. Runs all unit, property-based, and integration tests.

### 3. Launching Development Servers
```bash
# Terminal 1: Backend API (FastAPI)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend Analyst Workstation (Vite + React)
cd frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 6. Project Architecture & Directory Structure

```text
liquidity-twin-regulatory-control/
├── backend/
│   ├── app/
│   │   ├── api/v1/router.py          # Unified REST endpoints
│   │   ├── core/                     # Configuration & SQLAlchemy database sessions
│   │   ├── models/                   # Dimensions, regulatory rules, facts, lineage, workflow
│   │   ├── calculators/              # Rule classifier, ASF, RSF, NSFR, and LCR engines
│   │   ├── controls/                 # 100 automated controls catalog, execution engine, exceptions
│   │   ├── lineage/                  # NetworkX DAG lineage builder and blast-radius analyzer
│   │   ├── scenarios/                # Shapley movement attribution and counterfactual scenario lab
│   │   ├── reporting/                # ReportLab PDF & openpyxl XLSX reporting compiler
│   │   ├── copilot/                  # Intent parser, numeric verifier, AI red-team suite
│   │   └── main.py                   # FastAPI application factory
│   └── tests/
│       ├── unit/                     # Calculation engine & golden dataset tests
│       ├── property/                 # Hypothesis generative invariant tests
│       └── integration/              # FastAPI endpoint tests
│
├── frontend/
│   ├── src/
│   │   ├── components/               # Sidebar, KpiRow, Waterfall, LineageGraph, ScenarioLab, Close, Controls, Copilot
│   │   ├── services/api.ts           # Typed API client
│   │   ├── types/index.ts            # Domain TypeScript interfaces
│   │   └── App.tsx                   # Main analyst command center
│   └── package.json                  # React 18, Vite, Tailwind CSS, ECharts, React Flow
│
├── data/
│   ├── config/regulatory_rules.json  # Complete Basel III rule catalog with BCBS source references
│   └── golden/golden_dataset.json    # Hand-verified golden dataset for calculation regression
├── docs/research/                    # 12 authoritative research methodology documents
├── reports/generated/                # Output PDF and XLSX reporting packs
├── scripts/                          # Turnkey automation scripts (seed, calculate, controls, verify)
├── Makefile                          # Standard engineering operations targets
├── pyproject.toml                    # Python project configuration and pinned dependencies
└── README.md
```

---

## 7. Testing Strategy & Verification Gates

The test pyramid contains unit, generative property-based, and end-to-end integration tests:

```bash
# Execute full pytest suite
python -m pytest backend/tests -v
```

- **Golden Calculation Tests (`test_calculators.py`)**: Tests calculation precision down to the penny against a hand-verified 10-customer, 15-account dataset.
- **Property-Based Invariant Tests (`test_properties.py`)**: Uses **Hypothesis** to test balance roll-forwards, non-negativity of weighted factors, and conservation laws across arbitrary inputs.
- **API Integration Tests (`test_api.py`)**: Tests live HTTP responses, header statuses, scenario simulations, and AI quarantine behavior.

---

## 8. Authoritative References & Governance

All regulatory logic is directly grounded in primary supervisory documentation:
- **BCBS 295**: *Basel III: The Net Stable Funding Ratio* (Bank for International Settlements, October 2014) — [https://www.bis.org/bcbs/publ/d295.htm](https://www.bis.org/bcbs/publ/d295.htm)
- **BCBS 238**: *Basel III: The Liquidity Coverage Ratio and liquidity risk monitoring tools* (January 2013) — [https://www.bis.org/bcbs/publ/d238.htm](https://www.bis.org/bcbs/publ/d238.htm)
- **BCBS 239**: *Principles for effective risk data aggregation and risk reporting* (January 2013) — [https://www.bis.org/publ/bcbs239.htm](https://www.bis.org/publ/bcbs239.htm)
- **BCBS DIS30 / DIS40**: *Pillar 3 Disclosure Requirements - Consolidated and Enhanced Framework* (March 2017) — [https://www.bis.org/basel_framework/chapter/DIS/40.htm](https://www.bis.org/basel_framework/chapter/DIS/40.htm)

*Disclaimer: This system is a controlled synthetic regulatory liquidity simulation and reporting environment developed for institutional data modeling and risk governance demonstration.*
