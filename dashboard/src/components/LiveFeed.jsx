import { useState, useEffect, useRef } from 'react'
import { Radio, Pause, Play, Brain, Wrench, Zap, AlertCircle, ShieldOff } from 'lucide-react'

const API = 'http://localhost:7842'

const TYPE_ICONS = {
  llm_call: Brain,
  tool_call: Wrench,
  decision: Zap,
  error: AlertCircle,
  policy_block: ShieldOff,
  session_start: Zap,
  session_end: Zap,
}

const TYPE_COLORS = {
  llm_call: 'text-lens-blue',
  tool_call: 'text-lens-purple',
  decision: 'text-lens-muted',
  error: 'text-lens-red',
  policy_block: 'text-lens-orange',
  session_start: 'text-lens-green',
  session_end: 'text-lens-muted',
}

function summarize(event) {
  const parts = []
  if (event.event_type) parts.push(event.event_type.replace('_', ' '))
  if (event.model) parts.push(event.model)
  if (event.tool_name) parts.push(event.tool_name)
  if (event.cost_usd != null) parts.push(`$${event.cost_usd.toFixed(4)}`)
  if (event.prompt_preview) parts.push(event.prompt_preview.slice(0, 80))
  return parts.join(' · ') || 'event'
}

export default function LiveFeed() {
  const [events, setEvents] = useState([])
  const [paused, setPaused] = useState(false)
  const [connected, setConnected] = useState(false)
  const scrollRef = useRef(null)
  const pausedRef = useRef(false)
  const eventsRef = useRef([])

  useEffect(() => {
    pausedRef.current = paused
  }, [paused])

  useEffect(() => {
    let es
    const connect = () => {
      es = new EventSource(`${API}/api/events/stream`)
      es.onopen = () => setConnected(true)
      es.onmessage = (msg) => {
        try {
          const event = JSON.parse(msg.data)
          eventsRef.current = [event, ...eventsRef.current].slice(0, 50)
          if (!pausedRef.current) {
            setEvents([...eventsRef.current])
          }
        } catch {}
      }
      es.onerror = () => {
        setConnected(false)
        es.close()
        setTimeout(connect, 5000)
      }
    }
    connect()
    return () => es?.close()
  }, [])

  useEffect(() => {
    if (!paused && scrollRef.current) {
      scrollRef.current.scrollTop = 0
    }
  }, [events, paused])

  const togglePause = () => {
    const next = !paused
    setPaused(next)
    if (!next) {
      setEvents([...eventsRef.current])
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Radio className={`w-4 h-4 ${connected ? 'text-lens-green' : 'text-lens-red'}`} />
          <span className="text-xs text-lens-muted">
            {connected ? 'Streaming live events' : 'Connecting to event stream...'}
          </span>
        </div>
        <button
          onClick={togglePause}
          className="flex items-center gap-2 px-3 py-1.5 bg-lens-card border border-lens-border rounded-lg text-xs text-lens-muted hover:text-lens-text transition-colors cursor-pointer"
        >
          {paused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
          {paused ? 'Resume' : 'Pause'}
        </button>
      </div>

      <div
        ref={scrollRef}
        className="bg-lens-card border border-lens-border rounded-xl overflow-y-auto max-h-[calc(100vh-200px)]"
      >
        {events.length === 0 ? (
          <div className="p-12 text-center text-lens-muted text-sm">
            Waiting for events...
          </div>
        ) : (
          <div className="divide-y divide-lens-border">
            {events.map((event, i) => {
              const Icon = TYPE_ICONS[event.event_type] || Zap
              const color = TYPE_COLORS[event.event_type] || 'text-lens-muted'
              return (
                <div key={event.trace_id || i} className="flex items-start gap-3 px-4 py-3 hover:bg-lens-bg/50 transition-colors">
                  <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${color}`} />
                  <div className="min-w-0 flex-1">
                    <span className="text-xs text-lens-text">{summarize(event)}</span>
                  </div>
                  <span className="text-[10px] text-lens-muted shrink-0 font-mono">
                    {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ''}
                  </span>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
