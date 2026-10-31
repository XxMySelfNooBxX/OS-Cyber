// components/ControlBar.jsx
import { Loader2, Play, ToggleLeft, ToggleRight, Wifi, WifiOff, Printer } from 'lucide-react'

export function ControlBar({ status, onToggle, onScan, scanning, toggling }) {
  const reachable = status?.reachable
  const isStrict = status?.strict_compliance_mode

  return (
    <div className="card p-4 no-print">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left: Server posture */}
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            {reachable
              ? <Wifi className="w-4 h-4 text-emerald-400" />
              : <WifiOff className="w-4 h-4 text-red-400" />}
            <span className="text-sm font-semibold text-slate-400">Target Server</span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${reachable ? 'bg-emerald-900/40 text-emerald-400 border border-emerald-700/40' : 'bg-red-900/40 text-red-400 border border-red-700/40'}`}>
              {reachable ? 'CONNECTED' : 'OFFLINE'}
            </span>
          </div>

          {reachable && (
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-sm font-bold ${
              isStrict
                ? 'bg-emerald-900/30 border-emerald-700/50 text-emerald-400'
                : 'bg-red-900/30 border-red-700/50 text-red-400'
            }`}>
              {isStrict
                ? <>✅ STRICT COMPLIANCE MODE — HARDENED</>
                : <>⚠️ RELAXED MODE — UNPROTECTED</>}
            </div>
          )}
        </div>

        {/* Right: Action buttons */}
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={onToggle}
            disabled={toggling || !reachable}
            className="btn-secondary text-sm"
          >
            {toggling
              ? <Loader2 className="w-4 h-4 animate-spin" />
              : (isStrict ? <ToggleRight className="w-4 h-4 text-emerald-400" /> : <ToggleLeft className="w-4 h-4 text-red-400" />)}
            Toggle Compliance Mode
          </button>

          <button
            onClick={onScan}
            disabled={scanning || !reachable}
            className="btn-primary text-sm"
          >
            {scanning
              ? <><Loader2 className="w-4 h-4 animate-spin" /> Scanning…</>
              : <><Play className="w-4 h-4" /> Run Live Nuclei Audit</>}
          </button>

          <button
            onClick={() => window.print()}
            className="btn-secondary text-sm no-print"
            title="Export forensic report"
          >
            <Printer className="w-4 h-4" />
            Print / Export
          </button>
        </div>
      </div>
    </div>
  )
}

