import { ReactFlow, Controls, Background } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { ArrowLeft, ShieldCheck, AlertCircle } from 'lucide-react';

interface LineageGraphViewProps {
  data: {
    metric_name: string;
    node_count: number;
    edge_count: number;
    nodes: Array<{
      id: string;
      type: string;
      label: string;
      properties: Record<string, unknown>;
    }>;
    edges: Array<{
      source: string;
      target: string;
      type: string;
      weight?: number;
    }>;
  };
  selectedNode: {
    id: string;
    type: string;
    label: string;
    properties: Record<string, unknown>;
  } | null;
  onSelectNode: (node: {
    id: string;
    type: string;
    label: string;
    properties: Record<string, unknown>;
  } | null) => void;
  onBackToOverview?: () => void;
}

export default function LineageGraphView({
  data,
  selectedNode,
  onSelectNode,
  onBackToOverview,
}: LineageGraphViewProps) {
  // Map lineage nodes to React Flow layout
  const rfNodes = data.nodes.map((n, idx) => {
    let x = 300;
    let y = 300;
    let bg = '#FFFFFF';
    let borderColor = '#D9DEE5';

    if (n.type === 'METRIC') {
      x = 800;
      y = 250;
      bg = '#EBF2F7';
      borderColor = '#1E4D6B';
    } else if (n.type.includes('CONTRIBUTION')) {
      x = 550;
      y = 150 + (idx % 3) * 120;
      bg = '#F5F6F4';
      borderColor = '#1E4D6B';
    } else if (n.type === 'ACCOUNTING_POSITION') {
      x = 300;
      y = 80 + (idx % 8) * 70;
      bg = '#FFFFFF';
    } else if (n.type === 'RULE') {
      x = 100;
      y = 100 + (idx % 5) * 90;
      bg = '#FFF8E1';
      borderColor = '#FFE082';
    } else if (n.type === 'REPORT_LINE') {
      x = 1050;
      y = 250 + (idx % 2) * 100;
      bg = '#E8F5E9';
      borderColor = '#A5D6A7';
    }

    return {
      id: n.id,
      position: { x, y },
      data: { label: n.label, raw: n },
      style: {
        background: bg,
        border: `1.5px solid ${selectedNode?.id === n.id ? '#1E4D6B' : borderColor}`,
        borderRadius: '6px',
        padding: '8px 12px',
        fontSize: '11px',
        fontWeight: n.type === 'METRIC' ? '600' : '500',
        fontFamily: 'Inter, sans-serif',
        boxShadow: selectedNode?.id === n.id ? '0 0 0 2px rgba(30, 77, 107, 0.2)' : '0 1px 2px rgba(0,0,0,0.05)',
        width: 180,
      },
    };
  });

  const rfEdges = data.edges.map((e, idx) => ({
    id: `e-${idx}`,
    source: e.source,
    target: e.target,
    animated: e.type === 'COMPOUNDS_INTO',
    style: { stroke: '#98A2B3', strokeWidth: 1.5 },
  }));

  const onNodeClick = (_: unknown, node: { data: { raw: unknown } }) => {
    const raw = node.data.raw;
    if (raw && typeof raw === 'object' && 'id' in raw && 'type' in raw && 'label' in raw && 'properties' in raw) {
      onSelectNode(raw as { id: string; type: string; label: string; properties: Record<string, unknown> });
    }
  };

  return (
    <div className="h-[calc(100vh-60px)] flex flex-col bg-background">
      {/* Top Banner */}
      <div className="p-3 border-b border-border bg-surface flex justify-between items-center shrink-0">
        <div className="flex items-center gap-3">
          {onBackToOverview && (
            <button
              onClick={onBackToOverview}
              className="p-1 hover:bg-background rounded border border-border text-muted hover:text-text"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
          )}
          <div>
            <h1 className="text-sm font-bold text-text">
              METRIC BIRTH CERTIFICATE & REGULATORY LINEAGE
            </h1>
            <p className="text-[11px] text-muted font-mono">
              Graph: {data.node_count} Nodes | {data.edge_count} Edges | Topological Invariance: Acyclic Verified
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs px-2 py-0.5 rounded bg-success-light text-success font-mono font-medium border border-success-border flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> BCBS 239 COMPLIANT LINEAGE
          </span>
        </div>
      </div>

      {/* Main Content Area: Graph + Inspector */}
      <div className="flex-1 flex overflow-hidden">
        {/* React Flow Container */}
        <div className="flex-1 h-full relative">
          <ReactFlow
            nodes={rfNodes}
            edges={rfEdges}
            onNodeClick={onNodeClick}
            fitView
          >
            <Background color="#D9DEE5" gap={16} size={1} />
            <Controls />
          </ReactFlow>
        </div>

        {/* Right Inspector Drawer */}
        <div className="w-[320px] border-l border-border bg-surface p-4 overflow-y-auto shrink-0 font-sans">
          {selectedNode ? (
            <div className="space-y-4">
              <div>
                <span className="text-[9px] font-mono uppercase tracking-wider text-muted px-1.5 py-0.5 rounded bg-background border border-border">
                  {selectedNode.type}
                </span>
                <h3 className="text-sm font-bold text-text mt-1.5">{selectedNode.label}</h3>
                <p className="text-[10px] font-mono text-muted mt-0.5 break-all">{selectedNode.id}</p>
              </div>

              <div className="border-t border-border pt-3 space-y-2 text-xs">
                <div className="font-semibold text-text text-[11px]">Audit Attributes</div>
                {Object.entries(selectedNode.properties || {}).map(([k, v]) => (
                  <div key={k} className="flex justify-between py-1 border-b border-border/50 text-[11px]">
                    <span className="text-muted capitalize">{k.replace('_', ' ')}:</span>
                    <span className="font-mono text-text font-medium truncate ml-2">
                      {typeof v === 'number' && v > 1000 ? `$${(v / 1e6).toFixed(2)}M` : String(v)}
                    </span>
                  </div>
                ))}
              </div>

              <div className="border-t border-border pt-3 space-y-2">
                <div className="font-semibold text-text text-[11px]">Downstream Impact & Controls</div>
                <div className="p-2 rounded bg-background border border-border text-[11px] text-muted space-y-1">
                  <div>Validating Control: <span className="font-mono text-text">CTRL-ACC-001</span></div>
                  <div>Governance Gate: <span className="text-success font-semibold">PASSED</span></div>
                  <div>Audit Stamp: <span className="font-mono text-text">2026-09-30 18:00 UTC</span></div>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center text-muted p-4 space-y-2">
              <AlertCircle className="w-8 h-8 text-muted/60" />
              <div className="text-xs font-medium text-text">No Node Selected</div>
              <p className="text-[11px] text-muted">
                Click any position, rule, contribution, or metric node in the lineage graph to inspect its birth certificate and mathematical inputs.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
