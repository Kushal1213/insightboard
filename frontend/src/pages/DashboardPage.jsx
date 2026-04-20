import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { LayoutDashboard, Trash2, Zap, BarChart2 } from 'lucide-react'
import { fetchDashboard, deleteWidget } from '../services/api'
import ChartPreview from '../components/charts/ChartPreview'

export default function DashboardPage() {
  const { id } = useParams()
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', id],
    queryFn: () => fetchDashboard(id).then(r => r.data),
    refetchInterval: 15_000,
  })

  const deleteMut = useMutation({
    mutationFn: (widgetId) => deleteWidget(widgetId),
    onSuccess: () => {
      qc.invalidateQueries(['dashboard', id])
      toast.success('Widget removed')
    },
  })

  if (isLoading) {
    return (
      <div className="p-8 flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
        <div className="spinner" /> Loading dashboard…
      </div>
    )
  }

  const widgets = data?.widgets || []

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <LayoutDashboard size={18} style={{ color: 'var(--accent-light)' }} />
            <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {data?.dataset_name}
            </h1>
          </div>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            {widgets.length} widget{widgets.length !== 1 ? 's' : ''}
          </p>
        </div>
        <Link
          to={`/dataset/${id}`}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all"
          style={{ background: 'var(--accent)', color: 'white' }}
        >
          <Zap size={14} /> Ask AI
        </Link>
      </div>

      {/* Empty state */}
      {widgets.length === 0 && (
        <div
          className="rounded-2xl border p-16 text-center"
          style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
        >
          <BarChart2 size={40} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
          <p className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>No widgets yet</p>
          <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>
            Run a query and click "Pin to Dashboard" to add charts here.
          </p>
          <Link
            to={`/dataset/${id}`}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium"
            style={{ background: 'var(--accent)', color: 'white' }}
          >
            <Zap size={14} /> Ask AI now
          </Link>
        </div>
      )}

      {/* Widget grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {widgets.map((widget) => (
          <div
            key={widget.id}
            className="group rounded-2xl border p-5 relative transition-all hover:border-indigo-500/30"
            style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}
          >
            {/* Widget header */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="font-medium text-sm leading-snug" style={{ color: 'var(--text-primary)' }}>
                  {widget.title}
                </p>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                  {widget.chart_type} · {widget.data_snapshot?.length || 0} rows
                </p>
              </div>
              <button
                onClick={() => deleteMut.mutate(widget.id)}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg hover:bg-red-500/10 hover:text-red-400"
                style={{ color: 'var(--text-muted)' }}
              >
                <Trash2 size={14} />
              </button>
            </div>

            {/* Chart */}
            {widget.data_snapshot?.length > 0 ? (
              <ChartPreview
                chartType={widget.chart_type === 'table' ? 'bar' : widget.chart_type}
                columns={Object.keys(widget.data_snapshot[0] || {})}
                rows={widget.data_snapshot}
                compact
              />
            ) : (
              <div
                className="h-40 rounded-xl flex items-center justify-center"
                style={{ background: 'var(--bg-hover)', color: 'var(--text-muted)' }}
              >
                No data
              </div>
            )}

            <p className="text-xs mt-3" style={{ color: 'var(--text-muted)' }}>
              {new Date(widget.created_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
