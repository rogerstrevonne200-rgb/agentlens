import { useState, useEffect } from 'react'
import { Brain, Wrench, Zap, AlertCircle, ShieldOff, ChevronDown, ChevronRight, DollarSign } from 'lucide-react'

const API = 'http://localhost:7842'

const EVENT_CONFIG = {
  llm_call: { icon: Brain, color: 'lens-blue', label: 'LLM Call' },
  tool_call: { icon: Wrench, color: 'lens-purple', label: 'Tool Call' },
  decision: { icon: Zap, color: 'lens-muted', label: 'Decision' },
  error: { icon: AlertCircle, color: 'lens-red', label: 'Error' },
  policy_block: { icon: ShieldOff, color: 'lens-orange', label: 'Policy Block' },
  session_start: { icon: Zap, color: 'lens-green', label: 'Session Start' },
  session_end: { icon: Zap, color: 'lens-muted', label: 'Session End' },
}

function EventCard({ event }) {
  const [expanded, setExpanded] = useState(false)
  const config = EVENT_CONFIG[event.event_type] || EVENT_CONFIG.decision
  const Icon = config.icon
  const Chevron = expanded ? ChevronDown : ChevronRight

  return (
    <div className="relative pl-8 pb-4">
      <div className={`absolute left-0 top-1 w-6 h-6 rounded-full bg-${config.color}/20 flex items-center justify-center`}>
        <Icon className={`w-3.5 h-3.5 text-${config.color}`} />
      </div>
      <div className="absolute left-3 top-7 bottom-0 w-px bg-lens-border" />

      <div
        onClick={() => setExpanded(!expanded)}
        className="bg-lens-card border border-lens-border rounded-lg p-3 cursor-pointer hover:border-lens-muted/30 transition-colors"
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <Chevron className="w-4 h-4 text-lens-muted shrink-0" />
            <span className={`text-xs font-medium text-${config.color}`}>{config.label}</span>
            <Summary event={event} />
          </div>
          {event.duration_ms != null && (
            <span className="text-xs text-lens-muted shrink-0">{event.duration_ms}ms</span>
          )}
        </div>

        {expanded && (
          <div className="mt-3 pt-3 border-t border-lens-border text-xs space-y-2">
            {event.model && <Detail label="Model" value={event.model} />}
            {event.input_tokens != null && (
              <Detail label="Tokens" value={`${event.input_tokens} in / ${event.output_tokens} out`} />
            )}
            {event.cost_usd != null && (
              <Detail label="Cost" value={`$${event.cost_usd.toFixed(6)}`} />
            )}
            {event.tool_name && <Detail label="Tool" value={event.tool_name} />}
            {event.tool_input && (
              <Detail label="Input" value={JSON.stringify(event.tool_input, null, 2)} mono />
            )}
            {event.tool_output && (
              <Detail label="Output" value={JSON.stringify(event.tool_output, null, 2)} mono />
            )}
            {event.prompt_preview && <Detail label="Prompt" value={event.prompt_preview} mono />}
            {event.response_preview && <Detail label="Response" value={event.response_preview} mono />}
            {event.metadata && Object.keys(event.metadata).length > 0 && (
              <Detail label="Metadata" value={JSON.stringify(event.metadata, null, 2)} mono />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function Summary({ event }) {
  const parts = []
  if (event.model) parts.push(event.model)
  if (event.tool_name) parts.push(event.tool_name)
  if (event.cost_usd != null) parts.push(`$${event.cost_usd.toFixed(4)}`)
  if (event.prompt_preview) parts.push(event.prompt_preview.slice(0, 60) + '...')
  if (event.event_type === 'error' && event.metadata?.error) parts.push(event.metadata.error)
  if (event.event_type === 'policy_block' && event.metadata?.blocked) parts.push(event.metadata.blocked)
  if (event.event_type === 'decision') {
    if (event.metadata?.function_name) parts.push(event.metadata.function_name)
    if (event.metadata?.args) parts.push(JSON.stringify(event.metadata.args))
  }
  return (
    <span className="text-xs text-lens-muted truncate">
      {parts.join(' · ') || '-'}
    </span>
  )
}

function Detail({ label, value, mono }) {
  return (
    <div>
      <span className="text-lens-muted">{label}:</span>{' '}
      {mono ? (
        <pre className="mt-1 bg-lens-bg rounded p-2 overflow-x-auto whitespace-pre-wrap text-lens-text">{value}</pre>
      ) : (
        <span className="text-lens-text">{value}</span>
      )}
    </div>
  )
}

export default function TraceTimeline({ selectedSessionId }) {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!selectedSessionId) return
    setLoading(true)
    fetch(`${API}/api/sessions/${selectedSessionId}`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(data => {
        setSession(data)
        setLoading(false)
        setError(null)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [selectedSessionId])

  if (!selectedSessionId) {
    return (
      <div className="text-center text-lens-muted text-sm py-12">
        Select a session to view its trace timeline.
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-6 h-6 border-2 border-lens-accent border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-lens-card border border-lens-border rounded-xl p-6 text-center">
        <p className="text-lens-red text-sm">Failed to load session: {error}</p>
      </div>
    )
  }

  const events = session?.events || []
  const totalCost = events.reduce((sum, e) => sum + (e.cost_usd || 0), 0)

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <span className="font-mono text-sm text-lens-accent">{selectedSessionId.slice(0, 8)}</span>
        <span className="flex items-center gap-1 px-2 py-0.5 bg-lens-green/20 text-lens-green rounded-full text-xs font-medium">
          <DollarSign className="w-3 h-3" />
          {totalCost.toFixed(4)}
        </span>
        <span className="text-xs text-lens-muted">{events.length} events</span>
      </div>
      <div>
        {events.map((event, i) => (
          <EventCard key={event.trace_id || i} event={event} />
        ))}
      </div>
    </div>
  )
}
