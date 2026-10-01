import { useState } from 'react';
import { Play, RotateCcw, AlertTriangle, ArrowRight } from 'lucide-react';
import { runScenario } from '../services/api';

interface ScenarioLabProps {
  baseSnapshotId?: string;
  baseNsfr?: number;
  baseLcr?: number;
}

interface ScenarioResultState {
  scenario_name: string;
  metrics: {
    NSFR: {
      base: number;
      scenario: number;
      delta_pp: number;
      base_asf_usd: number;
      stressed_asf_usd: number;
      base_rsf_usd: number;
      stressed_rsf_usd: number;
    };
    LCR: {
      base: number;
      scenario: number;
      delta_pp: number;
      base_hqla_usd: number;
      stressed_hqla_usd: number;
    };
  };
  primary_drivers: string[];
  driver_explanation: string;
}

export default function ScenarioLab({
  baseSnapshotId = 'SNAP-2026-Q3-BASE',
  baseNsfr = 117.64,
  baseLcr = 132.49,
}: ScenarioLabProps) {
  const [corpDepositPct, setCorpDepositPct] = useState<number>(-8.0);
  const [retDepositPct, setRetDepositPct] = useState<number>(0.0);
  const [loanGrowthPct, setLoanGrowthPct] = useState<number>(0.0);
  const [wholesaleMaturityPct, setWholesaleMaturityPct] = useState<number>(0.0);
  const [newFundingM, setNewFundingM] = useState<number>(0.0);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ScenarioResultState | null>(null);

  const handleExecute = async () => {
    setLoading(true);
    try {
      const data = await runScenario({
        base_snapshot_id: baseSnapshotId,
        scenario_name: `Stress Test: Corp ${corpDepositPct}%, Loans ${loanGrowthPct}%`,
        corporate_deposit_pct: corpDepositPct,
        retail_deposit_pct: retDepositPct,
        loan_growth_pct: loanGrowthPct,
        wholesale_maturity_pct: wholesaleMaturityPct,
        new_term_funding_usd: newFundingM * 1e6,
      });
      setResult(data as ScenarioResultState);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCorpDepositPct(0.0);
    setRetDepositPct(0.0);
    setLoanGrowthPct(0.0);
    setWholesaleMaturityPct(0.0);
    setNewFundingM(0.0);
    setResult(null);
  };

  const handlePreset8PercentCorp = () => {
    setCorpDepositPct(-8.0);
    setRetDepositPct(0.0);
    setLoanGrowthPct(0.0);
    setWholesaleMaturityPct(0.0);
    setNewFundingM(0.0);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-surface p-4 rounded-lg border border-border flex justify-between items-center">
        <div>
          <h1 className="text-sm font-bold text-text">COUNTERFACTUAL LIQUIDITY LAB</h1>
          <p className="text-xs text-muted">
            Simulate balance-sheet stress shocks without mutating frozen baseline snapshots.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handlePreset8PercentCorp}
            className="px-2.5 py-1 text-xs font-mono rounded border border-border bg-background hover:bg-surface text-accent"
          >
            Load Target: -8% Corp Outflow
          </button>
          <button
            onClick={handleReset}
            className="px-2.5 py-1 text-xs font-mono rounded border border-border hover:bg-background text-muted flex items-center gap-1"
          >
            <RotateCcw className="w-3 h-3" /> Reset
          </button>
          <button
            onClick={handleExecute}
            disabled={loading}
            className="px-3 py-1 text-xs font-semibold rounded bg-accent text-white hover:bg-accent-hover flex items-center gap-1.5 shadow-sm"
          >
            <Play className="w-3.5 h-3.5" /> {loading ? 'Calculating...' : 'Run Scenario'}
          </button>
        </div>
      </div>

      {/* Main Grid: Inputs + Output Comparison */}
      <div className="grid grid-cols-12 gap-4">
        {/* Sliders Input Panel */}
        <div className="col-span-5 bg-surface p-4 rounded-lg border border-border space-y-4">
          <h2 className="text-xs font-bold text-text uppercase tracking-wider font-mono">
            Balance-Sheet Stress Parameters
          </h2>

          <div className="space-y-3 text-xs">
            {/* Corporate Deposits */}
            <div>
              <div className="flex justify-between font-mono mb-1">
                <span>Corporate Deposits Shock</span>
                <span className={corpDepositPct < 0 ? 'text-danger font-bold' : 'text-text'}>
                  {corpDepositPct > 0 ? '+' : ''}
                  {corpDepositPct.toFixed(1)}%
                </span>
              </div>
              <input
                type="range"
                min="-30"
                max="30"
                step="0.5"
                value={corpDepositPct}
                onChange={(e) => setCorpDepositPct(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-border rounded-lg appearance-none cursor-pointer accent-accent"
              />
            </div>

            {/* Retail Deposits */}
            <div>
              <div className="flex justify-between font-mono mb-1">
                <span>Retail Deposits Shock</span>
                <span className={retDepositPct < 0 ? 'text-danger font-bold' : 'text-text'}>
                  {retDepositPct > 0 ? '+' : ''}
                  {retDepositPct.toFixed(1)}%
                </span>
              </div>
              <input
                type="range"
                min="-20"
                max="20"
                step="0.5"
                value={retDepositPct}
                onChange={(e) => setRetDepositPct(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-border rounded-lg appearance-none cursor-pointer accent-accent"
              />
            </div>

            {/* Loan Growth */}
            <div>
              <div className="flex justify-between font-mono mb-1">
                <span>Loan Expansion / Amortization</span>
                <span className={loanGrowthPct > 0 ? 'text-accent font-bold' : 'text-text'}>
                  {loanGrowthPct > 0 ? '+' : ''}
                  {loanGrowthPct.toFixed(1)}%
                </span>
              </div>
              <input
                type="range"
                min="-20"
                max="30"
                step="0.5"
                value={loanGrowthPct}
                onChange={(e) => setLoanGrowthPct(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-border rounded-lg appearance-none cursor-pointer accent-accent"
              />
            </div>

            {/* Wholesale Funding Rollover Refusal */}
            <div>
              <div className="flex justify-between font-mono mb-1">
                <span>Wholesale Funding Maturity</span>
                <span className={wholesaleMaturityPct < 0 ? 'text-danger font-bold' : 'text-text'}>
                  {wholesaleMaturityPct.toFixed(1)}%
                </span>
              </div>
              <input
                type="range"
                min="-50"
                max="0"
                step="1.0"
                value={wholesaleMaturityPct}
                onChange={(e) => setWholesaleMaturityPct(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-border rounded-lg appearance-none cursor-pointer accent-accent"
              />
            </div>

            {/* New Term Debt Injection */}
            <div>
              <div className="flex justify-between font-mono mb-1">
                <span>New Long-Term Funding Injection</span>
                <span className="text-success font-bold">+${newFundingM.toFixed(1)}M</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5.0"
                value={newFundingM}
                onChange={(e) => setNewFundingM(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-border rounded-lg appearance-none cursor-pointer accent-accent"
              />
            </div>
          </div>
        </div>

        {/* Side-by-Side Comparison Panel */}
        <div className="col-span-7 bg-surface p-4 rounded-lg border border-border flex flex-col justify-between">
          <div>
            <h2 className="text-xs font-bold text-text uppercase tracking-wider font-mono mb-3">
              Comparative Impact Analysis (Base vs Stressed)
            </h2>

            <div className="grid grid-cols-2 gap-3 mb-4">
              {/* NSFR Comparison */}
              <div className="p-3 rounded-lg border border-border bg-background/50">
                <div className="text-[10px] font-mono text-muted mb-1">NET STABLE FUNDING RATIO</div>
                <div className="flex items-baseline justify-between">
                  <div>
                    <span className="text-xs text-muted mr-1">Base:</span>
                    <span className="font-mono text-sm font-semibold">{baseNsfr.toFixed(2)}%</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-muted" />
                  <div>
                    <span className="text-xs text-muted mr-1">Scenario:</span>
                    <span className="font-mono text-base font-bold text-accent">
                      {result ? `${result.metrics.NSFR.scenario.toFixed(2)}%` : '—'}
                    </span>
                  </div>
                </div>
                <div className="mt-2 pt-2 border-t border-border flex justify-between text-xs">
                  <span>Delta:</span>
                  <span
                    className={`font-mono font-bold ${
                      result && result.metrics.NSFR.delta_pp < 0 ? 'text-danger' : 'text-success'
                    }`}
                  >
                    {result ? `${result.metrics.NSFR.delta_pp > 0 ? '+' : ''}${result.metrics.NSFR.delta_pp.toFixed(2)} pp` : '—'}
                  </span>
                </div>
              </div>

              {/* LCR Comparison */}
              <div className="p-3 rounded-lg border border-border bg-background/50">
                <div className="text-[10px] font-mono text-muted mb-1">LIQUIDITY COVERAGE RATIO</div>
                <div className="flex items-baseline justify-between">
                  <div>
                    <span className="text-xs text-muted mr-1">Base:</span>
                    <span className="font-mono text-sm font-semibold">{baseLcr.toFixed(2)}%</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-muted" />
                  <div>
                    <span className="text-xs text-muted mr-1">Scenario:</span>
                    <span className="font-mono text-base font-bold text-accent">
                      {result ? `${result.metrics.LCR.scenario.toFixed(2)}%` : '—'}
                    </span>
                  </div>
                </div>
                <div className="mt-2 pt-2 border-t border-border flex justify-between text-xs">
                  <span>Delta:</span>
                  <span
                    className={`font-mono font-bold ${
                      result && result.metrics.LCR.delta_pp < 0 ? 'text-danger' : 'text-success'
                    }`}
                  >
                    {result ? `${result.metrics.LCR.delta_pp > 0 ? '+' : ''}${result.metrics.LCR.delta_pp.toFixed(2)} pp` : '—'}
                  </span>
                </div>
              </div>
            </div>

            {/* Driver Attribution Explanation */}
            {result ? (
              <div className="p-3 rounded bg-accent-light border border-accent/20 text-xs text-accent space-y-1">
                <div className="font-semibold flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" /> Analytical Attribution
                </div>
                <p>{result.driver_explanation}</p>
              </div>
            ) : (
              <div className="p-4 rounded border border-dashed border-border text-center text-xs text-muted">
                Adjust the stress sliders and click &quot;Run Scenario&quot; to compute exact counterfactual liquidity metrics.
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-border flex justify-between text-[11px] text-muted font-mono">
            <span>ISOLATION: Strict In-Memory Copy</span>
            <span>BASE SNAPSHOT: Sealed (Zero Mutation)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
