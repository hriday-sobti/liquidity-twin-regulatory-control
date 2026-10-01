# 07 Financial Reconciliation and Automated Control Framework

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-07  
**Status**: Authoritative Reference Documentation  

---

## 1. The Institutional Role of Controls

In financial institutions, regulatory reporting errors rarely originate in the final ratio formula ($ASF / RSF$). They originate upstream: in missing transactions, unreconciled ledger feeds, duplicate entries, misclassified customer types, stale fx rates, or unapproved manual adjustments.

A reporting system without embedded automated controls is merely a calculator. The Liquidity Twin embeds a **Continuous Control Engine** that executes over 100 automated checks across every stage of data ingestion, accounting rollup, regulatory classification, metric calculation, and reporting pack generation.

---

## 2. The 10 Control Families

The system organizes its 100+ controls into 10 structured operational families:

```
+------------------------------------------------------------------------------------+
|                         CONTINUOUS CONTROL ENGINE FAMILIES                         |
+---------------------+---------------------+--------------------+-------------------+
| 1. ACCOUNTING       | 2. DATA QUALITY     | 3. CLASSIFICATION  | 4. MATURITY       |
| Balance identities, | Nulls, duplicates,  | Factor boundaries, | Dates, tenors,    |
| roll-forwards, GL   | currencies, signs,  | rule coverage,     | past-due states,  |
| vs Subledger        | schema constraints  | counterparty types | backward tenors   |
+---------------------+---------------------+--------------------+-------------------+
| 5. CALCULATION      | 6. RECONCILIATION   | 7. REPORTING       | 8. LINEAGE        |
| Division by zero,   | Source-to-metric,   | Report cells vs    | Node graph        |
| formula invariance, | subledger-to-GL,    | facts, completeness| integrity, broken |
| decimal precision   | cash vs settlements | sign-off freeze    | dependency links  |
+---------------------+---------------------+--------------------+-------------------+
| 9. SCENARIO         | 10. AI OUTPUT       |                                        |
| Baseline immutabil- | Numeric accuracy,   |                                        |
| ity, stress bounds, | hallucination block,|                                        |
| isolation check     | claim verification  |                                        |
+---------------------+---------------------+--------------------+-------------------+
```

---

## 3. Four-State Control Status Model

Controls return one of four deterministic states:

1. **`PASS`**: Condition strictly satisfied within defined regulatory tolerance.
2. **`FAIL`**: Critical breach. Violates financial identity, missing required classification, or unreconciled balance break. **Blocks close sign-off and report generation**.
3. **`WARNING`**: Non-critical anomaly. Trend deviation, approaching regulatory buffer threshold, or non-material timing mismatch. Requires documented acknowledgment.
4. **`NOT_APPLICABLE`**: Control condition not triggered for the given entity or portfolio scope in the evaluated period.

---

## 4. Exception Management Lifecycle

Every control failure or warning generates a discrete, tracked exception record in `fact_exception`:

```
   [OPEN] ───────────────► [INVESTIGATING] ───────────────► [REMEDIATED]
     │                             │                              │
     │ (Rejected)                  │ (Unsuccessful)               ▼
     └─────────────────────────────┴─────────────────────► [AWAITING_REVIEW]
                                                                  │
                                   [CLOSED] ◄──────────────── [RESOLVED]
```

### Exception Record Attributes
- `exception_id`: Unique tracking UUID (e.g., `EXC-2026-09-0042`)
- `control_id`: Foreign key to `control_catalog`
- `severity`: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- `affected_metric`: `NSFR`, `LCR`, `ASF`, `RSF`, `GL_BALANCE`
- `affected_report`: Specific reporting line or schedule
- `root_cause`: Detailed diagnosis of underlying ledger or classification fault
- `owner`: Role responsible for investigation (`Analyst`, `Controller`, `Data Steward`)
- `reviewer`: Four-eye sign-off role (`Liquidity Reporting Lead`, `Reviewer`)

---

## 5. Control Blast Radius Analysis

When a control fails, the system must not merely log an error message. It computes the **downstream blast radius** via the data lineage graph:

$$\text{Direct Impact} \longrightarrow \text{Indirect Impact} \longrightarrow \text{Potential Impact}$$

For example, if control `CTRL-CLS-014` (*Wholesale Deposit Classification Valid*) fails on account `ACC-8821`:
- **Direct Impact**: Regulatory category assignment on Account `ACC-8821` ($15.0M).
- **Indirect Impact**: Available Stable Funding (ASF) calculation node; NSFR aggregate ratio.
- **Reporting Impact**: Executive Liquidity Summary (Line 1.1) and NSFR Reporting Table (Row 2.4).
- **Close Impact**: Shadow Close Stage 6 marked `BLOCKED`.

---

## 6. Metadata and Methodology Governance

```yaml
rule_name: Automated Regulatory Control and Reconciliation Architecture
rule_version: 2.1.0
effective_date: 2026-01-01
source_name: Basel Committee on Banking Supervision (BCBS 239 - Risk Data Aggregation & Reporting)
source_url: https://www.bis.org/publ/bcbs239.htm
source_access_date: 2026-10-01
methodology_note: >
  Implements BCBS 239 risk data governance, automated four-state control catalog,
  closed-loop exception tracking, and lineage-backed blast-radius propagation.
