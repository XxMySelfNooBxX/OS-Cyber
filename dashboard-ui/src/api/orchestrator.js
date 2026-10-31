// api/orchestrator.js — FastAPI Orchestrator client
const BASE_URL = 'http://127.0.0.1:8000'

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  // Target server status & toggle
  getTargetStatus: () => apiFetch('/api/target/status'),
  toggleCompliance: (enabled = null) =>
    apiFetch('/api/target/toggle', {
      method: 'POST',
      body: JSON.stringify(enabled !== null ? { enabled } : {}),
    }),

  // Scan operations
  runScan: (note = '') =>
    apiFetch('/api/scans/run', {
      method: 'POST',
      body: JSON.stringify({ target_url: 'http://127.0.0.1:5000', note }),
    }),
  getScanHistory: () => apiFetch('/api/scans/history'),
  getScanDetail: (scanId) => apiFetch(`/api/scans/${scanId}`),
}

