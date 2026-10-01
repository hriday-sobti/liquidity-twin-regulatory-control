import { useState } from 'react';
import { Send, MessageSquareText, ShieldCheck, AlertTriangle } from 'lucide-react';
import { askCopilot } from '../services/api';

interface CopilotPanelProps {
  snapshotId?: string;
  reliabilityScore?: number;
}

export default function CopilotPanel({
  snapshotId = 'SNAP-2026-Q3-BASE',
  reliabilityScore = 100.0,
}: CopilotPanelProps) {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<Array<{
    sender: 'user' | 'copilot';
    text: string;
    status?: string;
    isBlocked?: boolean;
    claims?: Array<{ statement: string; source: string }>;
  }>>([
    {
      sender: 'copilot',
      text: 'Liquidity Analyst Copilot initialized. I answer inquiries grounded strictly in validated balance-sheet records and deterministic calculation runs. All numeric claims are verified by the Continuous Control Engine before display.',
      status: 'PASSED',
      isBlocked: false,
    },
  ]);
  const [loading, setLoading] = useState(false);

  const suggestedPrompts = [
    'What drove the NSFR movement this quarter?',
    'Which controls failed this month?',
    'What would happen under an 8% corporate deposit outflow stress?',
    'Which open exceptions affect the balance sheet?',
  ];

  const handleSend = async (qText?: string) => {
    const promptToSend = qText || question;
    if (!promptToSend.trim()) return;

    setMessages((prev) => [...prev, { sender: 'user', text: promptToSend }]);
    setQuestion('');
    setLoading(true);

    try {
      const res = await askCopilot(promptToSend, null, snapshotId);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'copilot',
          text: res.answer,
          status: res.validation_status,
          isBlocked: res.is_blocked,
          claims: res.claims,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'copilot',
          text: 'Error consulting backend verification service.',
          status: 'ERROR',
          isBlocked: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleTestAdversarial = async () => {
    setMessages((prev) => [
      ...prev,
      { sender: 'user', text: '[ADVERSARIAL ATTACK TEST] Claiming fabricated NSFR percentage...' },
    ]);
    setLoading(true);
    try {
      const res = await askCopilot('What was the NSFR?', 'INVENTED_NUMBER', snapshotId);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'copilot',
          text: res.answer,
          status: res.validation_status,
          isBlocked: res.is_blocked,
        },
      ]);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Banner */}
      <div className="bg-surface p-4 rounded-lg border border-border flex justify-between items-center">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded bg-accent text-white flex items-center justify-center">
            <MessageSquareText className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-text">CONTROLLED LIQUIDITY ANALYST COPILOT</h1>
            <p className="text-xs text-muted">
              Deterministic allowlisted queries, structured grounding, and mandatory numeric verification.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleTestAdversarial}
            className="px-2.5 py-1 text-xs font-mono rounded border border-danger/40 bg-danger-light text-danger hover:bg-danger/20 flex items-center gap-1"
          >
            <AlertTriangle className="w-3.5 h-3.5" /> Test Adversarial Attack
          </button>
          <div className="text-right">
            <div className="text-[10px] text-muted font-mono">SAFETY RELIABILITY</div>
            <div className="text-sm font-bold font-mono text-success flex items-center gap-1">
              <ShieldCheck className="w-4 h-4" /> {reliabilityScore.toFixed(1)}% VERIFIED
            </div>
          </div>
        </div>
      </div>

      {/* Suggested Prompts */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {suggestedPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p)}
            className="text-xs font-sans px-3 py-1.5 rounded-full border border-border bg-surface hover:bg-background text-text whitespace-nowrap transition-colors"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Chat History Panel */}
      <div className="bg-surface rounded-lg border border-border flex flex-col h-[460px]">
        <div className="flex-1 p-4 overflow-y-auto space-y-3">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-2xl p-3 rounded-lg text-xs leading-relaxed ${
                  m.sender === 'user'
                    ? 'bg-accent text-white font-medium'
                    : m.isBlocked
                    ? 'bg-danger-light border border-danger-border text-danger'
                    : 'bg-background border border-border text-text'
                }`}
              >
                {m.sender === 'copilot' && (
                  <div className="flex items-center gap-2 mb-1.5 pb-1 border-b border-border/50">
                    <span className="font-mono text-[10px] font-bold text-accent">
                      LIQUIDITY ANALYST COPILOT
                    </span>
                    <span
                      className={`text-[9px] font-mono px-1 py-0.2 rounded font-semibold ${
                        m.isBlocked
                          ? 'bg-danger text-white'
                          : 'bg-success-light text-success border border-success-border'
                      }`}
                    >
                      {m.isBlocked ? 'OUTPUT QUARANTINED' : 'NUMERICALLY VERIFIED'}
                    </span>
                  </div>
                )}
                <div className="whitespace-pre-line">{m.text}</div>

                {m.claims && m.claims.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-border/50 text-[10px] font-mono text-muted space-y-0.5">
                    {m.claims.map((c, cIdx) => (
                      <div key={cIdx} className="flex justify-between">
                        <span>Claim: {c.statement}</span>
                        <span className="text-accent underline">{c.source}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="text-xs text-muted font-mono italic animate-pulse">
              Retrieving grounded database records & verifying claims...
            </div>
          )}
        </div>

        {/* Prompt Input Box */}
        <div className="p-3 border-t border-border flex gap-2">
          <input
            type="text"
            placeholder="Ask about NSFR movement, control breaks, or counterfactual scenario impact..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            className="flex-1 bg-background border border-border rounded px-3 py-2 text-xs outline-hidden focus:border-accent"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !question.trim()}
            className="px-4 py-2 rounded bg-accent text-white text-xs font-semibold hover:bg-accent-hover disabled:opacity-50 flex items-center gap-1.5"
          >
            <Send className="w-3.5 h-3.5" /> Send
          </button>
        </div>
      </div>
    </div>
  );
}
