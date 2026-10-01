# 02 Bank Balance-Sheet Structure and Dynamics

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-02  
**Status**: Authoritative Reference Documentation  

---

## 1. Commercial Bank Balance-Sheet Architecture

A commercial bank's balance sheet differs fundamentally from that of a non-financial corporation. For a non-financial firm, debt is a financing mechanism for physical or operating capital. For a bank, deposits and wholesale debt are the primary raw material of the business, used to fund loans and liquidity assets.

```
+------------------------------------------------------------------------------------+
|                                  SYNTHETIC BANK                                    |
|                              TOTAL ASSETS = $1,050M                                |
+-------------------------------------------------+----------------------------------+
| ASSETS ($1,050M)                                | LIABILITIES & EQUITY ($1,050M)   |
+-------------------------------------------------+----------------------------------+
| 1. Cash & Central Bank Reserves        $65.0M   | 1. Retail Deposits               |
| 2. High-Quality Liquid Assets (Securities)      |    - Stable (Insured)     $180.0M  |
|    - Level 1 Sovereign Bonds          $115.0M   |    - Less Stable           $95.0M  |
|    - Level 2A Corporate/Agency Bonds   $45.0M   | 2. Corporate Deposits            |
| 3. Interbank Placements / Reverse Repo $35.0M   |    - Operational Cash Mgmt $140.0M |
| 4. Retail Loans & Residential Mortgages         |    - Non-Operational Term  $195.0M |
|    - Prime Mortgages (<35% RW)        $280.0M   | 3. Wholesale Funding             |
|    - Consumer Unsecured Loans          $60.0M   |    - Interbank Borrowing   $45.0M  |
| 5. Corporate & Commercial Loans                 |    - Certificates of Dep.  $85.0M  |
|    - Non-financial Corporate Loans    $390.0M   |    - Senior Medium-Term Notes $160M|
| 6. Other Assets / Fixed Premises       $60.0M   | 4. Other Liabilities & Accruals $30M|
|                                                 | 5. Regulatory Equity & Capital   |
|                                                 |    - CET1 & Retained Earnings $95M |
|                                                 |    - Tier 2 Subordinated Debt $25M |
+-------------------------------------------------+----------------------------------+
| OFF-BALANCE SHEET COMMITMENTS                   | TOTAL LIABILITIES & EQUITY       |
| Committed Undrawn Credit & Liquidity: $120.0M   |                          $1,050M |
+-------------------------------------------------+----------------------------------+
```

---

## 2. Asset Structure and Liquidity Tiers

Bank assets are organized by a trade-off between yield and liquidity:

1. **Cash and Central Bank Reserves**: Completely liquid, 0% haircut, immediate availability for intraday payment clearing and liquidity buffers.
2. **High-Quality Liquid Assets (HQLA)**: Unencumbered marketable debt securities that can be liquidated or pledged in central bank standing facilities without material discount or fire-sale price impact.
3. **Short-Term Interbank Assets**: Reverse repurchase agreements and call placements with high-credit counterparties.
4. **Performing Customer Loans**: Illiquid earning assets with defined repayment schedules. Cash inflows are contractual, but selling loan books in a crisis incurs heavy haircuts.
5. **Non-Performing Assets and Illiquid Premises**: Fixed assets, software, property, and defaulted exposures that provide zero reliable liquidity in stress.

---

## 3. Liability Structure and Stability Profiles

Liabilities fund the asset book and are differentiated by customer relationship, contractual maturity, and behavioral stickiness:

1. **Retail Deposits**: Granular deposits from individuals. When insured by a formal deposit insurance scheme (e.g., FDIC / FSCS equivalent) and tied to transactional salary accounts, they exhibit high behavioral persistence even in market crises.
2. **Operational Wholesale Deposits**: Deposits from commercial clients necessary for daily clearing, custody, payroll, and cash management activities. Withdrawing these balances disrupts the corporate's core operations; hence they are moderately sticky.
3. **Non-Operational Corporate Deposits**: Excess liquidity deposited by institutional treasuries or corporations seeking yield. Highly sensitive to credit spreads, counterparty risk, and rate shifts.
4. **Wholesale Term Debt**: Commercial paper (CP), negotiable certificates of deposit (CDs), and medium-term notes (MTNs). Highly predictable contractual maturities, but susceptible to complete rollover refusal upon maturity during stress.

---

## 4. Contractual vs. Behavioral Maturity

The contractual maturity date is the legally enforceable termination date of an instrument. However, bank balance-sheet management and regulatory liquidity frameworks (BCBS NSFR / LCR) recognize behavioral reality:

- **Demand Deposits**: Contractual maturity is overnight ($T+0$), but the behavioral sticky core may remain stable for years.
- **Retail Mortgages**: Contractual maturity may be 25 years ($300\text{ months}$), but prepayments shorten the effective duration to 5–7 years.
- **Revolving Credit Lines**: Contractual expiry may be 2 years, but the borrower may draw funds at will under liquidity stress.

Under regulatory NSFR guidelines (BCBS 295), regulatory factors apply strictly to **contractual residual maturity** unless explicitly codified by the national supervisor (e.g., stable demand deposits receiving an ASF factor of 95% despite having no contractual maturity).

---

## 5. Asset Encumbrance and Pledged Collateral

An asset is **encumbered** if it is pledged as collateral, assigned, or subject to any form of arrangement to secure, collateralize, or credit-enhance any transaction from which it cannot be freely withdrawn.

- **Unencumbered Assets**: Can be pledged or liquidated immediately. Eligible for HQLA inclusion and lower RSF weighting.
- **Encumbered Assets**: Locked in repo, covered bond pools, or clearing house margins. Cannot support the general liquidity buffer until released.

---

## 6. Metadata and Methodology Governance

```yaml
rule_name: Commercial Bank Balance-Sheet Structural Classification
rule_version: 1.0.0
effective_date: 2026-01-01
source_name: Basel Committee on Banking Supervision (BCBS)
source_url: https://www.bis.org/bcbs/publ/d295.htm
source_access_date: 2026-10-01
methodology_note: >
  Defines asset, liability, equity, and off-balance-sheet taxonomies,
  encumbrance states, and residual maturity bucketing for the synthetic bank.
