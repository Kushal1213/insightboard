import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Zap, Send, PlusCircle, Table, BarChart2, TrendingUp, PieChart } from 'lucide-react'
import { fetchDataset, runQuery, createWidget } from '../services/api'
import ResultTable from '../components/ui/ResultTable'
import ChartPreview from '../components/charts/ChartPreview'

const SUGGESTED_QUESTIONS = [
  'Show me the first 10 rows',
  'Count rows grouped by each category',
  'Find the top 5 highest values',
  'Show summary statistics',
]

export default function DatasetPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [activeTab, setActiveTab] = useState('table') // table | bar | line | pie
  const [saving, setSaving] = useState(false)

  const { data: dataset, isLoading: dsLoading } = useQuery({
    queryKey: ['dataset', id],
    queryFn: () => fetchDataset(id).then(r => r.data),
  })

  const queryMut = useMutation({
    mutationFn: ({ question }) => runQuery(question, Number(id)),
    onSuccess: (res) => {
      setResult(res.data)
      toast.success(`${res.data.row_count} rows returned in ${res.data.execution_time_ms?.toFixed(0)}ms`)
      qc.invalidateQueries(['history', id])
    },
    onError: (err) => {
      const msg = err.response?.data?.error || 'Query failed'
      toast.error(msg)
    },
  })

  const handleSubmit = (q) => {
    const text = q || question
    if (!text.trim()) return
    setResult(null)
    setActiveTab('table')
    queryMut.mutate({ question: text })
  }

  const handleSaveWidget = async (chartType) => {
    if (!result?.query_id) return
    setSaving(true)
    try {
      await createWidget({
        query_id: result.query_id,
        title: question,
        chart_type: chartType,
      })
      toast.success('Widget saved to dashboard!')
      navigate(`/dashboard/${id}`)
    } catch (e) {
      toast.error('Failed to save widget')
    } finally {
      setSaving(false)
    }
  }

  if (dsLoading) {
    return (
      <div className="p-8 flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
        <div className="spinner" /> Loading dataset…
      </div>
    )
  }

  return (
    <div className="p-8 max-w-5xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-xs mb-2" style={{ color: 'var(--text-muted)' }}>
          <span>{dataset?.name}</span>
          <span>·</span>
          <span>{dataset?.row_count?.toLocaleString()} rows</span>
          <span>·</span>
          <span>{dataset?.column_names?.length} columns</span>
        </div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          Ask AI
        </h1>
      </div>

      {/* Schema pill list */}
      <div className="flex flex-wrap gap-2 mb-6">
        {dataset?.column_names?.map((col) => (
          <span
            key={col}
            className="px-2.5 py-1 rounded-full text-xs font-mono"
            style={{ background: 'var(--bg-hover)', color: 'var(--accent-light)', border: '1px solid var(--border)' }}
          >
            {col}
            <span className="ml-1.5 opacity-50">{dataset.column_types?.[col]}</span>
          </span>
        ))}
      </div>

      {/* Question input */}
      <div
        className="rounded-2xl border p-4 mb-4"
        style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}
      >
        <div className="flex gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
            style={{ background: 'var(--accent)' }}
          >
            <Zap size={14} color="white" />
          </div>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit()
              }
            }}
            placeholder="Ask anything about your data… e.g. 'Show top 5 customers by revenue'"
            rows={2}
            className="flex-1 bg-transparent resize-none outline-none text-sm leading-relaxed"
            style={{ color: 'var(--text-primary)' }}
          />
          <button
            onClick={() => handleSubmit()}
            disabled={queryMut.isPending || !question.trim()}
            className="self-end px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-2 transition-all disabled:opacity-40"
            style={{ background: 'var(--accent)', color: 'white' }}
          >
            {queryMut.isPending ? (
              <><div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Running</>
            ) : (
              <><Send size={14} /> Run</>
            )}
          </button>
        </div>
      </div>

      {/* Suggested questions */}
      <div className="flex flex-wrap gap-2 mb-8">
        {SUGGESTED_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => { setQuestion(q); handleSubmit(q) }}
            className="px-3 py-1.5 rounded-full text-xs transition-all hover:opacity-80"
            style={{
              background: 'var(--bg-hover)',
              border: '1px solid var(--border)',
              color: 'var(--text-muted)',
            }}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Loading skeleton */}
      {queryMut.isPending && (
        <div className="rounded-2xl border p-8 text-center animate-pulse" style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}>
          <div className="spinner mx-auto mb-3" style={{ width: 28, height: 28, borderWidth: 3 }} />
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Generating SQL and running query…</p>
        </div>
      )}

      {/* Result */}
      {result && !queryMut.isPending && (
        <div className="animate-slide-up">
          {/* Generated SQL */}
          <div className="mb-4">
            <p className="text-xs font-medium mb-2" style={{ color: 'var(--text-muted)' }}>GENERATED SQL</p>
            <div className="sql-block">{result.generated_sql}</div>
          </div>

          {/* Tabs */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex gap-1">
              {[
                { key: 'table', icon: <Table size={13} />, label: 'Table' },
                { key: 'bar',   icon: <BarChart2 size={13} />, label: 'Bar' },
                { key: 'line',  icon: <TrendingUp size={13} />, label: 'Line' },
                { key: 'pie',   icon: <PieChart size={13} />, label: 'Pie' },
              ].map(({ key, icon, label }) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                  style={{
                    background: activeTab === key ? 'var(--accent)' : 'var(--bg-hover)',
                    color: activeTab === key ? 'white' : 'var(--text-muted)',
                  }}
                >
                  {icon} {label}
                </button>
              ))}
            </div>

            {/* Save to dashboard */}
            <button
              onClick={() => handleSaveWidget(activeTab === 'table' ? 'bar' : activeTab)}
              disabled={saving}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
              style={{ border: '1px solid var(--accent)', color: 'var(--accent-light)', background: 'transparent' }}
            >
              <PlusCircle size={13} />
              {saving ? 'Saving…' : 'Pin to Dashboard'}
            </button>
          </div>

          {/* Table view */}
          {activeTab === 'table' && (
            <ResultTable columns={result.columns} rows={result.rows} />
          )}

          {/* Chart views */}
          {['bar', 'line', 'pie'].includes(activeTab) && (
            <ChartPreview
              chartType={activeTab}
              columns={result.columns}
              rows={result.rows}
            />
          )}

          <p className="text-xs mt-3" style={{ color: 'var(--text-muted)' }}>
            {result.row_count} rows · {result.execution_time_ms?.toFixed(1)}ms
          </p>
        </div>
      )}
    </div>
  )
}
