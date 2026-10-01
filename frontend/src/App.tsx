import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import KpiRow from './components/KpiRow';
import MovementWaterfall from './components/MovementWaterfall';
import LineageGraphView from './components/LineageGraphView';
import ScenarioLab from './components/ScenarioLab';
import CloseWorkspace from './components/CloseWorkspace';
import ControlsCatalog from './components/ControlsCatalog';
import CopilotPanel from './components/CopilotPanel';
import { SectionKey, OverviewData } from './types';
import {
  fetchOverview,
  fetchLineage,
  fetchControls,
  fetchCloseStatus,
  advanceCloseStep,
  injectLateAdjustment,
  compileReports,
  fetchQueries,
  fetchEventReplay,
} from './services/api';
import { FileDown, CheckCircle2 } from 'lucide-react';

export default function App() {
  const [section, setSection] = useState<SectionKey>('overview');
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [controlsData, setControlsData] = useState<any[]>([]);
  const [closeStatus, setCloseStatus] = useState<any>(null);
  const [lineageData, setLineageData] = useState<any>(null);
  const [selectedLineageNode, setSelectedLineageNode] = useState<any>(null);
  const [queries, setQueries] = useState<any[]>([]);
  const [replayEvents, setReplayEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [over, ctrls, close, lin, qList, rep] = await Promise.all([
        fetchOverview(),
        fetchControls(),
        fetchCloseStatus(),
        fetchLineage('NSFR'),
        fetchQueries(),
        fetchEventReplay(),
      ]);
      setOverview(over);
      setControlsData(ctrls.controls || []);
      setCloseStatus(close);
      setLineageData(lin);
      setQueries(qList);
      setReplayEvents(rep);
    } catch (err) {
      console.error('Initialization error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleAdvanceStep = async (stepNum: number) => {
    try {
      const updated = await advanceCloseStep(stepNum);
      setCloseStatus(updated);
      setActionNotice(`Stage ${stepNum} completed successfully.`);
      setTimeout(() => setActionNotice(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLateAdjustment = async () => {
    try {
      await injectLateAdjustment({
        account_id: 'ACC-CORP_NON_OPERATIONAL',
        adjustment_amount_usd: 38000000.0,
      });
      await loadAll();
      setActionNotice('$38M Late Adjustment injected. Stages 5-10 BLOCKED.');
      setTimeout(() => setActionNotice(null), 4000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerateReport = async () => {
    try {
      const res = await compileReports();
      setActionNotice(`Reporting pack generated: ${res.pdf_path}`);
      setTimeout(() => setActionNotice(null), 4000);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading || !overview) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center font-mono text-xs text-muted space-y-2">
        <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin"></div>
        <div>Loading Liquidity Twin Regulatory Engine...</div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <Sidebar
        currentSection={section}
        onSelectSection={setSection}
        controlScore={overview.kpis.control_score}
        openExceptions={overview.kpis.open_exceptions_count}
      />

      {/* Main Content Workspace */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Global Notification Banner */}
        {actionNotice && (
          <div className="bg-accent text-white px-4 py-2 text-xs font-mono flex items-center justify-between shadow-xs">
            <span>{actionNotice}</span>
            <button onClick={() => setActionNotice(null)} className="underline text-[10px]">
              Dismiss
            </button>
          </div>
        )}

        {/* Viewport Render Area */}
        <div className="flex-1 p-5 overflow-y-auto">
          {section === 'overview' && (
            <div className="space-y-4">
              {/* Header Bar */}
              <div className="bg-surface p-4 rounded-lg border border-border flex justify-between items-center">
                <div>
                  <h1 className="text-base font-bold text-text">
                    REGULATORY LIQUIDITY COMMAND CENTER
                  </h1>
                  <p className="text-xs text-muted font-mono">
                    Snapshot: {overview.snapshot.snapshot_id} | Period: {overview.snapshot.period} | As of: {overview.snapshot.business_date}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSection('lineage')}
                    className="px-3 py-1.5 text-xs font-mono rounded border border-border bg-background hover:bg-surface text-accent font-semibold"
                  >
                    View Metric Birth Certificate
                  </button>
                  <button
                    onClick={handleGenerateReport}
                    className="px-3 py-1.5 text-xs font-semibold rounded bg-accent text-white hover:bg-accent-hover flex items-center gap-1.5 shadow-sm"
                  >
                    <FileDown className="w-3.5 h-3.5" /> Generate Reporting Pack
                  </button>
                </div>
              </div>

              {/* KPI Cards Row */}
              <KpiRow
                nsfr={overview.kpis.nsfr}
                lcr={overview.kpis.lcr}
                asfUsd={overview.kpis.asf_usd}
                rsfUsd={overview.kpis.rsf_usd}
                controlScore={overview.kpis.control_score}
                openExceptions={overview.kpis.open_exceptions_count}
                onKpiClick={(m) => {
                  if (m === 'NSFR' || m === 'LCR') setSection('lineage');
                  else if (m === 'CONTROLS' || m === 'EXCEPTIONS') setSection('controls');
                }}
              />

              {/* Movement Waterfall */}
              <MovementWaterfall
                previousNsfr={overview.movement.previous_nsfr_percentage}
                currentNsfr={overview.movement.current_nsfr_percentage}
                totalMovement={overview.movement.total_movement_pp}
                drivers={overview.movement.drivers}
                onDriverClick={() => setSection('movement')}
              />

              {/* Five Core Operational Inquiries */}
              <div className="grid grid-cols-5 gap-3 pt-2">
                <div
                  onClick={() => setSection('movement')}
                  className="p-3 bg-surface rounded-lg border border-border cursor-pointer hover:border-accent"
                >
                  <div className="text-[10px] font-mono text-muted uppercase">1. What Changed?</div>
                  <div className="text-xs font-bold text-text mt-1">Movement Decomposition</div>
                  <p className="text-[11px] text-muted mt-1">Shapley driver attribution for NSFR shift.</p>
                </div>
                <div
                  onClick={() => setSection('lineage')}
                  className="p-3 bg-surface rounded-lg border border-border cursor-pointer hover:border-accent"
                >
                  <div className="text-[10px] font-mono text-muted uppercase">2. Can I Trust It?</div>
                  <div className="text-xs font-bold text-text mt-1">Lineage &amp; Birth Certificate</div>
                  <p className="text-[11px] text-muted mt-1">End-to-end provenance down to source records.</p>
                </div>
                <div
                  onClick={() => setSection('scenarios')}
                  className="p-3 bg-surface rounded-lg border border-border cursor-pointer hover:border-accent"
                >
                  <div className="text-[10px] font-mono text-muted uppercase">3. What If?</div>
                  <div className="text-xs font-bold text-text mt-1">Counterfactual Scenario Lab</div>
                  <p className="text-[11px] text-muted mt-1">Stress corporate deposit outflows &amp; loan growth.</p>
                </div>
                <div
                  onClick={() => setSection('close')}
                  className="p-3 bg-surface rounded-lg border border-border cursor-pointer hover:border-accent"
                >
                  <div className="text-[10px] font-mono text-muted uppercase">4. Close Status</div>
                  <div className="text-xs font-bold text-text mt-1">Shadow Close Workspace</div>
                  <p className="text-[11px] text-muted mt-1">10-stage sequential accounting sign-off.</p>
                </div>
                <div
                  onClick={() => setSection('reporting')}
                  className="p-3 bg-surface rounded-lg border border-border cursor-pointer hover:border-accent"
                >
                  <div className="text-[10px] font-mono text-muted uppercase">5. What Do I Send?</div>
                  <div className="text-xs font-bold text-text mt-1">Reporting Pack Compiler</div>
                  <p className="text-[11px] text-muted mt-1">Publication-grade PDF and XLSX compilation.</p>
                </div>
              </div>
            </div>
          )}

          {section === 'movement' && (
            <div className="space-y-4">
              <MovementWaterfall
                previousNsfr={overview.movement.previous_nsfr_percentage}
                currentNsfr={overview.movement.current_nsfr_percentage}
                totalMovement={overview.movement.total_movement_pp}
                drivers={overview.movement.drivers}
              />
              <div className="bg-surface p-4 rounded-lg border border-border">
                <h3 className="text-xs font-bold font-mono uppercase text-text mb-3">
                  Driver Decomposition Table (Exact Shapley Attribution)
                </h3>
                <table className="w-full text-left text-xs font-sans">
                  <thead className="bg-background text-[10px] font-mono text-muted uppercase border-b border-border">
                    <tr>
                      <th className="p-2.5">Driver Category</th>
                      <th className="p-2.5">Balance Movement</th>
                      <th className="p-2.5">Delta ASF</th>
                      <th className="p-2.5">Delta RSF</th>
                      <th className="p-2.5">Contribution (pp)</th>
                      <th className="p-2.5">Direction</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {overview.movement.drivers.map((d, i) => (
                      <tr key={i} className="hover:bg-background/50">
                        <td className="p-2.5 font-semibold text-text">{d.driver_name}</td>
                        <td className="p-2.5 font-mono">${(d.balance_movement_usd / 1e6).toFixed(1)}M</td>
                        <td className="p-2.5 font-mono text-muted">—</td>
                        <td className="p-2.5 font-mono text-muted">—</td>
                        <td
                          className={`p-2.5 font-mono font-bold ${
                            d.contribution_pp >= 0 ? 'text-success' : 'text-danger'
                          }`}
                        >
                          {d.contribution_pp >= 0 ? '+' : ''}
                          {d.contribution_pp.toFixed(4)} pp
                        </td>
                        <td className="p-2.5 font-mono text-[10px] uppercase">{d.impact_direction}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {section === 'lineage' && lineageData && (
            <LineageGraphView
              data={lineageData}
              selectedNode={selectedLineageNode}
              onSelectNode={setSelectedLineageNode}
              onBackToOverview={() => setSection('overview')}
            />
          )}

          {section === 'scenarios' && (
            <ScenarioLab
              baseSnapshotId={overview.snapshot.snapshot_id}
              baseNsfr={overview.kpis.nsfr}
              baseLcr={overview.kpis.lcr}
            />
          )}

          {section === 'close' && closeStatus && (
            <CloseWorkspace
              period={overview.snapshot.period}
              closeData={closeStatus}
              onAdvanceStep={handleAdvanceStep}
              onInjectLateAdjustment={handleLateAdjustment}
            />
          )}

          {section === 'controls' && (
            <ControlsCatalog
              controls={controlsData}
              controlScore={overview.kpis.control_score}
            />
          )}

          {section === 'reporting' && (
            <div className="space-y-4">
              <div className="bg-surface p-4 rounded-lg border border-border flex justify-between items-center">
                <div>
                  <h1 className="text-sm font-bold text-text">REGULATORY REPORTING PACK COMPILER</h1>
                  <p className="text-xs text-muted">
                    Compile formal PDF &amp; XLSX reporting packs backed by frozen snapshot lineage.
                  </p>
                </div>
                <button
                  onClick={handleGenerateReport}
                  className="px-3 py-1.5 text-xs font-semibold rounded bg-accent text-white hover:bg-accent-hover flex items-center gap-1.5 shadow-sm"
                >
                  <FileDown className="w-3.5 h-3.5" /> Compile Latest Pack
                </button>
              </div>

              <div className="bg-surface rounded-lg border border-border p-4 space-y-3">
                <div className="flex justify-between items-center border-b border-border pb-2 text-xs font-mono">
                  <span>REPORT PACK 2026-Q3</span>
                  <span className="text-success font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> READY FOR PUBLICATION
                  </span>
                </div>
                <p className="text-xs text-muted">
                  Includes Executive Liquidity Summary, NSFR Reporting Table, LCR Reporting Table, Balance-Sheet Reconciliation, Variance Commentary, Control Exceptions, and Reviewer Sign-Off.
                </p>
                <div className="flex gap-2">
                  <a
                    href="/static/reports/Liquidity_Reporting_Pack_2026-Q3_20261001_183030.pdf"
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1 text-xs rounded border border-border bg-background hover:bg-surface font-mono text-accent"
                  >
                    Download PDF Pack
                  </a>
                  <a
                    href="/static/reports/Liquidity_Reporting_Pack_2026-Q3_20261001_183030.xlsx"
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1 text-xs rounded border border-border bg-background hover:bg-surface font-mono text-accent"
                  >
                    Download XLSX Pack
                  </a>
                </div>
              </div>
            </div>
          )}

          {section === 'queries' && (
            <div className="space-y-4">
              <div className="bg-surface p-4 rounded-lg border border-border">
                <h1 className="text-sm font-bold text-text">STAKEHOLDER QUERY WORKBENCH</h1>
                <p className="text-xs text-muted">
                  Structured investigation cases, metric reproduction, and audit resolutions.
                </p>
              </div>
              <div className="grid grid-cols-12 gap-4">
                <div className="col-span-5 bg-surface rounded-lg border border-border divide-y divide-border">
                  {queries.map((q) => (
                    <div key={q.query_id} className="p-3 hover:bg-background/50 cursor-pointer">
                      <div className="flex justify-between items-center text-[10px] font-mono">
                        <span className="font-bold text-accent">{q.query_id}</span>
                        <span className="text-success font-semibold">{q.investigation_status}</span>
                      </div>
                      <div className="text-xs font-semibold text-text mt-1">{q.question}</div>
                      <div className="text-[10px] text-muted mt-1">Requester: {q.requester}</div>
                    </div>
                  ))}
                </div>
                <div className="col-span-7 bg-surface rounded-lg border border-border p-4 space-y-3">
                  {queries.length > 0 && (
                    <>
                      <div className="border-b border-border pb-2">
                        <div className="text-[10px] font-mono text-accent font-bold">{queries[0].query_id}</div>
                        <h2 className="text-xs font-bold text-text mt-1">{queries[0].question}</h2>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-xs font-mono p-2 rounded bg-background">
                        <div>Reported: <b>{queries[0].reported_value}%</b></div>
                        <div>Recalculated: <b>{queries[0].recalculated_value}%</b></div>
                        <div>Variance: <b className="text-danger">+{queries[0].variance} pp</b></div>
                      </div>
                      <div className="text-xs space-y-1">
                        <div className="font-semibold text-text">Root Cause:</div>
                        <p className="text-muted text-[11px]">{queries[0].root_cause}</p>
                      </div>
                      <div className="text-xs space-y-1">
                        <div className="font-semibold text-text">Resolution &amp; Evidence:</div>
                        <p className="text-muted text-[11px]">{queries[0].resolution}</p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {section === 'copilot' && (
            <CopilotPanel snapshotId={overview.snapshot.snapshot_id} />
          )}

          {section === 'replay' && (
            <div className="space-y-4">
              <div className="bg-surface p-4 rounded-lg border border-border">
                <h1 className="text-sm font-bold text-text">TRANSACTION EVENT TIMELINE REPLAY</h1>
                <p className="text-xs text-muted">
                  Stepped chronological replay of balance-sheet movements and their cumulative NSFR impact.
                </p>
              </div>
              <div className="bg-surface rounded-lg border border-border overflow-hidden">
                <table className="w-full text-left text-xs font-sans">
                  <thead className="bg-background text-[10px] font-mono text-muted uppercase border-b border-border">
                    <tr>
                      <th className="p-2.5">Step</th>
                      <th className="p-2.5">Timestamp</th>
                      <th className="p-2.5">Event Type</th>
                      <th className="p-2.5">Account / Product</th>
                      <th className="p-2.5">Amount</th>
                      <th className="p-2.5">NSFR Impact</th>
                      <th className="p-2.5">Running NSFR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border font-mono text-[11px]">
                    {replayEvents.slice(0, 20).map((ev) => (
                      <tr key={ev.event_id} className="hover:bg-background/50">
                        <td className="p-2.5 font-bold text-accent">#{ev.step_index}</td>
                        <td className="p-2.5 text-muted">{ev.timestamp.replace('T', ' ').slice(0, 16)}</td>
                        <td className="p-2.5 font-semibold text-text">{ev.event_type}</td>
                        <td className="p-2.5 text-muted">{ev.product_name}</td>
                        <td className="p-2.5 font-semibold">{ev.amount_formatted}</td>
                        <td className={`p-2.5 font-bold ${ev.nsfr_impact_pp >= 0 ? 'text-success' : 'text-danger'}`}>
                          {ev.nsfr_impact_pp >= 0 ? '+' : ''}{ev.nsfr_impact_pp.toFixed(2)} pp
                        </td>
                        <td className="p-2.5 font-bold text-accent">{ev.running_nsfr_percentage.toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {section === 'benchmark' && (
            <div className="space-y-4">
              <div className="bg-surface p-4 rounded-lg border border-border">
                <h1 className="text-sm font-bold text-text">PUBLIC DISCLOSURE BENCHMARK (BCBS PILLAR 3)</h1>
                <p className="text-xs text-muted">
                  Alignment of synthetic reporting lines with Basel DIS30 (LCR) and DIS40 (NSFR) public disclosure frameworks.
                </p>
              </div>
              <div className="bg-surface rounded-lg border border-border p-4 text-xs space-y-3">
                <table className="w-full text-left font-sans">
                  <thead className="bg-background text-[10px] font-mono text-muted uppercase border-b border-border">
                    <tr>
                      <th className="p-2.5">Pillar 3 Concept</th>
                      <th className="p-2.5">Public Standard Reference</th>
                      <th className="p-2.5">Synthetic Implementation</th>
                      <th className="p-2.5">Methodology Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border text-[11px]">
                    <tr>
                      <td className="p-2.5 font-semibold text-text">NSFR Table LIQ2</td>
                      <td className="p-2.5 font-mono text-muted">BCBS DIS40</td>
                      <td className="p-2.5">4 residual maturity buckets applied to liabilities &amp; assets</td>
                      <td className="p-2.5 font-mono text-success font-semibold">100% ALIGNED</td>
                    </tr>
                    <tr>
                      <td className="p-2.5 font-semibold text-text">LCR Table LIQ1</td>
                      <td className="p-2.5 font-mono text-muted">BCBS DIS30</td>
                      <td className="p-2.5">HQLA Level 1 / 2A / 2B with haircuts and 75% inflow cap</td>
                      <td className="p-2.5 font-mono text-success font-semibold">100% ALIGNED</td>
                    </tr>
                    <tr>
                      <td className="p-2.5 font-semibold text-text">Data Privacy</td>
                      <td className="p-2.5 font-mono text-muted">Standard Rule 3 / 4</td>
                      <td className="p-2.5">Fully synthetic data model; zero confidential institution data</td>
                      <td className="p-2.5 font-mono text-success font-semibold">COMPLIANT</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
