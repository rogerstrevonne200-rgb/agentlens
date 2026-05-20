import { useState, useEffect } from 'react'
import { DollarSign, BarChart3, Hash } from 'lucide-react'

const API = 'http://localhost:7842'

export default function CostMeter() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchCost = () => {
      fetch(`${API}/api/cost/summary`)
        .then(r => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`)
          return r.json()
        })
        .then(d => {
          setData(d)
          setLoading(false)
          setError(null)
        })
        .catch(err => {
          setError(err.message)
          setLoading(false)
        })
    }
    fetchCost()
    const id = setInterval(fetchCost, 10000)
    return () => clearInterval(id)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-6 h-6 border-2 border-lens-accent border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-lens-card border border-lens-border rounded-xl p-8 text-center">
        <p className="text-lens-muted text-sm">Cannot load cost data: {error}</p>
      </div>
    )
  }

  const models = data?.by_model || {}
  const maxCost = Math.max(...Object.values(models).map(m => m.cost || 0), 0.001)

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          icon={DollarSign}
          label="Total Spent"
          value={`$${(data?.total_cost || 0).toFixed(4)}`}
          color="text-lens-green"
        />
        <StatCard
          icon={Hash}
          label="Total Calls"
          value={data?.total_calls || 0}
          color="text-lens-blue"
        />
        <StatCard
          icon={BarChart3}
          label="Avg / Session"
          value={`$${(data?.avg_cost_per_session || 0).toFixed(4)}`}
          color="text-lens-purple"
        />
      </div>

      <div className="bg-lens-card border border-lens-border rounded-xl p-6">
        <h3 className="text-sm font-medium text-lens-text mb-4">Cost by Model</h3>
        {Object.keys(models).length === 0 ? (
          <p className="text-lens-muted text-sm">No model data available yet.</p>
        ) : (
          <div className="space-y-3">
            {Object.entries(models).map(([model, stats]) => {
              const pct = ((stats.cost || 0) / maxCost) * 100
              return (
                <div key={model}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-lens-text font-medium">{model}</span>
                    <span className="text-lens-muted">
                      ${(stats.cost || 0).toFixed(4)} &middot; {stats.calls || 0} calls
                    </span>
                  </div>
                  <div className="h-6 bg-lens-bg rounded-md overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-lens-accent to-lens-purple rounded-md transition-all duration-500"
                      style={{ width: `${Math.max(pct, 2)}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-lens-card border border-lens-border rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${color}`} />
        <span className="text-xs text-lens-muted">{label}</span>
      </div>
      <span className="text-xl font-semibold text-lens-text">{value}</span>
    </div>
  )
}
