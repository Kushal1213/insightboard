import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Clock, CheckCircle2, XCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { fetchHistory } from '../services/api'
import { useState } from 'react'

export default function HistoryPage() {
  const { id } = useParams()
  const [expanded, setExpanded] = useState(null)

  const { data: history = [], isLoading } = useQuery({
    queryKey: ['history', id],
    queryFn: () => fetchHistory(id).then(r => r.data),
    refetchInterval: 20_000,
  })

  return (
    <div className="p-8 max-w-3xl mx-auto animate-fade-in">
      <div className="flex items-center gap-2 mb-8">
        <Clock size={18} style={{ color: 'var(--accent-light)' }} />
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Query History</h1>
        <span
          className="ml-2 px-2 py-0.5 rounded-full text-xs"
          style={{ background: 'var(--bg-hover)', color: 'var(--text-muted)' }}
        >
          {history.length}
        </span>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
          <div className="spinner" /> Loading…
        </div>
      )}

      {!isLoading && history.length === 0 && (
        <div
          className="rounded-2xl border p-12 text-center"
          style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
        >
          <Clock size={32} className="mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
          <p style={{ color: 'var(--text-muted)' }}>No queries yet.</p>
        </div>
      )}

      <div className="flex flex-col gap-3">
        {history.map((item) => {
          const isOpen = expanded === item.id
          const isSuccess = item.status === 'success'

          return (
            <div
              key={item.id}
              className="rounded-xl border overflow-hidden transition-all"
              style={{ background: 'var(--bg-secondary)', borderColor: isOpen ? 'rgba(99,102,241,0.4)' : 'var(--border)' }}
            >
              <button
                className="w-full text-left px-4 py-3.5 flex items-center gap-3"
                onClick={() => setExpanded(isOpen ? null : item.id)}
              >
                {isSuccess
                  ? <CheckCircle2 size={16} style={{ color: 'var(--success)', flexShrink: 0 }} />
                  : <XCircle size={16} style={{ color: 'var(--danger)', flexShrink: 0 }} />
                }
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                    {item.question}
                  </p>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    {item.row_count} rows · {item.execution_time_ms?.toFixed(0)}ms ·{' '}
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                {isOpen
                  ? <ChevronUp size={15} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
                  : <ChevronDown size={15} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
                }
              </button>

              {isOpen && (
                <div className="px-4 pb-4 border-t animate-slide-up" style={{ borderColor: 'var(--border)' }}>
                  <p className="text-xs font-medium mt-3 mb-1.5" style={{ color: 'var(--text-muted)' }}>SQL</p>
                  <div className="sql-block">
                    {item.generated_sql || '—'}
                  </div>
                  {item.error_message && (
                    <div
                      className="mt-3 px-3 py-2.5 rounded-lg text-xs"
                      style={{ background: 'rgba(248,113,113,0.08)', color: 'var(--danger)', border: '1px solid rgba(248,113,113,0.2)' }}
                    >
                      {item.error_message}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
