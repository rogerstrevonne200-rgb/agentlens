import { useState } from 'react'
import { FileText, Copy, Check, Loader2 } from 'lucide-react'

const API = 'http://localhost:7842'

export default function ReceiptPanel({ selectedSessionId }) {
  const [receipt, setReceipt] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)

  const generate = () => {
    if (!selectedSessionId) return
    setLoading(true)
    setError(null)
    setReceipt(null)

    fetch(`${API}/api/receipt/${selectedSessionId}`, { method: 'POST' })
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(data => {
        setReceipt(data.receipt || data.markdown || JSON.stringify(data, null, 2))
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }

  const copyToClipboard = () => {
    if (!receipt) return
    navigator.clipboard.writeText(receipt).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="max-w-2xl">
      <div className="bg-lens-card border border-lens-border rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <FileText className="w-5 h-5 text-lens-accent" />
          <h3 className="text-sm font-medium text-lens-text">Session Receipt</h3>
        </div>

        {!selectedSessionId ? (
          <p className="text-lens-muted text-sm">
            Select a session from the Sessions tab first, then generate a receipt.
          </p>
        ) : (
          <>
            <p className="text-xs text-lens-muted mb-4">
              Session: <span className="font-mono text-lens-accent">{selectedSessionId.slice(0, 8)}</span>
            </p>
            <button
              onClick={generate}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-lens-accent text-white rounded-lg text-sm font-medium hover:bg-lens-accent/80 transition-colors disabled:opacity-50 cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Generate Receipt
                </>
              )}
            </button>
          </>
        )}

        {error && (
          <div className="mt-4 p-3 bg-lens-red/10 border border-lens-red/30 rounded-lg text-lens-red text-sm">
            {error}
          </div>
        )}

        {receipt && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-lens-muted">Receipt</span>
              <button
                onClick={copyToClipboard}
                className="flex items-center gap-1 text-xs text-lens-muted hover:text-lens-text transition-colors cursor-pointer"
              >
                {copied ? <Check className="w-3 h-3 text-lens-green" /> : <Copy className="w-3 h-3" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <pre className="bg-lens-bg border border-lens-border rounded-lg p-4 text-xs text-lens-text font-mono whitespace-pre-wrap overflow-x-auto max-h-96 overflow-y-auto">
              {receipt}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
