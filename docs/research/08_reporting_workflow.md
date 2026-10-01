# 08 Reporting Workflow: Shadow Close Orchestration and Late Adjustments

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-08  
**Status**: Authoritative Reference Documentation  

---

## 1. The Month-End / Quarter-End Close Challenge

Regulatory reporting is not an ad-hoc batch calculation; it is a rigorous, controlled accounting cycle. If raw trade feeds or deposit books continue mutating while calculations are underway, the resulting numbers are unreconcilable.

The Liquidity Twin implements a deterministic **10-Stage Shadow Close Process** designed to model real-world institutional treasury and financial control workflows.

---

## 2. The 10 Sequential Close Stages

```
   [1. Freeze Source Data]
              │
              ▼
   [2. Validate Balances]
              │
              ▼
   [3. Reconcile Accounting Totals]
              │
              ▼
   [4. Apply Regulatory Classification]
              │
              ▼
   [5. Calculate Liquidity Metrics]
              │
              ▼
   [6. Run Controls]
              │
              ▼
   [7. Investigate Exceptions]
              │
              ▼
   [8. Prepare Management Information]
              │
              ▼
   [9. Generate Reporting Output]
              │
              ▼
   [10. Reviewer Sign-Off]
```

### Stage Details and Exit Criteria

| Stage # | Stage Name | Target Owner | Invariants and Exit Criteria | Status Lifecycle |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Freeze Source Data** | Data Operations | Ingestion window locked. Source snapshot hash computed and stored. No mutable source updates permitted. | NOT_STARTED → IN_PROGRESS → COMPLETED |
| **2** | **Validate Balances** | Subledger Team | Record-level schema validation: non-null balances, valid ISO currencies, positive asset/liability magnitudes. | COMPLETED / FAILED |
| **3** | **Reconcile Accounting Totals** | Financial Control | Assets = Liabilities + Equity verified. Opening + Movement = Closing for all accounts. Subledger to GL variance = $0.00. | COMPLETED / BLOCKED |
| **4** | **Apply Regulatory Classification** | Regulatory Policy | 100% of balance-sheet positions mapped to active regulatory rules. No unmapped fallback accounts. | COMPLETED / BLOCKED |
| **5** | **Calculate Liquidity Metrics** | Liquidity Engine | Deterministic computation of ASF, RSF, NSFR, HQLA, Net Cash Outflows, and LCR. Numerators/denominators persisted. | COMPLETED / FAILED |
| **6** | **Run Controls** | Quality Assurance | Execution of 100+ automated controls across all 10 families. Pass/fail scores computed. | COMPLETED / BLOCKED |
| **7** | **Investigate Exceptions** | Finance Analyst | All `FAIL` exceptions investigated and assigned remediation plans or approved risk waivers. Zero unresolved critical breaks. | COMPLETED / BLOCKED |
| **8** | **Prepare Management Information** | Treasury Analytics | Driver decomposition computed (Shapley attribution). Variance commentary generated. Executive deck prepared. | COMPLETED / IN_PROGRESS |
| **9** | **Generate Reporting Output** | Reporting Compiler | Production of formal PDF and XLSX reporting packs. Cell-level reconciliation verified against calculation tables. | COMPLETED / BLOCKED |
| **10** | **Reviewer Sign-Off** | Lead Controller / Reviewer | Formal four-eye sign-off. Cryptographic snapshot sealing. Close cycle locked against further modification. | COMPLETED |

---

## 3. Late Adjustment Protocol

In active banking operations, late balance-sheet events frequently arrive after initial data freeze (e.g., late-clearing treasury wire, discovered settlement error, post-cutoff loan draw).

### The $38M Demonstration Scenario
The Liquidity Twin embeds a deterministic late adjustment scenario:
1. Initial close advances through Stage 5 (NSFR baseline calculated at $117.6\%$).
2. A late corporate funding adjustment of $\approx \$38\text{M}$ is posted with post-cutoff timestamp.
3. The system immediately registers:
   - **Reconciliation Break**: GL total diverges from frozen snapshot balance.
   - **Stage Regression**: Stages 5 through 10 revert from `COMPLETED` to `BLOCKED`.
   - **Impact Propagation**: Downstream ASF shifts, moving NSFR by $\approx -0.5\text{ pp}$.
   - **Control Trigger**: `CTRL-REC-008` (*Post-Freeze Mutation Detected*) trips to `FAIL`.
   - **Audit Trail**: Generates `adjustment_event` with before/after delta and user rationale.

---

## 4. Metadata and Methodology Governance

```yaml
rule_name: Shadow Close Workflow and Sign-Off Governance
rule_version: 2.0.0
effective_date: 2026-01-01
source_name: Federal Reserve / EBA Internal Control & Governance Guidelines
source_url: https://www.bis.org/publ/bcbs239.htm
source_access_date: 2026-10-01
methodology_note: >
  Defines state machine for 10-stage sequential month-end close,
  four-eye sign-off gates, and late balance-sheet adjustment blast radius.
