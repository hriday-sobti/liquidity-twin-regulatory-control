# 09 Regulatory Data Lineage Graph and Blast-Radius Architecture

**System Context**: LIQUIDITY TWIN — Controlled Synthetic Regulatory Liquidity Simulation and Reporting Environment  
**Document Reference**: DOC-RES-09  
**Status**: Authoritative Reference Documentation  

---

## 1. The Lineage Differentiator: Bidirectional Provenance

Most banking dashboards are one-way projections: numbers enter from a database and are rendered on a screen. When a regulator or senior committee asks *"Why is this line item $842.3M?"*, analysts are forced to spend days digging through SQL scripts, Excel macros, and subledger dumps.

The core differentiator of the Liquidity Twin is that **the system works in both directions**:

```
FORWARD PROVENANCE:
Source Event ──► Accounting Position ──► Regulatory Category ──► Rule ──► Contribution ──► Metric ──► Report

BACKWARD PROVENANCE ("Metric Birth Certificate"):
Report Cell ──► Metric ──► ASF / RSF Drivers ──► Subledger Accounts ──► Source Records ──► Validating Controls
```

---

## 2. Formal Lineage Graph Ontology

The lineage system is modeled as a strict **Directed Acyclic Graph (DAG)** $G = (V, E)$.

### Node Taxonomy ($V$)

| Node Type | Description | Primary Attributes |
| :--- | :--- | :--- |
| `SOURCE_RECORD` | Raw financial event or transaction | `event_id`, `event_type`, `amount`, `timestamp` |
| `ACCOUNTING_POSITION`| Aggregated subledger or GL balance | `account_id`, `balance`, `currency`, `entity_id` |
| `REGULATORY_CATEGORY`| Basel regulatory classification bucket | `category_code`, `framework` (NSFR/LCR) |
| `RULE` | Regulatory rule specifying weights | `rule_id`, `rule_version`, `factor` |
| `ASF_CONTRIBUTION` | Available stable funding weighted dollar amount | `contribution_id`, `weighted_amount`, `factor` |
| `RSF_CONTRIBUTION` | Required stable funding weighted dollar amount | `contribution_id`, `weighted_amount`, `factor` |
| `METRIC` | High-level regulatory KPI | `metric_name` (NSFR, LCR), `ratio_value`, `snapshot_id`|
| `CONTROL` | Automated validation check | `control_id`, `family`, `status` (PASS/FAIL) |
| `REPORT_LINE` | Formal line item in regulatory pack | `report_id`, `schedule`, `line_number`, `cell_value` |
| `EXCEPTION` | Flagged data break or audit anomaly | `exception_id`, `severity`, `status` |

### Edge Taxonomy ($E$)

- `AGGREGATES`: Source records rolled up into an accounting position.
- `CLASSIFIED_AS`: Accounting position mapped to a regulatory category.
- `GOVERNED_BY`: Regulatory category bound to a specific regulatory rule version.
- `CALCULATES`: Category and rule evaluated to yield an ASF/RSF contribution.
- `COMPOUNDS_INTO`: Contributions aggregated into final metric numerator/denominator.
- `VALIDATES`: Control rule validating an accounting position or metric node.
- `DISCLOSES`: Metric or contribution rendered into a formal report line.
- `AFFECTS`: Exception or break impacting a downstream node.

---

## 3. Bidirectional Traversal Algorithms

### Backward Traversal: The Metric Birth Certificate
Given any metric node $v_{\text{metric}}$ (e.g., `NSFR = 117.6%`):
1. Find incoming edges $u \in \text{Predecessors}(v_{\text{metric}})$ where $u.\text{type} \in \{\text{ASF\_CONTRIBUTION}, \text{RSF\_CONTRIBUTION}\}$.
2. For each contribution, find its assigned `RULE` and `REGULATORY_CATEGORY`.
3. Traverse backward to all contributing `ACCOUNTING_POSITION` nodes.
4. Drill down to individual supporting `SOURCE_RECORD` events.
5. Collect all `CONTROL` nodes associated with every step in the path.

This produces an immutable **Lineage Certificate** proving mathematical and operational validity.

### Forward Traversal: Control Blast-Radius Analysis
Given a failed control $c_{\text{failed}}$ attached to position $p_0$:
1. Perform Breadth-First Search (BFS) over all downstream reachable nodes $\text{Descendants}(p_0)$.
2. Partition reached nodes by type:
   - **Direct Impact**: Immediate regulatory category and contribution nodes.
   - **Indirect Impact**: Final liquidity metrics (NSFR / LCR).
   - **Reporting Impact**: Affected report schedules and published PDF/XLSX cells.
3. Compute total monetary value at risk:
$$\text{Monetary Exposure} = \sum_{p \in \text{ImpactedPositions}} |\text{Balance}(p)|$$

---

## 4. Metadata and Methodology Governance

```yaml
rule_name: Directed Acyclic Graph Lineage Engine
rule_version: 2.0.0
effective_date: 2026-01-01
source_name: BCBS 239 / OpenLineage Standard
source_url: https://www.bis.org/publ/bcbs239.htm
source_access_date: 2026-10-01
methodology_note: >
  Graph-theoretic implementation using NetworkX in Python and React Flow in the UI.
  Guarantees cycle-free DAG lineage, backward auditability, and automated blast-radius calculation.
