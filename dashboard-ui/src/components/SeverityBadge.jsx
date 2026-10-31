// components/SeverityBadge.jsx
export function SeverityBadge({ severity }) {
  const s = (severity || '').toLowerCase()
  if (s === 'high') return <span className="badge-high">HIGH</span>
  if (s === 'medium') return <span className="badge-medium">MEDIUM</span>
  if (s === 'low') return <span className="badge-low">LOW</span>
  return <span className="badge-info">{severity || 'INFO'}</span>
}

