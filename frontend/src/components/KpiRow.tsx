import { ArrowUpRight, ShieldCheck, AlertCircle } from 'lucide-react';

interface KpiRowProps {
  nsfr: number;
  lcr: number;
  asfUsd: number;
  rsfUsd: number;
  controlScore: number;
  openExceptions: number;
  onKpiClick?: (metric: string) => void;
}

export default function KpiRow({
  nsfr,
  lcr,
  asfUsd,
  rsfUsd,
  controlScore,
  openExceptions,
  onKpiClick,
}: KpiRowProps) {
  const cards = [
    {
      id: 'NSFR',
      label: 'NET STABLE FUNDING RATIO',
      value: `${nsfr.toFixed(2)}%`,
      sub: 'Regulatory Min: 100.00%',
      buffer: `${(nsfr - 100).toFixed(2)} pp Buffer`,
      status: nsfr >= 100 ? 'COMPLIANT' : 'BREACH',
      statusColor: 'text-success',
      icon: ArrowUpRight,
      highlight: true,
    },
    {
      id: 'LCR',
      label: 'LIQUIDITY COVERAGE RATIO',
      value: `${lcr.toFixed(2)}%`,
      sub: 'Regulatory Min: 100.00%',
      buffer: `${(lcr - 100).toFixed(2)} pp Buffer`,
      status: lcr >= 100 ? 'COMPLIANT' : 'BREACH',
      statusColor: 'text-success',
      icon: ArrowUpRight,
      highlight: false,
    },
    {
      id: 'ASF',
      label: 'AVAILABLE STABLE FUNDING',
      value: `$${(asfUsd / 1e6).toFixed(1)}M`,
      sub: 'Capital & Stable Liabilities',
      buffer: 'Numerator',
      status: 'WEIGHTED',
      statusColor: 'text-muted',
      icon: ShieldCheck,
      highlight: false,
    },
    {
      id: 'RSF',
      label: 'REQUIRED STABLE FUNDING',
      value: `$${(rsfUsd / 1e6).toFixed(1)}M`,
      sub: 'Assets & Committed OBS',
      buffer: 'Denominator',
      status: 'WEIGHTED',
      statusColor: 'text-muted',
      icon: ShieldCheck,
      highlight: false,
    },
    {
      id: 'CONTROLS',
      label: 'AUTOMATED CONTROLS',
      value: `${controlScore.toFixed(1)}%`,
      sub: '98 / 100 Executed Controls Passed',
      buffer: '1 Warning, 1 Break',
      status: controlScore >= 95 ? 'HEALTHY' : 'WARNING',
      statusColor: controlScore >= 95 ? 'text-success' : 'text-warning',
      icon: AlertCircle,
      highlight: false,
    },
    {
      id: 'EXCEPTIONS',
      label: 'OPEN AUDIT EXCEPTIONS',
      value: `${openExceptions}`,
      sub: 'Tracked Control Breaks',
      buffer: '1 Investigating, 1 Open',
      status: openExceptions === 0 ? 'CLEARED' : 'INVESTIGATING',
      statusColor: openExceptions === 0 ? 'text-success' : 'text-warning',
      icon: AlertCircle,
      highlight: false,
    },
  ];

  return (
    <div className="grid grid-cols-6 gap-3">
      {cards.map((card) => {
        return (
          <div
            key={card.id}
            onClick={() => onKpiClick?.(card.id)}
            className={`p-3.5 rounded-lg border bg-surface transition-all cursor-pointer hover:border-accent hover:shadow-sm ${
              card.highlight ? 'border-accent/40 ring-1 ring-accent/10' : 'border-border'
            }`}
          >
            <div className="flex justify-between items-start mb-1.5">
              <span className="text-[10px] font-mono tracking-wider text-muted truncate">
                {card.label}
              </span>
              <span className={`text-[9px] font-mono font-semibold px-1 py-0.5 rounded bg-background border border-border ${card.statusColor}`}>
                {card.status}
              </span>
            </div>
            <div className="text-xl font-bold font-mono text-text tracking-tight mb-1">
              {card.value}
            </div>
            <div className="flex justify-between items-center text-[10px] text-muted">
              <span className="truncate">{card.sub}</span>
              <span className="font-mono text-accent font-medium shrink-0 ml-1">{card.buffer}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
