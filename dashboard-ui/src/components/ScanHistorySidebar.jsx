// components/ScanHistorySidebar.jsx
import { useState } from 'react'
import { History, ChevronRight, CheckCircle, AlertCircle } from 'lucide-react'

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', hour12: false })
}

export function ScanHistorySidebar({ history, onSelectScan, activeScanId }) {
  const [collapsed, setCollapsed] = useState(false)

  if (!history || history.length === 0) {
    return (
      <div className="card p-4 text-center text-slate-500 text-sm">
        <History className="w-6 h-6 mx-auto mb-2 opacity-40" />
        No previous scans
      </div>
    )
  }

  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => setCollapsed(c => !c)}
        className="w-full flex items-center justify-between px-4 py-3 bg-slate-800/60 hover:bg-slate-800 transition-colors"
      >
        <div className="flex items-center gap-2 font-semibold text-sm text-slate-300">
          <History className="w-4 h-4 text-sky-400" />
          Scan History ({history.length})
        </div>
        <ChevronRight className={`w-4 h-4 text-slate-400 transition-transform ${collapsed ? '' : 'rotate-90'}`} />
      </button>

      {!collapsed && (
        <div className="divide-y divide-slate-700/50 max-h-96 overflow-y-auto">
          {history.map(scan => {
            const isStrict = scan.compliance_mode?.toLowerCase().includes('strict')
            const isActive = scan.scan_id === activeScanId
            return (
              <button
                key={scan.scan_id}
                onClick={() => onSelectScan(scan.scan_id)}
                className={`w-full text-left px-4 py-3 hover:bg-slate-800/70 transition-colors flex items-start gap-3 ${isActive ? 'bg-sky-900/20 border-l-2 border-sky-500' : ''}`}
              >
                <div className="mt-0.5">
                  {scan.total_findings === 0
                    ? <CheckCircle className="w-4 h-4 text-emerald-400" />
                    : <AlertCircle className="w-4 h-4 text-red-400" />
                  }
                </div>
                <div className="flex-1 min-w-0 space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${isStrict ? 'bg-emerald-900/50 text-emerald-400' : 'bg-red-900/50 text-red-400'}`}>
                      {isStrict ? 'STRICT' : 'RELAXED'}
                    </span>
                    <span className="text-xs text-slate-400">{scan.total_findings} finding{scan.total_findings !== 1 ? 's' : ''}</span>
                  </div>
                  <p className="font-mono text-xs text-slate-500 truncate">{scan.scan_id}</p>
                  <p className="text-xs text-slate-500">{formatDate(scan.started_at)}</p>
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

