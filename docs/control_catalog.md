# Automated Continuous Control Catalog

**Governance Reference**: BCBS 239 Risk Data Aggregation Standards  
**Scope**: 100 Automated Checks across 10 Operational Families  

---

## 1. Catalog Summary

| Family | Total Checks | Primary Invariant | Baseline Score |
| :--- | :---: | :--- | :---: |
| **ACCOUNTING** | 10 | Double-entry balance sheet identity ($Assets == Liabilities + Equity$) and roll-forward | **10 / 10 PASS** |
| **DATA QUALITY** | 10 | Null checks, ISO currencies, deduplication, referential integrity | **10 / 10 PASS** |
| **CLASSIFICATION** | 10 | 100% regulatory mapping, LTV thresholds, rating floors | **9 / 10 PASS (1 WARN)** |
| **MATURITY** | 10 | Residual tenor non-negativity, bucketing rules, NPL aging | **10 / 10 PASS** |
| **CALCULATION** | 10 | Non-zero denominators, factor bounds, 75% inflow ceiling | **10 / 10 PASS** |
| **RECONCILIATION** | 10 | Subledger to GL summary, post-freeze mutation lock, trade matching | **9 / 10 PASS (1 FAIL)** |
| **REPORTING** | 10 | Cell-level reconciliation, sign-off freeze, schedule summation | **10 / 10 PASS** |
| **LINEAGE** | 10 | Strict graph acyclicity (DAG), complete backward traversal paths | **10 / 10 PASS** |
| **SCENARIO** | 10 | Baseline immutability, cash drain conservation, double-entry in stress | **10 / 10 PASS** |
| **AI OUTPUT** | 10 | Grounding verification, directional claim consistency, SQL rejection | **10 / 10 PASS** |
| **TOTAL** | **100** | **Comprehensive Financial Control Verification** | **98.0% PASSED** |

---

## 2. Sample Control Definitions

### `CTRL-ACC-001`: Balance Sheet Double-Entry Identity
- **Family**: Accounting
- **Severity**: Critical
- **Frequency**: Per Close Cycle
- **Rule**: $\sum Assets - \sum (Liabilities + Equity) = 0.00$
- **Expected**: Variance == $0.00
- **Action on Breach**: Blocks close cycle stage 3 and halts all downstream metric calculations.

### `CTRL-REC-008`: Post-Freeze Data Mutation Guard
- **Family**: Reconciliation
- **Severity**: Critical
- **Frequency**: Continuous
- **Rule**: Once snapshot status is set to `FROZEN`, zero insert/update/delete operations are permitted on source tables.
- **Action on Breach**: Instantly regresses Close Stages 5 through 10 to `BLOCKED` and opens an emergency reconciliation exception.

### `CTRL-AI-001`: AI NSFR Numeric Grounding Check
- **Family**: AI Output
- **Severity**: Critical
- **Frequency**: Per Query
- **Rule**: $|Claimed NSFR - Validated NSFR| \le 0.05\text{ pp}$
- **Action on Breach**: Quarantines generated narrative with red `OUTPUT QUARANTINED` alert and displays underlying database value.
