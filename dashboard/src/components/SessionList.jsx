import { useState, useEffect } from 'react'
import { Clock, Zap, DollarSign } from 'lucide-react'

const API = 'http://localhost:7842'

function costColor(cost) {
  if (cost > 1) return 'bg-lens-red/20 text-lens-red'
  if (cost >= 0.10) return 'bg-lens-yellow/20 text-lens-yellow'
  return 'bg-lens-green/20 text-lens-green'
}

function formatDuration(ms) {
  if (!ms) return '-'
  if (ms < 1000) return `${ms}ms`
  const s = (ms / 1000).toFixed(1)
  return `${s}s`
}

export default function SessionList({ selectedId, onSelect }) {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchSessions = () => {
      fetch(`${API}/api/sessions`)
        .then(r => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`)
          return r.json()
        })
        .then(data => {
          setSessions(data.sessions || data || [])
          setLoading(false)
          setError(null)
        })
        .catch(err => {
          setError(err.message)
          setLoading(false)
        })
    }
    fetchSessions()
    const id = setInterval(fetchSessions, 5000)
    return () => clearInterval(id)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-lens-muted">
        <div className="animate-spin w-6 h-6 border-2 border-lens-accent border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-lens-card border border-lens-border rounded-xl p-8 text-center">
        <p className="text-lens-muted text-sm">Cannot reach server: {error}</p>
      </div>
    )
  }

  if (sessions.length === 0) {
    return (
      <div className="bg-lens-card border border-lens-border rounded-xl p-12 text-center">
        <Zap className="w-10 h-10 text-lens-muted mx-auto mb-4" />
        <p className="text-lens-muted text-sm">
          No sessions yet. Start your agent with AgentLens to see traces here.
        </p>
      </div>
    )
  }

  return (
    <div className="bg-lens-card border border-lens-border rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-lens-border text-lens-muted text-xs uppercase tracking-wider">
            <th className="text-left px-4 py-3 font-medium">Session ID</th>
            <th className="text-left px-4 py-3 font-medium">Date</th>
            <th className="text-left px-4 py-3 font-medium">Duration</th>
            <th className="text-left px-4 py-3 font-medium">Cost</th>
            <th className="text-left px-4 py-3 font-medium">Events</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map(s => (
            <tr
              key={s.session_id}
              onClick={() => onSelect(s.session_id)}
              className={`border-b border-lens-border cursor-pointer transition-colors ${
                selectedId === s.session_id
                  ? 'bg-lens-accent/10'
                  : 'hover:bg-lens-bg/50'
              }`}
            >
              <td className="px-4 py-3 font-mono text-lens-accent">
                {s.session_id?.slice(0, 8)}
              </td>
              <td className="px-4 py-3 text-lens-muted">
                {s.start_time ? new Date(s.start_time).toLocaleString() : '-'}
              </td>
              <td className="px-4 py-3 text-lens-muted flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatDuration(s.duration_ms)}
              </td>
              <td className="px-4 py-3">
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${costColor(s.total_cost || 0)}`}>
                  <DollarSign className="w-3 h-3" />
                  {(s.total_cost || 0).toFixed(4)}
                </span>
              </td>
              <td className="px-4 py-3 text-lens-muted">
                {s.event_count || 0}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
