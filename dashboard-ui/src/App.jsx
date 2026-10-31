// App.jsx — Cyber Crime & Digital Forensics Governance Center
import { useState, useEffect, useCallback } from 'react'
import { ShieldCheck, AlertOctagon, RefreshCw } from 'lucide-react'
import { api } from './api/orchestrator'
import { ControlBar } from './components/ControlBar'
import { MetricCards } from './components/MetricCards'
import { FindingCard } from './components/FindingCard'
import { ScanHistorySidebar } from './components/ScanHistorySidebar'

// ── Helpers ────────────────────────────────────────────────
function normalizeFindings(findings) {
  if (!Array.isArray(findings)) return []
  return findings.map(f => ({
    ...f,
    extracted_results: Array.isArray(f.extracted_results)
      ? f.extracted_results
      : (() => { try { return JSON.parse(f.extracted_results || '[]') } catch { return [] } })(),
    compliance: f.compliance || {
      owasp_category: f.owasp_category,
      it_act_section: f.it_act_section,
      it_act_description: f.it_act_description,
      cert_in_ref: f.cert_in_ref,
      dpdp_ref: f.dpdp_ref,
      remediation: f.remediation,
    },
    sha256_forensic_hash: f.sha256_forensic_hash || f.sha256_hash || '',
  }))
}

// ── App ────────────────────────────────────────────────────
export default function App() {
  const [status, setStatus] = useState(null)
  const [scanResult, setScanResult] = useState(null)
  const [history, setHistory] = useState([])
  const [activeScanId, setActiveScanId] = useState(null)

  const [scanning, setScanning] = useState(false)
  const [toggling, setToggling] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [error, setError] = useState(null)

  // ── Fetch status & history on mount ──
  const fetchStatus = useCallback(async () => {
    try {
      const s = await api.getTargetStatus()
      setStatus(s)
    } catch (e) {
      setStatus({ reachable: false })
    }
  }, [])

  const fetchHistory = useCallback(async () => {
    setLoadingHistory(true)
    try {
      const h = await api.getScanHistory()
      setHistory(h.scans || [])
    } catch {
      setHistory([])
    } finally {
      setLoadingHistory(false)
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    fetchHistory()
    const interval = setInterval(fetchStatus, 8000)
    return () => clearInterval(interval)
  }, [fetchStatus, fetchHistory])

  // ── Toggle compliance mode ──
  const handleToggle = async () => {
    setToggling(true)
    setError(null)
    try {
      await api.toggleCompliance()
      await fetchStatus()
    } catch (e) {
      setError(`Toggle failed: ${e.message}`)
    } finally {
      setToggling(false)
    }
  }

  // ── Run live Nuclei scan ──
  const handleScan = async () => {
    setScanning(true)
    setError(null)
    try {
      const result = await api.runScan('Dashboard-triggered scan')
      const normalized = { ...result, findings: normalizeFindings(result.findings) }
      setScanResult(normalized)
      setActiveScanId(result.scan_id)
      await fetchHistory()
    } catch (e) {
      setError(`Scan failed: ${e.message}`)
    } finally {
      setScanning(false)
    }
  }

  // ── Load historical scan ──
  const handleSelectScan = async (scanId) => {
    setError(null)
    try {
      const detail = await api.getScanDetail(scanId)
      const normalized = {
        scan_id: detail.scan_id,
        target_url: detail.target_url,
        compliance_mode_detected: detail.compliance_mode,
        total_findings: detail.total_findings,
        severity_summary: { high: 0, medium: 0, low: 0 },
        findings: normalizeFindings(detail.findings || []),
      }
      // Build severity summary from findings
      normalized.findings.forEach(f => {
        const s = (f.severity || '').toLowerCase()
        if (s in normalized.severity_summary) normalized.severity_summary[s]++
      })
      setScanResult(normalized)
      setActiveScanId(scanId)
    } catch (e) {
      setError(`Failed to load scan: ${e.message}`)
    }
  }

  const isStrict = status?.strict_compliance_mode
  const findings = scanResult?.findings || []
  const hasFindings = findings.length > 0

  return (
    <div className="min-h-screen bg-slate-950">
      {/* ── Header ── */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-30 no-print">
        <div className="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-sky-500/20 border border-sky-500/30 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-sky-400" />
            </div>
            <div>
              <h1 className="font-bold text-slate-100 text-lg leading-tight">
                Cyber Crime & Digital Forensics Governance Center
              </h1>
              <p className="text-xs text-slate-500">
                CyberBank Academic QA Platform · Nuclei v3.11.1 · FastAPI Orchestrator ·{' '}
                <span className="font-mono">127.0.0.1:5000</span>
              </p>
            </div>
          </div>
          <button
            onClick={() => { fetchStatus(); fetchHistory() }}
            className="text-slate-500 hover:text-slate-300 transition-colors"
            title="Refresh status"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </header>

      <main className="max-w-screen-2xl mx-auto px-6 py-6 space-y-6">
        {/* ── Error Banner ── */}
        {error && (
          <div className="bg-red-900/30 border border-red-700/50 rounded-xl px-4 py-3 flex items-center gap-3 text-red-300 text-sm no-print">
            <AlertOctagon className="w-4 h-4 flex-shrink-0" />
            {error}
            <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-200 font-bold">✕</button>
          </div>
        )}

        {/* ── Control Bar ── */}
        <ControlBar
          status={status}
          onToggle={handleToggle}
          onScan={handleScan}
          scanning={scanning}
          toggling={toggling}
        />

        {/* ── Metrics ── */}
        <MetricCards scanResult={scanResult} />

        {/* ── Main content: Findings + Sidebar ── */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 items-start">
          {/* Findings panel */}
          <div className="xl:col-span-3 space-y-4">
            {/* Print header */}
            <div className="hidden print:block mb-6">
              <h2 className="text-2xl font-bold">CyberBank — Digital Forensics Audit Report</h2>
              <p className="text-sm text-gray-600 mt-1">
                Scan ID: {scanResult?.scan_id} · Mode: {scanResult?.compliance_mode_detected} · Generated: {new Date().toUTCString()}
              </p>
              <hr className="mt-3" />
            </div>

            {!scanResult && !scanning && (
              <div className="card p-12 text-center space-y-3">
                <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto" />
                <h3 className="text-lg font-semibold text-slate-400">No Scan Results Yet</h3>
                <p className="text-slate-500 text-sm max-w-md mx-auto">
                  Click <strong className="text-sky-400">Run Live Nuclei Audit</strong> to execute Nuclei v3.11.1 against the
                  local Flask target server and display forensic findings with SHA-256 chain-of-custody hashes.
                </p>
              </div>
            )}

            {scanning && (
              <div className="card p-12 text-center space-y-4">
                <div className="w-12 h-12 border-4 border-sky-500/30 border-t-sky-500 rounded-full animate-spin mx-auto" />
                <h3 className="text-lg font-semibold text-sky-400">Nuclei Audit In Progress…</h3>
                <p className="text-slate-500 text-sm">
                  Executing: <code className="font-mono bg-slate-800 px-2 py-0.5 rounded text-xs">nuclei -u http://127.0.0.1:5000 -t custom-templates/ -jsonl -silent</code>
                </p>
              </div>
            )}

            {scanResult && !scanning && (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-bold text-slate-300">
                    Forensic Findings & Evidence Vault
                    <span className="ml-2 text-slate-500 font-normal text-sm">({scanResult.compliance_mode_detected})</span>
                  </h2>
                </div>

                {/* Zero findings — strict mode banner */}
                {!hasFindings && (
                  <div className="card border-emerald-700/50 bg-emerald-950/20 p-8 text-center space-y-3">
                    <ShieldCheck className="w-14 h-14 text-emerald-400 mx-auto" />
                    <h3 className="text-xl font-bold text-emerald-400">All Compliance Controls Verified — 0 Exposures Detected</h3>
                    <p className="text-slate-400 text-sm max-w-xl mx-auto leading-relaxed">
                      STRICT COMPLIANCE MODE is active. All vulnerability probes were blocked:
                    </p>
                    <div className="flex flex-wrap justify-center gap-3 text-sm">
                      {[
                        ['Customer API', '401 Unauthorized — Token Required'],
                        ['Debug Config', '403 Forbidden — Endpoint Locked'],
                        ['Security Headers', 'X-Frame-Options + CSP Active'],
                      ].map(([label, desc]) => (
                        <div key={label} className="bg-emerald-900/30 border border-emerald-700/40 rounded-lg px-4 py-2 text-left">
                          <p className="text-emerald-300 font-semibold text-xs">{label}</p>
                          <p className="text-emerald-500 text-xs mt-0.5">{desc}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Findings list */}
                {hasFindings && (
                  <div className="space-y-4">
                    {findings.map((finding, idx) => (
                      <FindingCard key={`${finding.template_id}-${idx}`} finding={finding} index={idx} />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>

          {/* Sidebar */}
          <div className="xl:col-span-1 space-y-4 no-print">
            <ScanHistorySidebar
              history={history}
              onSelectScan={handleSelectScan}
              activeScanId={activeScanId}
            />
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-800 mt-12 py-4 text-center text-slate-600 text-xs no-print">
        CyberBank Academic QA Compliance Platform · Digital Forensics & API Governance · All scans locked to 127.0.0.1:5000
      </footer>
    </div>
  )
}

