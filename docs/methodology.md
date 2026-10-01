# Quantitative & Regulatory Methodology Reference

**Standard References**: BCBS 295 (NSFR), BCBS 238 (LCR), BCBS 239 (Risk Data Governance)  

---

## 1. Net Stable Funding Ratio (NSFR) Methodology

The Net Stable Funding Ratio requires banks to maintain a stable funding profile in relation to the composition of their assets and off-balance-sheet exposures over a one-year horizon:

$$\text{NSFR} = \frac{\text{Available Stable Funding (ASF)}}{\text{Required Stable Funding (RSF)}} \times 100\% \ge 100.0000\%$$

### 1.1 Available Stable Funding (ASF) Schedule
Every liability and capital instrument is weighted according to funding stability:

| ASF Factor | Regulatory Category | Description | Primary Mapping |
| :---: | :--- | :--- | :--- |
| **100%** | `ASF_CAPITAL_TIER1_2` | Regulatory capital and liabilities with residual maturity $\ge 1\text{ year}$. | Common equity, retained earnings, subordinated term debt $\ge 1\text{Y}$. |
| **95%** | `ASF_RETAIL_STABLE` | Fully insured retail demand and term deposits with transactional relationship. | Insured retail checking/savings accounts. |
| **90%** | `ASF_RETAIL_LESS_STABLE` | Uninsured or high-net-worth retail deposits. | High-balance retail deposits, internet-only deposits. |
| **50%** | `ASF_WHOLESALE_NON_FIN` | Non-financial corporate deposits and short wholesale debt $< 1\text{ year}$. | Non-operational corporate liquidity deposits. |
| **50%** | `ASF_OPERATIONAL_DEP` | Operational deposits from financial institutions (clearing, custody, cash management). | Operational clearing balances. |
| **50%** | `ASF_OTHER_LIAB_6M_1Y` | Wholesale funding from financial institutions with maturity $180\text{ days}$ to $< 1\text{ year}$. | Negotiable certificates of deposit (6M–1Y). |
| **0%** | `ASF_SHORT_FINANCIAL` | Short-term financial funding with residual maturity $< 180\text{ days}$. | Overnight interbank borrowings, short repo funding. |

### 1.2 Required Stable Funding (RSF) Schedule
Every asset and off-balance-sheet exposure is weighted according to its illiquidity and liquidation horizon:

| RSF Factor | Regulatory Category | Description | Primary Mapping |
| :---: | :--- | :--- | :--- |
| **0%** | `RSF_CASH_CENTRAL_BANK` | Central bank cash and reserves with maturity $< 180\text{ days}$. | Vault cash, central bank clearing reserves. |
| **5%** | `RSF_HQLA_LEVEL1` | Unencumbered Level 1 High-Quality Liquid Assets. | US Treasury securities, 0% risk-weight sovereign debt. |
| **10%** | `RSF_LOANS_FIN_SEC_L1` | Loans to financial entities $< 180\text{ days}$ secured by Level 1 HQLA. | Reverse repo backed by Treasury collateral. |
| **15%** | `RSF_HQLA_LEVEL2A` | Unencumbered Level 2A HQLA (sovereign 20% RW, qualifying AA- corporate bonds). | Agency debt, AA- corporate bonds. |
| **50%** | `RSF_RESIDENTIAL_MORT_35`| Residential mortgages qualifying for $\le 35\%$ risk weight. | Prime residential mortgages (LTV $\le 80\%$). |
| **50%** | `RSF_LOANS_NON_FIN_SHORT`| Non-financial corporate loans with residual maturity $< 1\text{ year}$. | Working capital commercial lines. |
| **65%** | `RSF_RESIDENTIAL_MORT_OTHER`| Residential mortgages with risk weight $> 35\%$. | Non-prime residential mortgages. |
| **65%** | `RSF_LOANS_LONG_LOW_RW` | Non-financial corporate loans $\ge 1\text{ year}$ with risk weight $\le 35\%$. | High-rated corporate term facilities. |
| **85%** | `RSF_LOANS_LONG_HIGH_RW`| Standard corporate term loans $\ge 1\text{ year}$ with risk weight $> 35\%$. | Standard commercial term loans. |
| **85%** | `RSF_NON_HQLA_SECURITIES`| Exchange-traded equities and non-HQLA securities $\ge 1\text{ year}$. | Corporate equities, junior bonds. |
| **100%** | `RSF_OTHER_ASSETS` | Non-performing loans, physical premises, tax assets, intangibles. | Branch buildings, defaulted loans ($>90\text{D past due}$). |
| **5%** | `RSF_OBS_COMMITTED` | Committed undrawn credit and liquidity facilities. | Undrawn revolving credit lines to commercial clients. |

---

## 2. Liquidity Coverage Ratio (LCR) Methodology

The Liquidity Coverage Ratio ensures banks hold sufficient unencumbered High-Quality Liquid Assets to withstand an acute 30-day liquidity stress:

$$\text{LCR} = \frac{\text{Stock of HQLA}}{\text{Total Net Cash Outflows over 30 Days}} \times 100\% \ge 100.0000\%$$

Where:
- $\text{Total Net Cash Outflows} = \text{Gross Expected Outflows} - \min\Big(\text{Gross Expected Inflows}, 0.75 \times \text{Gross Expected Outflows}\Big)$
- Level 2 assets are capped at 40% of the total adjusted buffer; Level 2B assets are capped at 15%.

---

## 3. Movement Driver Attribution (Shapley Framework)

Let $NSFR = \frac{A}{R} \times 100$. For any balance-sheet driver $i$ inducing changes $\Delta A_i$ and $\Delta R_i$:

$$\text{Contribution}_i = \left[ \frac{\Delta A_i}{R_0} - \frac{A_0 \cdot \Delta R_i}{R_0 \cdot R_1} \right] \times 100 + \text{Residual Weighting}_i$$

Guarantees exact additive reconciliation:
$$\sum_{i=1}^N \text{Contribution}_i = NSFR_1 - NSFR_0 \quad (\pm 0.0001\text{ pp})$$
