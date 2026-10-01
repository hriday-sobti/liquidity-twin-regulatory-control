# 01 Financial Basics: Double-Entry Bookkeeping and Balance-Sheet Identities

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-01  
**Status**: Authoritative Reference Documentation  

---

## 1. Core Accounting Identity and Invariance

At the foundation of any financial institution's accounting architecture lies the fundamental double-entry equation:

$$\text{Assets} = \text{Liabilities} + \text{Equity}$$

In an active commercial banking ledger, this identity must hold strictly at all times across all legal entities, currencies, and consolidated reporting perimeters. 

### Balance Sheet Components

1. **Assets ($A$)**: Economic resources controlled by the bank resulting from past transactions, from which future economic benefits are expected to flow. For a bank, assets are predominantly financial claims:
   - Cash and central bank reserves
   - High-Quality Liquid Assets (government and public-sector debt securities)
   - Loans and advances to retail, small business, and corporate borrowers
   - Interbank placements and reverse repurchase agreements
   - Other financial assets and physical premises

2. **Liabilities ($L$)**: Present obligations of the bank arising from past events, the settlement of which is expected to result in an outflow of economic benefits:
   - Retail deposits (demand, savings, fixed-term)
   - Corporate deposits (operational cash management balances, non-operational wholesale deposits)
   - Wholesale funding (commercial paper, certificates of deposit, medium-term notes, subordinated debt)
   - Interbank borrowings and repurchase agreements (repo)

3. **Equity ($E$)**: The residual interest in the assets of the bank after deducting all its liabilities:
   - Common Equity Tier 1 (CET1) capital: common shares, share premium, retained earnings, accumulated other comprehensive income (AOCI)
   - Additional Tier 1 (AT1) capital instruments
   - Tier 2 qualifying regulatory capital instruments

---

## 2. Temporal Mechanics: Opening, Movement, and Closing Balances

A financial position is defined over discrete accounting and reporting periods $[t_0, t_1]$. Every balance-sheet line item satisfies the fundamental roll-forward equation:

$$\text{Closing Balance}_{t_1} = \text{Opening Balance}_{t_0} + \sum \text{Inflows} - \sum \text{Outflows} + \Delta \text{Valuation}$$

Where:
- $\text{Opening Balance}_{t_0}$ is the frozen closing balance of the immediately preceding period $t_0$.
- $\sum \text{Inflows}$ represents positive balance-sheet movements (e.g., new deposit receipts, loan originations, debt issuances).
- $\sum \text{Outflows}$ represents negative balance-sheet movements (e.g., deposit withdrawals, loan amortizations/repayments, maturing funding redemption).
- $\Delta \text{Valuation}$ captures foreign exchange revaluations, amortized cost adjustments, and fair value changes through profit and loss or OCI.

### Accounting Invariant Enforcement
For any account $k$ across period $[t_0, t_1]$:
$$\epsilon_k = \text{Closing Balance}_k - \left( \text{Opening Balance}_k + \sum_{m \in \text{Movements}_k} m \right) = 0$$

If $|\epsilon_k| > 0$, an **Accounting Break Exception** is flagged immediately. Under the Liquidity Twin governance protocol, an unreconciled accounting break blocks final regulatory sign-off and reporting generation.

---

## 3. Product Types and Balance-Sheet Roles

| Product Group | Typical Side | Liquidity Horizon | Contractual vs. Behavioral Nature |
| :--- | :--- | :--- | :--- |
| **Current / Transaction Accounts** | Liability | Instant / On Demand | Contractually overnight; behaviorally sticky if granular retail |
| **Term Deposits** | Liability | 1M to 5Y | Fixed contractual maturity; subject to early breakage risk |
| **Wholesale Certificates of Deposit** | Liability | 1M to 12M | Fixed contractual maturity; strictly non-sticky at maturity |
| **Senior Unsecured Bonds** | Liability | 3Y to 10Y | Long-term stable wholesale funding |
| **Retail Mortgages** | Asset | 15Y to 30Y | Long-term asset; amortizing contractual schedule, subject to prepayment |
| **Corporate Revolving Credit Lines** | Off-Balance Sheet | 1Y to 5Y | Contingent liquidity commitment; drawdown creates immediate cash outflow |
| **Sovereign Treasury Bills** | Asset | 1M to 12M | Unencumbered Level 1 HQLA; readily monetizable via central bank repo |

---

## 4. Financial Precision and Computational Standards

Financial calculations in the Liquidity Twin must never use unchecked floating-point arithmetic. Floating-point IEEE-754 approximations cause rounding drift (e.g., `0.1 + 0.2 != 0.3`), which invalidates reconciliation controls and audit trails.

- **Storage Precision**: All balance-sheet monetary amounts are represented as fixed-point numbers with 4 decimal places (`NUMERIC(24, 4)` in SQL; Python `Decimal` with `ROUND_HALF_EVEN` banking rounding).
- **Exchange Rates**: Stored to 6 decimal places (`NUMERIC(18, 6)`).
- **Ratios and Percentages**: Computed to 4 decimal places (e.g., `117.6254%` stored as `1.1763` or `117.6254` depending on convention).

---

## 5. Metadata and Methodology Governance

```yaml
rule_name: Standard Financial Double-Entry and Balance Identity Framework
rule_version: 1.0.0
effective_date: 2026-01-01
source_name: International Accounting Standards Board (IASB) / Basel Committee on Banking Supervision (BCBS)
source_url: https://www.bis.org/bcbs/publ/d295.htm
source_access_date: 2026-10-01
methodology_note: >
  Defines foundational ledger double-entry invariance, temporal balance roll-forwards,
  product taxonomy, and decimal computation precision for the synthetic bank.
