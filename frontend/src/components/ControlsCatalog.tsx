import { useState } from 'react';
import { ShieldCheck, AlertCircle, AlertTriangle, Search, Filter } from 'lucide-react';

interface ControlsCatalogProps {
  controls: Array<{
    control_id: string;
    control_name: string;
    control_family: string;
    severity: string;
    expected_result: string;
    actual_result: string;
    status: string;
    evidence_reference?: string;
  }>;
  controlScore?: number;
  onControlClick?: (controlId: string) => void;
}

export default function ControlsCatalog({
  controls,
  controlScore = 98.0,
  onControlClick,
}: ControlsCatalogProps) {
  const [search, setSearch] = useState('');
  const [selectedFamily, setSelectedFamily] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');

  const families = ['ALL', 'ACCOUNTING', 'DATA QUALITY', 'CLASSIFICATION', 'MATURITY', 'CALCULATION', 'RECONCILIATION', 'REPORTING', 'LINEAGE', 'SCENARIO', 'AI OUTPUT'];

  const filtered = controls.filter((c) => {
    const matchesSearch = c.control_id.toLowerCase().includes(search.toLowerCase()) || c.control_name.toLowerCase().includes(search.toLowerCase());
    const matchesFamily = selectedFamily === 'ALL' || c.control_family === selectedFamily;
    const matchesStatus = selectedStatus === 'ALL' || c.status === selectedStatus;
    return matchesSearch && matchesFamily && matchesStatus;
  });

  return (
    <div className="space-y-4">
      {/* Top Banner */}
      <div className="bg-surface p-4 rounded-lg border border-border flex justify-between items-center">
        <div>
          <h1 className="text-sm font-bold text-text">AUTOMATED CONTINUOUS CONTROL CATALOG</h1>
          <p className="text-xs text-muted">
            100 automated checks across 10 families validating data quality, accounting identities, and regulatory logic.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-xs text-muted font-mono">CONTROL SCORE</div>
            <div className="text-lg font-bold font-mono text-success">{controlScore.toFixed(1)}% PASSED</div>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-surface p-3 rounded-lg border border-border flex flex-wrap gap-2 items-center justify-between text-xs">
        <div className="flex items-center gap-2 flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 text-muted" />
          <input
            type="text"
            placeholder="Search by ID or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-background border border-border rounded px-2 py-1 text-xs outline-hidden focus:border-accent"
          />
        </div>

        <div className="flex items-center gap-2 font-mono">
          <Filter className="w-3 h-3 text-muted" />
          <select
            value={selectedFamily}
            onChange={(e) => setSelectedFamily(e.target.value)}
            className="bg-background border border-border rounded px-2 py-1 text-xs"
          >
            {families.map((f) => (
              <option key={f} value={f}>
                Family: {f}
              </option>
            ))}
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-background border border-border rounded px-2 py-1 text-xs"
          >
            <option value="ALL">Status: ALL</option>
            <option value="PASS">PASS</option>
            <option value="FAIL">FAIL</option>
            <option value="WARNING">WARNING</option>
          </select>
        </div>
      </div>

      {/* Controls List Table */}
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        <table className="w-full text-left text-xs font-sans">
          <thead className="bg-background/80 border-b border-border text-[10px] font-mono text-muted uppercase">
            <tr>
              <th className="p-2.5">Control ID</th>
              <th className="p-2.5">Name & Description</th>
              <th className="p-2.5">Family</th>
              <th className="p-2.5">Severity</th>
              <th className="p-2.5">Status</th>
              <th className="p-2.5">Actual Observation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {filtered.map((c) => {
              const isPass = c.status === 'PASS';
              const isFail = c.status === 'FAIL';

              return (
                <tr
                  key={c.control_id}
                  onClick={() => onControlClick?.(c.control_id)}
                  className="hover:bg-background/60 cursor-pointer transition-colors"
                >
                  <td className="p-2.5 font-mono text-[11px] font-semibold text-accent whitespace-nowrap">
                    {c.control_id}
                  </td>
                  <td className="p-2.5 max-w-xs">
                    <div className="font-semibold text-text">{c.control_name}</div>
                    <div className="text-[10px] text-muted truncate">{c.expected_result}</div>
                  </td>
                  <td className="p-2.5 font-mono text-[10px] text-muted whitespace-nowrap">
                    {c.control_family}
                  </td>
                  <td className="p-2.5 font-mono text-[10px]">
                    <span
                      className={`px-1.5 py-0.5 rounded font-semibold ${
                        c.severity === 'CRITICAL'
                          ? 'bg-danger-light text-danger'
                          : c.severity === 'HIGH'
                          ? 'bg-warning-light text-warning'
                          : 'bg-background text-muted border border-border'
                      }`}
                    >
                      {c.severity}
                    </span>
                  </td>
                  <td className="p-2.5 font-mono text-[10px] whitespace-nowrap">
                    <span
                      className={`px-1.5 py-0.5 rounded font-semibold flex items-center gap-1 w-fit ${
                        isPass
                          ? 'bg-success-light text-success border border-success-border'
                          : isFail
                          ? 'bg-danger-light text-danger border border-danger-border'
                          : 'bg-warning-light text-warning border border-warning-border'
                      }`}
                    >
                      {isPass ? <ShieldCheck className="w-3 h-3" /> : isFail ? <AlertCircle className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                      {c.status}
                    </span>
                  </td>
                  <td className="p-2.5 text-[11px] text-muted max-w-sm truncate">
                    {c.actual_result}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
