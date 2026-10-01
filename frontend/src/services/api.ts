const API_BASE = '/api/v1';

export async function fetchOverview(snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/overview?snapshot_id=${snapshotId}`);
  if (!res.ok) throw new Error('Failed to load overview data');
  return res.json();
}

export async function fetchNsfrDetail(snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/metrics/nsfr?snapshot_id=${snapshotId}`);
  if (!res.ok) throw new Error('Failed to load NSFR details');
  return res.json();
}

export async function fetchLcrDetail(snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/metrics/lcr?snapshot_id=${snapshotId}`);
  if (!res.ok) throw new Error('Failed to load LCR details');
  return res.json();
}

export async function fetchLineage(metricName: string = 'NSFR', snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/lineage/${metricName}?snapshot_id=${snapshotId}`);
  if (!res.ok) throw new Error('Failed to load lineage graph');
  return res.json();
}

export async function fetchBlastRadius(controlId: string, snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/lineage/blast-radius/${controlId}?snapshot_id=${snapshotId}`);
  if (!res.ok) throw new Error('Failed to compute blast radius');
  return res.json();
}

export async function runScenario(params: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}/scenarios/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to execute scenario');
  return res.json();
}

export async function fetchControls(snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/controls?snapshot_id=${snapshotId}`);
  if (!res.ok) throw new Error('Failed to load controls');
  return res.json();
}

export async function fetchExceptions(snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/exceptions?snapshot_id=${snapshotId}`);
  if (!res.ok) throw new Error('Failed to load exceptions');
  return res.json();
}

export async function updateException(exceptionId: string, payload: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}/exceptions/${exceptionId}/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to update exception');
  return res.json();
}

export async function fetchCloseStatus(period: string = '2026-Q3') {
  const res = await fetch(`${API_BASE}/close/status?period=${period}`);
  if (!res.ok) throw new Error('Failed to load close status');
  return res.json();
}

export async function advanceCloseStep(stepNumber: number, period: string = '2026-Q3') {
  const res = await fetch(`${API_BASE}/close/advance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ period, step_number: stepNumber, actor_role: 'Lead Controller' }),
  });
  if (!res.ok) throw new Error('Failed to advance close stage');
  return res.json();
}

export async function injectLateAdjustment(params: Record<string, unknown> = {}) {
  const res = await fetch(`${API_BASE}/close/late-adjustment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to inject late adjustment');
  return res.json();
}

export async function compileReports(snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/reports/compile?snapshot_id=${snapshotId}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to compile reporting pack');
  return res.json();
}

export async function fetchQueries() {
  const res = await fetch(`${API_BASE}/queries`);
  if (!res.ok) throw new Error('Failed to load queries');
  return res.json();
}

export async function fetchEventReplay(snapshotId: string = 'SNAP-2026-Q3-BASE', limit: number = 40) {
  const res = await fetch(`${API_BASE}/replay?snapshot_id=${snapshotId}&limit=${limit}`);
  if (!res.ok) throw new Error('Failed to load replay events');
  return res.json();
}

export async function askCopilot(question: string, forceAdversarial: string | null = null, snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/copilot/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, force_adversarial_error: forceAdversarial, snapshot_id: snapshotId }),
  });
  if (!res.ok) throw new Error('Failed to consult Copilot');
  return res.json();
}

export async function fetchRedTeamResults(snapshotId: string = 'SNAP-2026-Q3-BASE') {
  const res = await fetch(`${API_BASE}/copilot/red-team?snapshot_id=${snapshotId}`);
  if (!res.ok) throw new Error('Failed to run AI red-team suite');
  return res.json();
}
