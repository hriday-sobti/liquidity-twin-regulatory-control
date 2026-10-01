# 06 Regulatory Classification Engine Specification

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-06  
**Status**: Authoritative Reference Documentation  

---

## 1. The Classification Mandate

In production banking systems, one of the most persistent sources of audit findings and regulatory fines is **misclassification**—mapping an internal core banking product or subledger account to an incorrect regulatory category.

A single misclassification cascades directly into:
$$\text{Account} \longrightarrow \text{Category} \longrightarrow \text{Factor Error} \longrightarrow \text{Distorted ASF/RSF} \longrightarrow \text{Inaccurate NSFR/LCR} \longrightarrow \text{Flawed Filing}$$

The Liquidity Twin implements a centralized, versioned, rule-driven classification engine that isolates regulatory mapping logic from raw transaction processing.

---

## 2. Classification Architecture and Pipeline

```
+----------------------------------------------------------------------------------+
|                            INPUT: RAW SOURCE POSITION                            |
| account_id, product_type, balance, counterparty_type, residual_maturity,         |
| encumbrance_status, rating, is_operational, is_insured                           |
+----------------------------------------------------------------------------------+
                                        │
                                        ▼
+----------------------------------------------------------------------------------+
|                           RULE-DRIVEN MATCHING ENGINE                            |
| 1. Filter active rules where effective_from <= business_date <= effective_to     |
| 2. Match instrument_type and counterparty_type                                   |
| 3. Evaluate maturity boundary: [0, 6M), [6M, 1Y), [1Y, inf)                      |
| 4. Check encumbrance and insurance / operational predicates                      |
+----------------------------------------------------------------------------------+
                                        │
                                        ▼
+----------------------------------------------------------------------------------+
|                        OUTPUT: REGULATORY ATTRIBUTION                            |
| regulatory_category_id, asf_factor, rsf_factor, lcr_outflow_rate,                |
| lcr_inflow_rate, rule_id, rule_version                                           |
+----------------------------------------------------------------------------------+
```

---

## 3. Decision Matrix and Predicate Evaluation

### Available Stable Funding (ASF) Liability Classification

```
IF liability_side:
  IF counterparty IN ('RETAIL', 'SMALL_BUSINESS'):
    IF is_insured AND (is_transactional OR relationship_years >= 1):
      --> ASF_RETAIL_STABLE (ASF = 95%)
    ELSE:
      --> ASF_RETAIL_LESS_STABLE (ASF = 90%)
  
  ELSE IF counterparty IN ('NON_FINANCIAL_CORPORATE', 'SOVEREIGN', 'PSE'):
    IF residual_maturity >= 1Y:
      --> ASF_CAPITAL_TIER1_2 (ASF = 100%)
    ELSE:
      --> ASF_WHOLESALE_NON_FIN (ASF = 50%)
      
  ELSE IF counterparty == 'FINANCIAL_INSTITUTION':
    IF residual_maturity >= 1Y:
      --> ASF_CAPITAL_TIER1_2 (ASF = 100%)
    ELSE IF is_operational:
      --> ASF_OPERATIONAL_DEP (ASF = 50%)
    ELSE IF residual_maturity >= 6M:
      --> ASF_OTHER_LIAB_6M_1Y (ASF = 50%)
    ELSE:
      --> ASF_SHORT_FINANCIAL (ASF = 0%)
      
  ELSE IF product_type == 'EQUITY_CAPITAL':
    --> ASF_CAPITAL_TIER1_2 (ASF = 100%)
```

### Required Stable Funding (RSF) Asset Classification

```
IF asset_side:
  IF is_encumbered:
    --> RSF_OTHER_ASSETS (RSF = 100%)
    
  ELSE IF product_type == 'CASH_CENTRAL_BANK':
    --> RSF_CASH_CENTRAL_BANK (RSF = 0%)
    
  ELSE IF product_type == 'SOVEREIGN_BOND' AND risk_weight == 0:
    --> RSF_HQLA_LEVEL1 (RSF = 5%)
    
  ELSE IF product_type IN ('AGENCY_BOND', 'CORP_BOND_AA') AND risk_weight <= 20:
    --> RSF_HQLA_LEVEL2A (RSF = 15%)
    
  ELSE IF product_type == 'RESIDENTIAL_MORTGAGE':
    IF risk_weight <= 35:
      --> RSF_RESIDENTIAL_MORT_35 (RSF = 50%)
    ELSE:
      --> RSF_RESIDENTIAL_MORT_OTHER (RSF = 65%)
      
  ELSE IF counterparty IN ('NON_FINANCIAL_CORPORATE', 'RETAIL'):
    IF residual_maturity < 1Y:
      --> RSF_LOANS_NON_FIN_SHORT (RSF = 50%)
    ELSE IF risk_weight <= 35:
      --> RSF_LOANS_LONG_LOW_RW (RSF = 65%)
    ELSE:
      --> RSF_LOANS_LONG_HIGH_RW (RSF = 85%)
      
  ELSE IF product_type == 'LOAN_FINANCIAL':
    IF residual_maturity < 6M AND secured_by_level1:
      --> RSF_LOANS_FIN_SEC_L1 (RSF = 10%)
    ELSE IF residual_maturity < 6M:
      --> RSF_LOANS_FIN_SHORT (RSF = 15%)
    ELSE:
      --> RSF_OTHER_ASSETS (RSF = 100%)
      
  ELSE:
    --> RSF_OTHER_ASSETS (RSF = 100%)
```

---

## 4. Residual Maturity Bucketing Precision

Residual maturity is evaluated strictly relative to the reporting business date $D_{\text{business}}$:

$$\Delta t = D_{\text{maturity}} - D_{\text{business}} \quad (\text{days})$$

Standard BCBS bucketing:
- **Bucket 1 (Short)**: $\Delta t < 180\text{ days}$ ($< 6\text{ months}$)
- **Bucket 2 (Medium)**: $180\text{ days} \le \Delta t < 365\text{ days}$ ($6\text{ months to } < 1\text{ year}$)
- **Bucket 3 (Long)**: $\Delta t \ge 365\text{ days}$ ($\ge 1\text{ year}$) or perpetual

---

## 5. Metadata and Methodology Governance

```yaml
rule_name: Regulatory Classification Rule Engine
rule_version: 3.2.0
effective_date: 2026-01-01
source_name: Basel Committee on Banking Supervision (BCBS 295 / BCBS 238)
source_url: https://www.bis.org/bcbs/publ/d295.htm
source_access_date: 2026-10-01
methodology_note: >
  Defines deterministic predicate evaluation for counterparty, product, maturity,
  and encumbrance state mapping to Basel regulatory factors.
