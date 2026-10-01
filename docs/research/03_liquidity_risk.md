# 03 Liquidity Risk: Structural Transformation, Runs, and Regulatory Buffers

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-03  
**Status**: Authoritative Reference Documentation  

---

## 1. The Duality of Liquidity Risk: Funding vs. Market

Liquidity risk in banking is the risk that a financial institution will be unable to meet its contractual payment obligations as they fall due without incurring unacceptable losses.

It manifests in two interconnected forms:

1. **Funding Liquidity Risk**: The risk that the bank cannot settle payment demands, repay maturing wholesale liabilities, or meet depositor withdrawals due to a cash deficit or an inability to obtain new borrowings.
2. **Market Liquidity Risk**: The risk that the bank cannot liquidate or monetize an asset rapidly at low cost without suffering a prohibitive price discount (fire-sale risk).

The dangerous feedback loop between the two is known as a **liquidity spiral**:
$$\text{Wholesale funding dries up} \longrightarrow \text{Bank forced to sell assets} \longrightarrow \text{Asset prices drop} \longrightarrow \text{Margins and haircuts rise} \longrightarrow \text{Funding shrinks further}$$

---

## 2. Maturity Transformation and Inherent Vulnerability

Banks perform the essential economic function of **maturity transformation**: borrowing short-term from depositors and lending long-term to homebuyers and enterprises.

$$\text{Short-Term Liabilities (Demand / 30D / 90D)} \Longrightarrow \text{Long-Term Illiquid Assets (5Y / 10Y / 25Y)}$$

This transformation exposes the bank to **refinancing and rollover risk**:
- If depositors or wholesale lenders refuse to roll over their claims, the bank cannot instantly liquidate its 25-year mortgage book or 5-year corporate loans.
- In the absence of an adequate unencumbered liquidity buffer, a solvent bank (Assets > Liabilities) can suffer immediate technical insolvency via a liquidity run.

---

## 3. Structural Run Dynamics and Contagion Channels

Under market or counterparty stress, liquidity drains occur through distinct behavioral channels:

1. **Retail Run**: In modern banking, digital and mobile banking enables instant transfer of funds. However, retail deposits covered by deposit insurance remain relatively sticky.
2. **Wholesale Run**: Uninsured corporate treasuries and financial counterparties flee first. Wholesale lenders do not renew maturing commercial paper, certificates of deposit, or repo arrangements.
3. **Contingent Drawdowns**: Corporate clients facing market stress immediately draw down their pre-committed revolving credit lines to hoard cash, shifting off-balance sheet contingent commitments directly onto the bank's funded asset ledger.
4. **Collateral Calls**: Rating downgrades or asset price declines trigger additional margin calls on derivative liabilities and secured borrowing.

---

## 4. The Post-Crisis Regulatory Architecture: LCR and NSFR

Following the 2007–2008 Global Financial Crisis and subsequent liquidity shocks, the Basel Committee on Banking Supervision (BCBS) instituted a two-pillar liquidity framework to address both short-term acute stress and structural funding imbalances:

```
+-----------------------------------------------------------------------------+
|                          BASEL III LIQUIDITY FRAMEWORK                       |
+------------------------------------+----------------------------------------+
| LIQUIDITY COVERAGE RATIO (LCR)     | NET STABLE FUNDING RATIO (NSFR)        |
| Standard: BCBS 238                 | Standard: BCBS 295                     |
+------------------------------------+----------------------------------------+
| Time Horizon: 30 Calendar Days     | Time Horizon: 1 Year (Structural)      |
| Objective: Acute Stress Survival   | Objective: Long-Term Structural Health |
| Stress Type: Severe multi-notch    | Metric: Available Stable Funding (ASF) |
|   downgrade, wholesale freeze,     |         divided by                     |
|   retail deposit outflow           |         Required Stable Funding (RSF)  |
| Minimum Threshold: >= 100%         | Minimum Threshold: >= 100%             |
| Numerator: High-Quality Liquid     | Numerator: ASF (Capital, Long-Term     |
|   Assets (HQLA) after haircuts     |   Funding, Stable Retail Deposits)     |
| Denominator: Total Net Cash        | Denominator: RSF (Assets & Off-Balance |
|   Outflows over 30 days            |   Sheet items weighted by illiquidity) |
+------------------------------------+----------------------------------------+
```

---

## 5. Metadata and Methodology Governance

```yaml
rule_name: Bank Liquidity Risk and Regulatory Buffer Rationale
rule_version: 1.0.0
effective_date: 2026-01-01
source_name: Basel Committee on Banking Supervision (BCBS)
source_url: https://www.bis.org/bcbs/publ/d238.htm
source_access_date: 2026-10-01
methodology_note: >
  Provides theoretical and empirical grounding for funding liquidity risk,
  asset liquidity haircuts, and the dual-horizon regulatory defense (LCR 30D / NSFR 1Y).
