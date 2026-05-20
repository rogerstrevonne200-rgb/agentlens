import { useState, useEffect } from 'react'
import { List, Radio, DollarSign, FileText, Eye } from 'lucide-react'
import SessionList from './components/SessionList'
import TraceTimeline from './components/TraceTimeline'
import CostMeter from './components/CostMeter'
import ReceiptPanel from './components/ReceiptPanel'
import LiveFeed from './components/LiveFeed'

const API = 'http://localhost:7842'

const NAV_ITEMS = [
  { id: 'sessions', label: 'Sessions', icon: List },
  { id: 'live', label: 'Live Feed', icon: Radio },
  { id: 'cost', label: 'Cost', icon: DollarSign },
  { id: 'receipt', label: 'Receipt', icon: FileText },
]

export default function App() {
  const [view, setView] = useState('sessions')
  const [serverUp, setServerUp] = useState(false)
  const [selectedSessionId, setSelectedSessionId] = useState(null)

  useEffect(() => {
    const check = () => {
      fetch(`${API}/`)
        .then(r => r.ok ? setServerUp(true) : setServerUp(false))
        .catch(() => setServerUp(false))
    }
    check()
    const id = setInterval(check, 5000)
    return () => clearInterval(id)
  }, [])

  const handleSelectSession = (id) => {
    setSelectedSessionId(id)
    setView('sessions')
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-56 bg-lens-sidebar border-r border-lens-border flex flex-col shrink-0">
        <div className="p-4 border-b border-lens-border flex items-center gap-2">
          <Eye className="w-5 h-5 text-lens-accent" />
          <span className="font-semibold text-lg text-lens-text">AgentLens</span>
        </div>
        <nav className="flex-1 p-2 space-y-1">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setView(id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
                view === id
                  ? 'bg-lens-accent/15 text-lens-accent'
                  : 'text-lens-muted hover:bg-lens-card hover:text-lens-text'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </nav>
        <div className="p-4 border-t border-lens-border">
          <div className="flex items-center gap-2 text-xs text-lens-muted">
            <span className={`w-2 h-2 rounded-full ${serverUp ? 'bg-lens-green' : 'bg-lens-red'}`} />
            {serverUp ? 'Server connected' : 'Server offline'}
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto bg-lens-bg">
        <header className="sticky top-0 z-10 bg-lens-bg/80 backdrop-blur border-b border-lens-border px-6 py-3 flex items-center justify-between">
          <h1 className="text-lg font-medium text-lens-text">
            {NAV_ITEMS.find(n => n.id === view)?.label}
          </h1>
          <div className="flex items-center gap-2 text-xs text-lens-muted">
            <span className={`w-2 h-2 rounded-full ${serverUp ? 'bg-lens-green animate-pulse' : 'bg-lens-red'}`} />
            {serverUp ? 'Connected to :7842' : 'Disconnected'}
          </div>
        </header>
        <div className="p-6">
          {view === 'sessions' && (
            <div className="flex gap-6">
              <div className={selectedSessionId ? 'w-1/2' : 'w-full'}>
                <SessionList
                  selectedId={selectedSessionId}
                  onSelect={handleSelectSession}
                />
              </div>
              {selectedSessionId && (
                <div className="w-1/2">
                  <TraceTimeline selectedSessionId={selectedSessionId} />
                </div>
              )}
            </div>
          )}
          {view === 'live' && <LiveFeed />}
          {view === 'cost' && <CostMeter />}
          {view === 'receipt' && <ReceiptPanel selectedSessionId={selectedSessionId} />}
        </div>
      </main>
    </div>
  )
}
