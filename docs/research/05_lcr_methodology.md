# 05 Liquidity Coverage Ratio (LCR) Methodology Specification

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-05  
**Primary Standard**: BCBS 238 ("Basel III: The Liquidity Coverage Ratio and liquidity risk monitoring tools", January 2013)  
**Status**: Authoritative Reference Documentation  

---

## 1. Regulatory Authority and Formula Definition

The Liquidity Coverage Ratio (LCR) promotes the short-term resilience of the liquidity risk profile of a bank by ensuring that it has sufficient unencumbered High-Quality Liquid Assets (HQLA) to survive an acute stress scenario lasting 30 calendar days.

$$\text{LCR} = \frac{\text{Stock of High-Quality Liquid Assets (HQLA)}}{\text{Total Net Cash Outflows over 30 Calendar Days}} \times 100\% \ge 100.0000\%$$

Where:
- **Stock of HQLA** is the total value of liquid assets after regulatory haircuts and after applying the 40% cap on Level 2 assets and 15% cap on Level 2B assets.
- **Total Net Cash Outflows** is calculated as:
$$\text{Total Net Cash Outflows} = \text{Total Expected Outflows} - \min\Big(\text{Total Expected Inflows}, 0.75 \times \text{Total Expected Outflows}\Big)$$
The 75% inflow cap ensures that banks always retain a minimum unencumbered buffer regardless of incoming cash flows.

---

## 2. High-Quality Liquid Assets (HQLA) Composition and Haircuts

| Asset Tier | Eligible Assets (BCBS 238 §§49–64) | Haircut | Buffer Cap |
| :--- | :--- | :---: | :---: |
| **Level 1** | Cash, central bank reserves, qualifying 0% risk-weight sovereign/PSE debt securities | **0%** | Min 60% of total |
| **Level 2A** | Qualifying sovereign/PSE debt 20% RW, qualifying AA- corporate bonds | **15%** | Max 40% of total |
| **Level 2B** | Qualifying BBB corporate bonds, qualifying residential mortgage-backed securities | **50%** | Max 15% of total |

### HQLA Cap Adjustment Calculation
If $\text{Level 2A} + \text{Level 2B} > 0.40 \times \text{Adjusted Total}$, or $\text{Level 2B} > 0.15 \times \text{Adjusted Total}$, the excess is removed from the qualifying stock of HQLA.

---

## 3. 30-Day Cash Outflow Schedules and Run-Off Rates

| Category | Description | Run-Off Rate | Synthetic Mapping |
| :--- | :--- | :---: | :--- |
| **Stable Retail Deposits** | Fully insured, transactional/relationship checking and savings accounts | **5.0%** | Insured retail demand deposits |
| **Less Stable Retail Deposits** | Uninsured retail deposits, internet-only brokered deposits | **10.0%** | Uninsured retail high-net-worth balances |
| **Operational Corporate Deposits** | Corporate cash management, payroll, and custodial balances | **25.0%** | Corporate operational accounts |
| **Non-Operational Corporate Deposits** | Commercial deposits not tied to daily operational services | **40.0%** | Corporate term & wholesale liquidity deposits |
| **Financial Institution Deposits** | Unsecured deposits from other banks, hedge funds, broker-dealers | **100.0%** | Interbank short-term borrowings |
| **Maturing Wholesale Debt** | Commercial paper and certificates of deposit maturing in $\le 30\text{ days}$ | **100.0%** | Wholesale debt $< 30\text{D}$ |
| **Committed Credit Facilities** | Undrawn committed credit lines provided to non-financial corporates | **10.0%** | Corporate credit lines |
| **Committed Liquidity Facilities** | Undrawn committed liquidity lines provided to financial entities | **40.0%** | Financial institution liquidity backup |

---

## 4. 30-Day Cash Inflow Schedules and Inflow Cap

Inflows are contractual cash receipts expected within the 30-day stress window:

| Category | Description | Inflow Rate | Synthetic Mapping |
| :--- | :--- | :---: | :--- |
| **Retail Loan Inflows** | Contractual principal repayments due from individuals $\le 30\text{ days}$ | **50%** | Retail loan monthly amortizations |
| **Corporate Loan Inflows** | Contractual principal repayments due from non-financial corporates $\le 30\text{ days}$ | **50%** | Corporate loan amortizations |
| **Financial Counterparty Inflows**| Contractual repayments from banks and financial institutions $\le 30\text{ days}$ | **100%** | Maturing reverse repo / interbank claims |

$$\text{Eligible Inflow} = \min\big(\text{Gross Inflows}, 0.75 \times \text{Gross Outflows}\big)$$

---

## 5. Educational Simulation Documentation and Simplifications

The Liquidity Twin models the complete BCBS 238 logic with the following documented simplifications:
1. **Intraday Liquidity**: Modeled as daily end-of-day settlement rather than minute-by-minute clearing buffers.
2. **Derivative Collateral Outflows**: Modeled using standard Lookback Historical Approach (LHA) without full ISDA CSA margin simulation.
3. **Foreign Exchange Stress**: Multi-currency positions are consolidated into USD base reporting currency using spot valuation rather than per-currency LCR sub-ring-fencing.

---

## 6. Metadata and Methodology Governance

```yaml
rule_name: Liquidity Coverage Ratio Calculation Engine
rule_version: 3.2.0
effective_date: 2026-01-01
source_name: Basel Committee on Banking Supervision (BCBS)
source_url: https://www.bis.org/bcbs/publ/d238.htm
source_access_date: 2026-10-01
methodology_note: >
  Direct implementation of BCBS 238 rules. Level 1/2A/2B haircuts, 40%/15% buffer caps,
  run-off schedules, and the 75% inflow ceiling strictly conform to Basel III standards.
