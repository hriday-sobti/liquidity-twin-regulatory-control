# Methodological Assumptions & Educational Simplifications

**System Context**: Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Governance Standard**: Basel Committee on Banking Supervision (BCBS 295 / 238)  

---

## 1. Regulatory Alignment & Documented Simplifications

To ensure this simulation functions reliably in an on-premises or developer environment without external market feeds or proprietary core-banking mainframes, the following explicit assumptions are documented:

1. **Intraday Liquidity Monitoring**: Modeled as daily end-of-day balances and 30-day forward cash flow schedules rather than minute-by-minute real-time gross settlement (RTGS) queue monitoring.
2. **Derivative Collateral Outflows**: Modeled using standard Lookback Historical Approach (LHA) proxies rather than continuous ISDA CSA margin valuation engines.
3. **Multi-Currency Consolidation**: Foreign currency positions (EUR, GBP, SGD, INR) are revalued to USD base currency using spot exchange rates at snapshot cutoff rather than per-currency ring-fenced LCR sub-ratios.
4. **Behavioral Tenor vs. Contractual Tenor**: In accordance with BCBS 295, contractual residual maturity governs factor assignments except where explicit supervisory treatments exist (e.g. 95% ASF on stable demand deposits).

---

## 2. Synthetic Data Generation Assumptions

1. **Seed Reproducibility**: All synthetic customers, accounts, instruments, and transactions are deterministically generated via random seed `42`. Any clean instance generates the exact same portfolio down to the cent.
2. **Institutional Demarcation**: The modeled institution (`ENT-001`, "Synthetic Benchmark Bank NA") is completely synthetic. No non-public commercial bank data, confidential supervisory communications, or customer information has been used.
