# 12 Technical Stack Architecture and Design Rationale

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-12  
**Status**: Authoritative Reference Documentation  

---

## 1. Architectural Philosophy and Technology Selection

The architecture is built on three core engineering tenets:
1. **Financial Precision and Determinism**: Zero unchecked floating-point math; fixed-point decimal arithmetic throughout; deterministic random seeds for reproducible data generation.
2. **Transparent Data Provenance**: Every calculation is persisted with rule versions, input hashes, and explicit graph lineage; zero unexplainable numbers.
3. **Turnkey Local Reproducibility**: Designed to operate with zero external infrastructure overhead using SQLite for instant local execution and automated testing, while remaining 100% production-compatible with PostgreSQL.

---

## 2. Technology Stack Breakdown

```
+------------------------------------------------------------------------------------+
|                                    FRONTEND                                        |
|  React 19 / 18  │  TypeScript 5  │  Vite  │  Tailwind CSS  │  ECharts  │ React Flow|
+------------------------------------------------------------------------------------+
                                        │  JSON / REST API
                                        ▼
+------------------------------------------------------------------------------------+
|                                BACKEND APPLICATION                                 |
|               FastAPI (REST Framework)  │  Pydantic v2 (Validation)                |
+------------------------------------------------------------------------------------+
|        ENGINES & COMPILERS               │          LIBRARIES                      |
|  - Synthetic Bank Event Generator        │  - SQLAlchemy 2.0 (Core & ORM)          |
|  - Accounting Rollup & GL Reconciler     │  - Alembic (Schema Migrations)          |
|  - Regulatory Classification Engine      │  - NetworkX 3.7 (Lineage & Blast Radius)|
|  - ASF / RSF / NSFR Engine               │  - Pandas 3.0 & NumPy 2.5 (Attribution) |
|  - LCR & Liquidity Buffer Engine         │  - ReportLab 5.0 (PDF Engine)           |
|  - 100+ Automated Control Engine         │  - openpyxl 3.1 (Excel Compiler)        |
|  - Counterfactual Scenario Lab           │  - Pytest 9.1 & Hypothesis 6.168        |
|  - Controlled Copilot & Numeric Verifier │  - Ruff (Linting & Formatting)          |
+------------------------------------------------------------------------------------+
                                        │  SQLAlchemy Unified Dialect
                                        ▼
+------------------------------------------------------------------------------------+
|                             RELATIONAL DATA STORE                                  |
|         PostgreSQL (Enterprise Production)  /  SQLite 3 (Local Portable)           |
+------------------------------------------------------------------------------------+
```

---

## 3. Storage Layer: Dual-Dialect Database Design

To ensure the project is immediately runnable on any local developer workstation or evaluation machine without requiring Docker or a running PostgreSQL daemon, the database architecture uses **SQLAlchemy 2.0 with Dual-Dialect Support**:
- **SQLite 3**: Default out-of-the-box local engine. Zero daemon, zero port conflicts, file-backed or in-memory, full support for foreign keys (`PRAGMA foreign_keys = ON`), complex CTEs, window functions, and JSON storage.
- **PostgreSQL**: Production engine. Configured via environment variable `DATABASE_URL=postgresql://user:pass@localhost:5432/liquidity_twin`.

### Decimal Arithmetic Standard
All monetary and balance fields are mapped to `Numeric(24, 4)` and handled in Python as `decimal.Decimal` with explicit rounding modes (`ROUND_HALF_EVEN`).

---

## 4. Graph & Lineage Engine: NetworkX

Data lineage is structured as a directed acyclic graph (DAG). The backend utilizes **NetworkX 3.7**:
- Nodes represent entities from source events to final report cells.
- Cycle detection guarantees topological order during calculation execution.
- Backward traversal reconstructs the **Metric Birth Certificate**.
- Forward BFS traversal calculates the **Blast Radius** of control failures.
- Serialized to lightweight JSON for visualization in the UI using **React Flow**.

---

## 5. Reporting Compiler: ReportLab and openpyxl

Reports are compiled deterministically from database snapshots:
- **PDF Compilation**: Powered by **ReportLab 5.0**. Generates professional, publication-quality regulatory reports with structured tables, executive callout boxes, watermark seals, and signatory blocks.
- **XLSX Compilation**: Powered by **openpyxl 3.1**. Generates auditable workbooks containing formulaic summaries, component tabs (ASF, RSF, LCR, Controls, Exceptions), and cell-level source references.

---

## 6. Testing Toolchain: Pytest and Hypothesis

Testing follows a three-tier pyramid:
1. **Unit Tests**: Pure functional tests of factors, bucketing rules, and regex verifiers.
2. **Property-Based Tests (Hypothesis)**: Generative testing verifying mathematical invariants (e.g., $Assets = Liabilities + Equity$ regardless of event ordering; driver waterfall sums exactly equal total delta; ASF/RSF are monotonically non-negative).
3. **Integration & Golden Tests**: Static golden balance-sheet dataset with known, pre-calculated expected results to verify calculation accuracy down to four decimal places.

---

## 7. Metadata and Methodology Governance

```yaml
rule_name: Production Technology Stack and Design Standard
rule_version: 1.0.0
effective_date: 2026-01-01
source_name: Liquidity Twin Engineering Architecture Specification
source_url: local://docs/research/12_technical_stack.md
source_access_date: 2026-10-01
methodology_note: >
  Defines framework selections, dual-dialect persistence strategy,
  precision decimal standards, and testing architecture.
