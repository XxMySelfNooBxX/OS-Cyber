// components/FindingCard.jsx
import { useState } from 'react'
import { Copy, Check, ChevronDown, ChevronUp, Terminal, Scale, Shield } from 'lucide-react'
import { SeverityBadge } from './SeverityBadge'

function CopyButton({ text, label = 'Copy' }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }
  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1 text-xs px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors"
    >
      {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
      {copied ? 'Copied!' : label}
    </button>
  )
}

function ComplianceGrid({ compliance }) {
  const [open, setOpen] = useState(false)
  if (!compliance) return null
  return (
    <div className="border border-slate-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 bg-slate-800/60 hover:bg-slate-800 transition-colors text-left"
      >
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
          <Scale className="w-4 h-4 text-violet-400" />
          Legal & Regulatory Compliance Mapping
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>
      {open && (
        <div className="p-4 space-y-3 bg-slate-900/50">
          <Row label="OWASP API Security Top 10" value={compliance.owasp_category} color="text-violet-300" />
          <Row label="Indian IT Act 2000 — Section" value={compliance.it_act_section} color="text-amber-300" />
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">IT Act Legal Basis</p>
            <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/50 rounded p-3 border border-slate-700/50">
              {compliance.it_act_description}
            </p>
          </div>
          <Row label="CERT-In 2022 Reference" value={compliance.cert_in_ref} color="text-sky-300" />
          <Row label="DPDP Act 2023" value={compliance.dpdp_ref} color="text-emerald-300" />
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Remediation Guidance</p>
            <p className="text-sm text-emerald-300 leading-relaxed bg-emerald-950/20 rounded p-3 border border-emerald-700/30">
              {compliance.remediation}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

function Row({ label, value, color = 'text-slate-300' }) {
  return (
    <div className="space-y-0.5">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">{label}</p>
      <p className={`text-sm font-medium ${color}`}>{value || '—'}</p>
    </div>
  )
}

export function FindingCard({ finding, index }) {
  const {
    template_id, template_name, severity, matched_at,
    extracted_results, curl_command, sha256_forensic_hash,
    sha256_hash, compliance, timestamp,
  } = finding

  const hash = sha256_forensic_hash || sha256_hash || ''
  const extracted = Array.isArray(extracted_results)
    ? extracted_results
    : (typeof extracted_results === 'string'
        ? JSON.parse(extracted_results || '[]')
        : [])

  return (
    <div className="finding-card card p-5 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-slate-500 text-sm font-mono">#{index + 1}</span>
          <SeverityBadge severity={severity} />
          <h3 className="font-bold text-slate-100 text-sm">{template_name}</h3>
        </div>
      </div>

      {/* Endpoint & Template ID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="space-y-1">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Matched Endpoint</p>
          <p className="font-mono text-sm text-sky-400 bg-slate-950/50 px-3 py-1.5 rounded border border-slate-700/50 break-all">{matched_at}</p>
        </div>
        <div className="space-y-1">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Template ID</p>
          <p className="font-mono text-sm text-slate-300 bg-slate-950/50 px-3 py-1.5 rounded border border-slate-700/50">{template_id}</p>
        </div>
      </div>

      {/* Extracted Evidence */}
      {extracted.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-red-400 uppercase tracking-wide flex items-center gap-1.5">
            <Shield className="w-3 h-3" /> Extracted Audit Evidence — Live PII / Config Fields
          </p>
          <div className="bg-red-950/20 border border-red-700/30 rounded-lg p-3 flex flex-wrap gap-2">
            {extracted.map((val, i) => (
              <span key={i} className="font-mono text-sm bg-slate-950 text-red-300 px-2.5 py-1 rounded border border-red-700/40">
                {val}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* SHA-256 Chain of Custody */}
      {hash && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-emerald-400 uppercase tracking-wide">
              Digital Forensics — SHA-256 Chain-of-Custody Hash
            </p>
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-950/30 border border-emerald-700/40 px-2 py-0.5 rounded-full">
                <Check className="w-3 h-3" /> Verified Integrity
              </span>
              <CopyButton text={hash} label="Copy Hash" />
            </div>
          </div>
          <div className="hash-box">{hash}</div>
        </div>
      )}

      {/* curl Command */}
      {curl_command && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide flex items-center gap-1.5">
              <Terminal className="w-3 h-3" /> Reproducible curl Command
            </p>
            <CopyButton text={curl_command} label="Copy" />
          </div>
          <div className="font-mono text-xs bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-300 break-all">
            {curl_command}
          </div>
        </div>
      )}

      {/* Compliance Accordion */}
      <ComplianceGrid compliance={compliance} />
    </div>
  )
}

