// components/MetricCards.jsx
import { ShieldAlert, ShieldX, AlertTriangle, Info, Hash, Clock } from 'lucide-react'

function MetricCard({ icon: Icon, label, value, colorClass, bgClass }) {
  return (
    <div className={`card p-4 flex items-center gap-4 ${bgClass || ''}`}>
      <div className={`p-3 rounded-lg ${colorClass}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-slate-400 text-xs font-semibold uppercase tracking-wide">{label}</p>
        <p className="text-2xl font-bold text-slate-100">{value ?? '—'}</p>
      </div>
    </div>
  )
}

export function MetricCards({ scanResult }) {
  if (!scanResult) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {['Total Findings', 'High Severity', 'Medium Severity', 'Low Severity'].map(label => (
          <MetricCard key={label} icon={ShieldAlert} label={label} value="—" colorClass="bg-slate-700/50 text-slate-400" />
        ))}
      </div>
    )
  }

  const { total_findings, severity_summary, scan_id, findings } = scanResult
  const high = severity_summary?.high ?? 0
  const medium = severity_summary?.medium ?? 0
  const low = severity_summary?.low ?? 0
  const ts = findings?.[0]?.timestamp ?? null

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={ShieldAlert}
          label="Total Findings"
          value={total_findings}
          colorClass={total_findings > 0 ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}
        />
        <MetricCard
          icon={ShieldX}
          label="High Severity"
          value={high}
          colorClass={high > 0 ? 'bg-red-500/20 text-red-400' : 'bg-slate-700/50 text-slate-400'}
        />
        <MetricCard
          icon={AlertTriangle}
          label="Medium Severity"
          value={medium}
          colorClass={medium > 0 ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-700/50 text-slate-400'}
        />
        <MetricCard
          icon={Info}
          label="Low Severity"
          value={low}
          colorClass={low > 0 ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-700/50 text-slate-400'}
        />
      </div>
      <div className="flex flex-wrap gap-3 text-xs text-slate-500">
        {scan_id && (
          <span className="flex items-center gap-1.5">
            <Hash className="w-3 h-3" />
            <span className="font-mono text-slate-400">{scan_id}</span>
          </span>
        )}
        {ts && (
          <span className="flex items-center gap-1.5">
            <Clock className="w-3 h-3" />
            <span className="text-slate-400">{new Date(ts).toUTCString()}</span>
          </span>
        )}
      </div>
    </div>
  )
}

