# End-to-End Demonstration Script

**System**: Liquidity Twin Workstation  
**Total Demonstration Time**: Approximately 5 Minutes  

---

## Demonstration Sequence

### 1. Command Center Overview
- Open `http://localhost:5173`.
- Point out top KPI indicators:
  - NSFR: **117.64%** ($\ge 100\%$ regulatory minimum)
  - LCR: **132.49%** ($\ge 100\%$ regulatory minimum)
  - ASF: **$842.3M**, RSF: **$716.0M**
  - Continuous Controls: **98.0% Passed** (98 Pass, 1 Warning, 1 Failed)
- Highlight the **"What Changed?"** waterfall chart showing prior vs current ratio movements.

### 2. "Why Did NSFR Move?" Decomposition
- Navigate to **Movement Explorer** tab.
- Click **Corporate Deposits** driver.
- Note the -$1.12 pp dilution, supporting -$10.0M deposit outflow, and exact Shapley additive reconciliation.

### 3. Metric Birth Certificate (Lineage & Audit)
- Navigate to **Lineage & Audit** tab.
- Inspect the interactive DAG (86 nodes, 88 edges).
- Click the **NSFR** metric node. Observe backward provenance tracing through ASF/RSF contributions down to specific subledger positions and Basel rules (`RULE-ASF-04`).

### 4. Counterfactual Scenario Lab
- Navigate to **Scenario Lab** tab.
- Click **Load Target: -8% Corp Outflow** preset.
- Click **Run Scenario**.
- Observe stressed NSFR landing at **113.10%** (-4.54 pp delta) and cash buffer reduction.
- Confirm base snapshot remains locked and unmutated.

### 5. Shadow Close & Late Adjustment Injection
- Navigate to **Close Workspace** tab.
- Show stages 1 through 6 COMPLETED.
- Click **Inject $38M Late Adjustment**.
- Observe stages 5–10 instantly regress to **BLOCKED**, control `CTRL-REC-008` trip to FAIL, and exception `EXC-CTRL-REC-008` open.

### 6. Continuous Control Catalog & Exceptions
- Navigate to **Controls Catalog** tab.
- Filter by status `FAIL`.
- Inspect control `CTRL-REC-007` (Broker notice matching pending).
- Show expected vs actual results and downstream blast radius ($1.2M exposure).

### 7. Stakeholder Query Workbench
- Navigate to **Query Workbench** tab.
- Open Query **Q-1048** (Chief Risk Officer variance inquiry).
- Show the 7-step investigation trail, root cause (preliminary classification mismatch), resolution evidence, and reviewer sign-off.

### 8. Regulatory Reporting Compiler
- Navigate to **Reporting Packs** tab.
- Click **Compile Latest Pack**.
- Open the compiled PDF and multi-tab XLSX workbooks displaying executive summaries, reconciliation tables, and maker-checker signatures.

### 9. Controlled Analyst Copilot & Red-Team Verifier
- Navigate to **Analyst Copilot** tab.
- Ask: *"What drove the NSFR movement this quarter?"*
- Observe grounded response and green **NUMERICALLY VERIFIED** badge.
- Click **Test Adversarial Attack**.
- Observe the verifier catch the injected hallucinated number (149.99%) and display the red **OUTPUT QUARANTINED** alert.
