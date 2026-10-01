# 04 Net Stable Funding Ratio (NSFR) Methodology Specification

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-04  
**Primary Standard**: BCBS 295 ("Basel III: the net stable funding ratio", October 2014)  
**Status**: Authoritative Reference Documentation  

---

## 1. Regulatory Authority and Formula Definition

The Net Stable Funding Ratio (NSFR) is designed to ensure that a financial institution maintains an ongoing, stable funding profile in relation to the composition of its assets and off-balance-sheet exposures over a one-year time horizon.

$$\text{NSFR} = \frac{\text{Available Stable Funding (ASF)}}{\text{Required Stable Funding (RSF)}} \times 100\% \ge 100.0000\%$$

Where:
- **Available Stable Funding (ASF)** is the portion of capital and liabilities expected to be reliable over the one-year horizon.
- **Required Stable Funding (RSF)** is the portion of assets and off-balance-sheet commitments that require funding based on their liquidity characteristics, residual maturity, and encumbrance.

---

## 2. Available Stable Funding (ASF) Classification and Factors

Every liability and equity item on the balance sheet is assigned an ASF factor based on counterparty type, contractual maturity, and behavioral stickiness:

| ASF Factor | Regulatory Category | Description & Criteria (BCBS 295 §§17–31) | Synthetic Product Mapping |
| :---: | :--- | :--- | :--- |
| **100%** | `ASF_CAPITAL_TIER1_2` | Regulatory capital (CET1, AT1, Tier 2) instruments and other liabilities with effective residual maturity $\ge 1\text{ year}$. | Common equity, retained earnings, subordinated term debt $\ge 1\text{Y}$. |
| **95%** | `ASF_RETAIL_STABLE` | "Stable" retail and small business deposits (fully covered by an explicit deposit insurance scheme; transactional account or established relationship), residual maturity $< 1\text{ year}$. | Insured retail checking/savings, insured retail term deposits $< 1\text{Y}$. |
| **90%** | `ASF_RETAIL_LESS_STABLE`| "Less stable" retail and small business deposits (uninsured, high-balance, or non-relationship), residual maturity $< 1\text{ year}$. | Uninsured retail deposits, internet-only brokered deposits $< 1\text{Y}$. |
| **50%** | `ASF_WHOLESALE_NON_FIN` | Funding provided by non-financial corporates, sovereigns, PSEs, and multilateral development banks with residual maturity $< 1\text{ year}$. | Non-operational corporate deposits, corporate commercial paper $< 1\text{Y}$. |
| **50%** | `ASF_OPERATIONAL_DEP` | Operational deposits provided by financial institutions (cash management, clearing, custody balances). | Financial institution operational clearing accounts. |
| **50%** | `ASF_OTHER_LIAB_6M_1Y` | Funding from financial institutions and other entities with residual maturity $\ge 6\text{ months}$ and $< 1\text{ year}$. | Wholesale certificates of deposit ($6\text{M} \le \text{maturity} < 1\text{Y}$). |
| **0%** | `ASF_SHORT_FINANCIAL` | All other liabilities from financial institutions, central banks, and broker-dealers with residual maturity $< 6\text{ months}$. | Overnight interbank borrowings, short repo funding $< 6\text{M}$. |
| **0%** | `ASF_OTHER_ZERO` | Derivative liabilities, trade payables, and other non-funding liabilities with residual maturity $< 6\text{ months}$. | Net negative derivative mark-to-market balances. |

---

## 3. Required Stable Funding (RSF) Classification and Factors

Every asset on the balance sheet, plus designated off-balance-sheet commitments, is assigned an RSF factor based on liquidity monetization potential, residual maturity, and encumbrance:

| RSF Factor | Regulatory Category | Description & Criteria (BCBS 295 §§32–45) | Synthetic Asset Mapping |
| :---: | :--- | :--- | :--- |
| **0%** | `RSF_CASH_CENTRAL_BANK` | Cash, central bank reserves, claims on central banks with residual maturity $< 6\text{ months}$. | Physical vault currency, central bank clearing reserves. |
| **5%** | `RSF_HQLA_LEVEL1` | Unencumbered Level 1 High-Quality Liquid Assets (0% risk weight sovereign bonds). | US Treasury securities, sovereign debt 0% RW. |
| **10%** | `RSF_LOANS_FIN_SEC_L1` | Unencumbered loans to financial institutions with residual maturity $< 6\text{ months}$, secured by Level 1 HQLA. | Reverse repos backed by Level 1 sovereign collateral. |
| **15%** | `RSF_HQLA_LEVEL2A` | Unencumbered Level 2A HQLA (20% risk-weight sovereign/PSE debt, qualifying AA- corporate bonds). | GSE debt, corporate bonds rated AA- and higher. |
| **15%** | `RSF_LOANS_FIN_SHORT` | Unencumbered loans to financial institutions with residual maturity $< 6\text{ months}$ not secured by Level 1 HQLA. | Unsecured interbank placements $< 6\text{M}$. |
| **50%** | `RSF_HQLA_LEVEL2B` | Unencumbered Level 2B HQLA (qualifying BBB corporate bonds, residential mortgage-backed securities). | BBB corporate debt, qualifying RMBS. |
| **50%** | `RSF_RESIDENTIAL_MORT_35`| Unencumbered residential mortgages qualifying for a $\le 35\%$ risk weight under standardized approach. | Prime residential mortgages, LTV $\le 80\%$. |
| **50%** | `RSF_LOANS_NON_FIN_SHORT`| Loans to non-financial corporates, retail clients, sovereigns with residual maturity $< 1\text{ year}$. | Working capital corporate loans $< 1\text{Y}$. |
| **65%** | `RSF_RESIDENTIAL_MORT_OTHER`| Unencumbered residential mortgages with risk weight $> 35\%$. | Non-prime residential mortgages, LTV $> 80\%$. |
| **65%** | `RSF_LOANS_LONG_LOW_RW` | Loans to non-financial corporates and retail with maturity $\ge 1\text{ year}$ and risk weight $\le 35\%$. | High-rated corporate term loans $\ge 1\text{Y}$. |
| **85%** | `RSF_LOANS_LONG_HIGH_RW`| Loans to non-financial corporates and retail with maturity $\ge 1\text{ year}$ and risk weight $> 35\%$. | Standard commercial loans $\ge 1\text{Y}$, retail unsecured credit. |
| **85%** | `RSF_NON_HQLA_SECURITIES`| Exchange-traded equities and non-HQLA securities with residual maturity $\ge 1\text{ year}$. | Corporate equities, junior bond holdings. |
| **100%** | `RSF_OTHER_ASSETS` | Non-performing loans, physical fixed assets, software, tax assets, derivative assets, claims on financial institutions $\ge 1\text{Y}$. | Bank branches, NPLs ($>90\text{ days past due}$), derivative assets. |
| **5%** | `RSF_OBS_COMMITTED` | Undrawn committed credit and liquidity facilities provided to clients. | Undrawn revolving credit lines to corporates and retail. |

---

## 4. Analytical Driver Decomposition (Why Did NSFR Move?)

Let $NSFR = \frac{A}{R} \times 100$. The differential change in NSFR from period $t_0$ to $t_1$ is:

$$\Delta NSFR = NSFR(t_1) - NSFR(t_0) = \left( \frac{A_1}{R_1} - \frac{A_0}{R_0} \right) \times 100$$

For a balance-sheet driver $k$ (e.g., corporate deposits, wholesale funding, retail loans) causing changes $\Delta A_k$ and $\Delta R_k$:
$$\text{Contribution}_k \approx \frac{\Delta A_k}{R_0} \times 100 - \frac{A_0 \cdot \Delta R_k}{R_0^2} \times 100 + \text{Interacting Terms}$$

In the Liquidity Twin engine, we implement exact Shapley value decomposition to guarantee that the sum of all individual driver contributions reconciles exactly to $\Delta NSFR$:
$$\sum_{k=1}^K \text{Contribution}_k = \Delta NSFR$$

---

## 5. Metadata and Methodology Governance

```yaml
rule_name: Net Stable Funding Ratio Calculation Engine
rule_version: 3.2.0
effective_date: 2026-01-01
source_name: Basel Committee on Banking Supervision (BCBS)
source_url: https://www.bis.org/bcbs/publ/d295.htm
source_access_date: 2026-10-01
methodology_note: >
  Direct implementation of BCBS 295 rules. Factor schedules, maturity thresholds,
  and off-balance-sheet weights strictly conform to Basel III standards.
