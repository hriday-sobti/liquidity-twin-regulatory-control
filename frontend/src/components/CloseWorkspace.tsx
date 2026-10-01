import { CheckCircle2, Clock, AlertTriangle, Play, RefreshCw } from 'lucide-react';

interface CloseWorkspaceProps {
  period?: string;
  closeData?: {
    period: string;
    status: string;
    steps: Array<{
      step_number: number;
      step_name: string;
      status: string;
      owner: string;
      evidence?: string;
      error_message?: string;
    }>;
  };
  onAdvanceStep?: (stepNumber: number) => void;
  onInjectLateAdjustment?: () => void;
}

export default function CloseWorkspace({
  period = '2026-Q3',
  closeData,
  onAdvanceStep,
  onInjectLateAdjustment,
}: CloseWorkspaceProps) {
  const steps = closeData?.steps || [];

  return (
    <div className="space-y-4">
      {/* Top Banner */}
      <div className="bg-surface p-4 rounded-lg border border-border flex justify-between items-center">
        <div>
          <h1 className="text-sm font-bold text-text">SHADOW CLOSE ORCHESTRATION & CLOSE CYCLE</h1>
          <p className="text-xs text-muted">
            10-Stage Sequential Governance: Freeze, Reconcile, Classify, Calculate, Control, and Sign-off.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={onInjectLateAdjustment}
            className="px-2.5 py-1 text-xs font-mono rounded border border-warning/40 bg-warning-light text-warning hover:bg-warning/20 flex items-center gap-1.5"
          >
            <AlertTriangle className="w-3.5 h-3.5" /> Inject $38M Late Adjustment
          </button>
        </div>
      </div>

      {/* Stepper Table */}
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        <div className="p-3 border-b border-border bg-background/50 flex justify-between items-center text-xs font-mono">
          <span className="font-semibold text-text">CYCLE PERIOD: {period}</span>
          <span className="text-muted">CYCLE STATUS: <span className="text-accent font-bold">{closeData?.status || 'IN_PROGRESS'}</span></span>
        </div>

        <div className="divide-y divide-border">
          {steps.map((step) => {
            const isCompleted = step.status === 'COMPLETED';
            const isInProgress = step.status === 'IN_PROGRESS';
            const isBlocked = step.status === 'BLOCKED';

            return (
              <div
                key={step.step_number}
                className={`p-3 flex items-center justify-between transition-colors ${
                  isBlocked ? 'bg-danger-light/30' : isInProgress ? 'bg-accent-light/30' : ''
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center font-mono text-xs font-bold shrink-0">
                    {isCompleted ? (
                      <CheckCircle2 className="w-5 h-5 text-success" />
                    ) : isBlocked ? (
                      <AlertTriangle className="w-5 h-5 text-danger" />
                    ) : isInProgress ? (
                      <Clock className="w-5 h-5 text-accent animate-pulse" />
                    ) : (
                      <span className="w-5 h-5 rounded-full border border-border flex items-center justify-center text-muted text-[10px]">
                        {step.step_number}
                      </span>
                    )}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-text">
                        Stage {step.step_number}: {step.step_name}
                      </span>
                      <span
                        className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-semibold ${
                          isCompleted
                            ? 'bg-success-light text-success border border-success-border'
                            : isBlocked
                            ? 'bg-danger-light text-danger border border-danger-border'
                            : isInProgress
                            ? 'bg-accent-light text-accent border border-accent/20'
                            : 'bg-background text-muted border border-border'
                        }`}
                      >
                        {step.status}
                      </span>
                    </div>
                    <p className="text-[11px] text-muted mt-0.5">
                      {isBlocked
                        ? step.error_message
                        : step.evidence || `Assigned to ${step.owner}`}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 font-mono text-xs">
                  <span className="text-muted text-[10px] hidden sm:inline">{step.owner}</span>
                  {isInProgress && onAdvanceStep && (
                    <button
                      onClick={() => onAdvanceStep(step.step_number)}
                      className="px-2.5 py-1 rounded bg-accent text-white text-[11px] font-semibold hover:bg-accent-hover flex items-center gap-1 shadow-xs"
                    >
                      <Play className="w-3 h-3" /> Complete Stage
                    </button>
                  )}
                  {isBlocked && (
                    <button
                      onClick={() => onAdvanceStep?.(step.step_number)}
                      className="px-2 py-1 rounded border border-danger text-danger text-[10px] font-semibold hover:bg-danger-light flex items-center gap-1"
                    >
                      <RefreshCw className="w-3 h-3" /> Re-execute
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
