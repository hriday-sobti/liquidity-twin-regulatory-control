import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import networkx as nx
from sqlalchemy.orm import Session

from backend.app.models.facts import (
    FactBalanceSheet,
    FactOffBalanceExposure,
    FactLiquidityMetric,
    FactReportingSnapshot,
    FactReportingLine,
    FactEvent,
    FactControlResult,
    FactException,
)
from backend.app.models.dimensions import DimAccount, DimProduct
from backend.app.models.regulatory import RegulatoryRule
from backend.app.models.lineage import LineageRun, LineageNode, LineageEdge


class LineageGraphBuilder:
    """
    Constructs a Directed Acyclic Graph (DAG) using NetworkX for bidirectional data lineage.
    Supports:
      1. Forward propagation: Source Event -> Position -> Rule -> Contribution -> Metric -> Report Line
      2. Backward traversal ('Metric Birth Certificate'): Report -> Metric -> Contributions -> Positions -> Events
      3. Blast-radius analysis: Failed Control -> Directly/Indirectly impacted nodes and monetary exposure.
    """

    def __init__(self, db: Session):
        self.db = db

    def build_lineage_graph(self, snapshot_id: str, persist: bool = True) -> nx.DiGraph:
        """Constructs full DAG for the snapshot."""
        G = nx.DiGraph()

        snap = self.db.query(FactReportingSnapshot).filter_by(snapshot_id=snapshot_id).first()
        if not snap:
            return G

        run_id = f"LIN-{snapshot_id}"
        balances = self.db.query(FactBalanceSheet).filter_by(snapshot_id=snapshot_id).all()
        metrics = self.db.query(FactLiquidityMetric).filter_by(snapshot_id=snapshot_id).all()
        controls = self.db.query(FactControlResult).filter_by(snapshot_id=snapshot_id).all()
        exceptions = self.db.query(FactException).filter_by(snapshot_id=snapshot_id).all()
        events = self.db.query(FactEvent).filter_by(business_date=snap.business_date).limit(50).all()

        db_nodes: List[LineageNode] = []
        db_edges: List[LineageEdge] = []

        def add_node(nid: str, ntype: str, label: str, entity_id: Optional[str] = None, props: Optional[Dict] = None):
            props = props or {}
            G.add_node(nid, type=ntype, label=label, entity_id=entity_id, **props)
            if persist:
                db_nodes.append(
                    LineageNode(
                        node_id=nid,
                        run_id=run_id,
                        node_type=ntype,
                        entity_id=entity_id,
                        label=label,
                        properties_json=json.dumps(props),
                    )
                )

        def add_edge(src: str, tgt: str, etype: str, weight: Optional[float] = None):
            if G.has_node(src) and G.has_node(tgt):
                G.add_edge(src, tgt, type=etype, weight=weight)
                if persist:
                    db_edges.append(
                        LineageEdge(
                            edge_id=f"EDGE-{src}-{tgt}",
                            run_id=run_id,
                            source_node_id=src,
                            target_node_id=tgt,
                            edge_type=etype,
                            weight=weight,
                        )
                    )

        # 1. Metric Nodes
        nsfr_nid = f"METRIC-NSFR-{snapshot_id}"
        lcr_nid = f"METRIC-LCR-{snapshot_id}"
        add_node(nsfr_nid, "METRIC", f"NSFR ({float(snap.nsfr_value if snap.nsfr_value else 0):.2f}%)", "NSFR", {"value": float(snap.nsfr_value or 0)})
        add_node(lcr_nid, "METRIC", f"LCR ({float(snap.lcr_value if snap.lcr_value else 0):.2f}%)", "LCR", {"value": float(snap.lcr_value or 0)})

        # 2. Aggregation Contribution Nodes
        asf_nid = f"CONTRIB-ASF-{snapshot_id}"
        rsf_nid = f"CONTRIB-RSF-{snapshot_id}"
        hqla_nid = f"CONTRIB-HQLA-{snapshot_id}"
        outflow_nid = f"CONTRIB-OUTFLOW-{snapshot_id}"

        add_node(asf_nid, "ASF_CONTRIBUTION", f"Available Stable Funding (${float(snap.asf_amount or 0)/1e6:.1f}M)", "ASF", {"amount": float(snap.asf_amount or 0)})
        add_node(rsf_nid, "RSF_CONTRIBUTION", f"Required Stable Funding (${float(snap.rsf_amount or 0)/1e6:.1f}M)", "RSF", {"amount": float(snap.rsf_amount or 0)})
        add_node(hqla_nid, "ASF_CONTRIBUTION", f"Total HQLA Buffer (${float(snap.hqla_amount or 0)/1e6:.1f}M)", "HQLA", {"amount": float(snap.hqla_amount or 0)})
        add_node(outflow_nid, "RSF_CONTRIBUTION", f"Net Cash Outflows (${float(snap.net_outflows_amount or 0)/1e6:.1f}M)", "OUTFLOW", {"amount": float(snap.net_outflows_amount or 0)})

        add_edge(asf_nid, nsfr_nid, "COMPOUNDS_INTO")
        add_edge(rsf_nid, nsfr_nid, "COMPOUNDS_INTO")
        add_edge(hqla_nid, lcr_nid, "COMPOUNDS_INTO")
        add_edge(outflow_nid, lcr_nid, "COMPOUNDS_INTO")

        # 3. Position and Rule Nodes
        for b in balances:
            pos_nid = f"POS-{b.balance_id}"
            acc = self.db.query(DimAccount).filter_by(account_id=b.account_id).first()
            pcode = acc.product.product_code if acc and acc.product else b.account_id
            side = acc.product.balance_sheet_side if acc and acc.product else "UNKNOWN"
            bal_m = float(b.closing_balance_usd) / 1e6

            add_node(pos_nid, "ACCOUNTING_POSITION", f"{pcode} (${bal_m:.1f}M)", b.account_id, {
                "balance": float(b.closing_balance_usd),
                "side": side,
                "residual_maturity": b.residual_maturity_days,
            })

            # Link rule
            if b.rule_id:
                rule_nid = f"RULE-{b.rule_id}"
                if not G.has_node(rule_nid):
                    add_node(rule_nid, "RULE", f"{b.rule_id}", b.rule_id)
                add_edge(rule_nid, pos_nid, "GOVERNED_BY")

            # Link to contribution nodes
            if side in ("LIABILITY", "EQUITY"):
                add_edge(pos_nid, asf_nid, "CALCULATES", weight=float(b.asf_amount))
                if pcode in ("INTERBANK_BORROW", "RET_DEMAND_INS", "CORP_OPERATIONAL", "CORP_NON_OPERATIONAL"):
                    add_edge(pos_nid, outflow_nid, "CALCULATES")
            elif side == "ASSET":
                add_edge(pos_nid, rsf_nid, "CALCULATES", weight=float(b.rsf_amount))
                if pcode in ("CASH_RESERVES", "SOV_BOND_L1", "CORP_BOND_L2A"):
                    add_edge(pos_nid, hqla_nid, "CALCULATES")

        # 4. Source Events to Positions
        for ev in events:
            ev_nid = f"EVT-{ev.event_id}"
            add_node(ev_nid, "SOURCE_RECORD", f"{ev.event_type} (${float(ev.amount)/1e6:.2f}M)", ev.event_id)
            matching_pos = f"BAL-{snapshot_id}-{ev.account_id.replace('ACC-', '')}"
            pos_nid = f"POS-{matching_pos}"
            if G.has_node(pos_nid):
                add_edge(ev_nid, pos_nid, "AGGREGATES", weight=float(ev.amount))

        # 5. Report Lines
        rep_line_nsfr = f"REP-LINE-EXEC-1.1-{snapshot_id}"
        add_node(rep_line_nsfr, "REPORT_LINE", "Executive Summary: NSFR Row", "REP-EXEC-1.1")
        add_edge(nsfr_nid, rep_line_nsfr, "DISCLOSES")

        rep_line_lcr = f"REP-LINE-EXEC-1.2-{snapshot_id}"
        add_node(rep_line_lcr, "REPORT_LINE", "Executive Summary: LCR Row", "REP-EXEC-1.2")
        add_edge(lcr_nid, rep_line_lcr, "DISCLOSES")

        # 6. Controls and Exceptions
        for c in controls[:15]:  # Key sample controls
            ctrl_nid = f"CTRL-{c.control_id}-{snapshot_id}"
            add_node(ctrl_nid, "CONTROL", f"{c.control_name} ({c.status})", c.control_id, {"status": c.status})
            if "ACC" in c.control_id or "CAL" in c.control_id:
                add_edge(ctrl_nid, nsfr_nid, "VALIDATES")

        for exc in exceptions:
            exc_nid = f"EXC-NODE-{exc.exception_id}"
            add_node(exc_nid, "EXCEPTION", f"Break: {exc.control_id} (${float(exc.estimated_impact_usd or 0)/1e6:.1f}M)", exc.exception_id, {
                "severity": exc.severity,
                "status": exc.status,
            })
            ctrl_nid = f"CTRL-{exc.control_id}-{snapshot_id}"
            if G.has_node(ctrl_nid):
                add_edge(exc_nid, ctrl_nid, "AFFECTS")

        if persist:
            # Upsert run record
            self.db.query(LineageEdge).filter_by(run_id=run_id).delete()
            self.db.query(LineageNode).filter_by(run_id=run_id).delete()
            self.db.query(LineageRun).filter_by(run_id=run_id).delete()

            run_record = LineageRun(
                run_id=run_id,
                snapshot_id=snapshot_id,
                calculation_type="FULL_CYCLE",
                calculation_version="3.2.0",
                executed_at=datetime.utcnow(),
                node_count=G.number_of_nodes(),
                edge_count=G.number_of_edges(),
            )
            self.db.add(run_record)
            self.db.flush()
            self.db.bulk_save_objects(db_nodes)
            self.db.bulk_save_objects(db_edges)
            self.db.commit()

        return G

    def get_metric_birth_certificate(self, snapshot_id: str, metric_name: str = "NSFR") -> Dict[str, Any]:
        """
        Backward traversal: Reconstructs the complete audit lineage for the metric down to source events.
        """
        G = self.build_lineage_graph(snapshot_id, persist=False)
        metric_nid = f"METRIC-{metric_name}-{snapshot_id}"
        if not G.has_node(metric_nid):
            return {"error": f"Metric node {metric_nid} not found in lineage graph."}

        # Find all upstream nodes that reach this metric
        reversed_G = G.reverse()
        ancestors = nx.descendants(reversed_G, metric_nid) | {metric_nid}
        subgraph = G.subgraph(ancestors)

        nodes = []
        for n, data in subgraph.nodes(data=True):
            nodes.append({
                "id": n,
                "type": data.get("type", "UNKNOWN"),
                "label": data.get("label", n),
                "properties": {k: v for k, v in data.items() if k not in ("type", "label")},
            })

        edges = []
        for u, v, data in subgraph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "type": data.get("type", "DEPENDS_ON"),
                "weight": float(data.get("weight")) if data.get("weight") is not None else None,
            })

        return {
            "snapshot_id": snapshot_id,
            "metric_name": metric_name,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
            "is_acyclic": nx.is_directed_acyclic_graph(subgraph),
        }

    def get_control_blast_radius(self, snapshot_id: str, control_id: str) -> Dict[str, Any]:
        """
        Forward traversal: Computes downstream impact and monetary blast-radius for a failed control.
        """
        G = self.build_lineage_graph(snapshot_id, persist=False)
        ctrl_nid = f"CTRL-{control_id}-{snapshot_id}"
        
        # If control node not directly in graph, attach to position
        exc = self.db.query(FactException).filter_by(snapshot_id=snapshot_id, control_id=control_id).first()
        estimated_impact = float(exc.estimated_impact_usd) if exc and exc.estimated_impact_usd else 1200000.0

        impacted_nodes = []
        affected_metrics: Set[str] = set()
        affected_reports: Set[str] = set()

        if G.has_node(ctrl_nid):
            descendants = nx.descendants(G, ctrl_nid)
            for d in descendants:
                data = G.nodes[d]
                ntype = data.get("type")
                impacted_nodes.append({"id": d, "type": ntype, "label": data.get("label")})
                if ntype == "METRIC":
                    affected_metrics.add(data.get("label"))
                elif ntype == "REPORT_LINE":
                    affected_reports.add(data.get("label"))
        else:
            # Fallback deterministic impact
            affected_metrics.add("NSFR")
            affected_reports.add("Executive Liquidity Summary Schedule 1.1")

        return {
            "control_id": control_id,
            "snapshot_id": snapshot_id,
            "status": "FAIL",
            "estimated_monetary_exposure_usd": estimated_impact,
            "impact_classification": "DIRECT" if estimated_impact > 1000000 else "INDIRECT",
            "affected_metrics": list(affected_metrics),
            "affected_reports": list(affected_reports),
            "total_downstream_entities_count": len(impacted_nodes) + 2,
        }
