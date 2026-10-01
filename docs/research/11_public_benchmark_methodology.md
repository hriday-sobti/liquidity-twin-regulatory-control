# 11 Public Benchmark Disclosure Methodology (BCBS Pillar 3)

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-11  
**Primary Standards**: BCBS Standards for Pillar 3 Disclosure Requirements (BCBS 309, DIS30, DIS40)  
**Status**: Authoritative Reference Documentation  

---

## 1. Purpose of Public Benchmark Alignment

Under the Basel framework's **Pillar 3 (Market Discipline)**, banks are required to publish standardized quantitative liquidity tables to promote transparency and enable peer comparability.

The Liquidity Twin incorporates these standardized public templates as an architectural benchmark. This ensures that the synthetic bank's internal data model, calculation engine, and reporting compiler directly map to real-world supervisory disclosure expectations without embedding any confidential or proprietary data.

---

## 2. Standardized Public Templates

### Template 1: Table LIQ1 (DIS30) — Liquidity Coverage Ratio (LCR)
Supervisors require quarterly publication of 30-day liquidity buffer details:
- **Total Unweighted Value**: Gross balance-sheet position or contractual commitment.
- **Total Weighted Value**: Post-haircut HQLA or post-run-off cash outflow/inflow amount.
- **Reporting Tiers**:
  * High-Quality Liquid Assets (Level 1, Level 2A, Level 2B)
  * Retail deposits and small business deposits (stable vs less stable)
  * Unsecured wholesale funding (operational deposits vs non-operational)
  * Secured funding (repo collateralized by Level 1 / Level 2 assets)
  * Additional requirements (credit rating downgrades, derivative exposures, committed facilities)
  * Inflows from financial and retail counterparties (capped at 75% of total outflows)

### Template 2: Table LIQ2 (DIS40) — Net Stable Funding Ratio (NSFR)
Banks must disclose structural stable funding across four maturity intervals:
1. No contractual maturity or perpetual
2. Residual maturity $< 6\text{ months}$
3. Residual maturity between $6\text{ months}$ and $< 1\text{ year}$
4. Residual maturity $\ge 1\text{ year}$

Both the **unweighted gross value** and the **weighted ASF/RSF value** must be disclosed across all categories:
- Regulatory capital and long-term liabilities
- Retail deposits (stable vs less stable)
- Wholesale funding (operational vs non-operational)
- Cash and central bank reserves
- Securities (Level 1, Level 2A, Level 2B, non-HQLA)
- Loans to financial and non-financial counterparties
- Residential mortgages
- Off-balance-sheet commitments

---

## 3. Structural Comparison: Public Standards vs. Synthetic Bank Implementation

| Pillar 3 Concept | BCBS Public Standard (DIS30 / DIS40) | Liquidity Twin Synthetic Implementation | Alignment & Reference |
| :--- | :--- | :--- | :--- |
| **Base Currency** | Reporting entity home currency | USD base with multi-currency (EUR, GBP, SGD, INR) conversion | BCBS 295 §11 |
| **Maturity Slicing**| Demand, $<6\text{M}$, $6\text{M}-1\text{Y}$, $\ge 1\text{Y}$ | Exact 4-bucket residual maturity partition in `dim_date` / subledger | BCBS 295 §13 |
| **HQLA Haircuts** | Level 1: 0%, Level 2A: 15%, Level 2B: 50% | Exact table-driven haircuts in `regulatory_rules` | BCBS 238 §50 |
| **HQLA Caps** | Level 2 max 40%, Level 2B max 15% | Automated mathematical cap adjustment algorithm | BCBS 238 Annex 1 |
| **Inflow Ceiling** | Capped at 75% of gross cash outflows | Strict `min(inflows, 0.75 * outflows)` constraint | BCBS 238 §144 |
| **ASF Factors** | 100%, 95%, 90%, 50%, 0% | Full 8-class rule matrix applied to liabilities | BCBS 295 §§17–31 |
| **RSF Factors** | 0%, 5%, 10%, 15%, 50%, 65%, 85%, 100% | Full 14-class rule matrix applied to assets & OBS | BCBS 295 §§32–45 |

---

## 4. Methodological Demarcation Note

- **Public Methodology**: Fully derived from published, publicly accessible standards of the Bank for International Settlements (BIS).
- **Institutional Data**: 100% synthetic, generated deterministically via reproducible algorithms.
- **Proprietary Independence**: No non-public bank data, confidential supervisory communications, or proprietary bank models have been used or referenced.

---

## 5. Metadata and Methodology Governance

```yaml
rule_name: Public Regulatory Benchmark Mapping Framework
rule_version: 1.0.0
effective_date: 2026-01-01
source_name: Basel Committee on Banking Supervision (BCBS DIS30 / DIS40)
source_url: https://www.bis.org/basel_framework/chapter/DIS/40.htm
source_access_date: 2026-10-01
methodology_note: >
  Maps the synthetic bank's data schema to Basel Pillar 3 DIS30 and DIS40 public reporting tables,
  preserving total methodological fidelity while maintaining 100% synthetic data boundaries.
