import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

const COLORS = ['#6366f1', '#34d399', '#fbbf24', '#f87171', '#60a5fa', '#a78bfa', '#f472b6']

const TOOLTIP_STYLE = {
  backgroundColor: '#1e1e28',
  border: '1px solid #2e2e3e',
  borderRadius: '8px',
  color: '#e8e8f0',
  fontFamily: 'DM Sans, sans-serif',
  fontSize: '12px',
}

function pickAxes(columns) {
  // Heuristic: first non-numeric col = X, first numeric = Y
  const numerics = columns.filter((_, i) => i > 0)
  return {
    xKey: columns[0] || 'x',
    yKey: numerics[0] || columns[1] || columns[0] || 'y',
  }
}

function truncateLabel(val, max = 14) {
  const s = String(val ?? '')
  return s.length > max ? s.slice(0, max) + '…' : s
}

export default function ChartPreview({ chartType, columns = [], rows = [], compact = false }) {
  const height = compact ? 200 : 280
  if (!rows.length || !columns.length) {
    return (
      <div
        className="rounded-xl flex items-center justify-center text-sm"
        style={{ height, background: 'var(--bg-hover)', color: 'var(--text-muted)' }}
      >
        No data to chart
      </div>
    )
  }

  const { xKey, yKey } = pickAxes(columns)

  // Prepare data — cap at 50 points for readability
  const data = rows.slice(0, 50).map((r) => ({
    ...r,
    [xKey]: truncateLabel(r[xKey]),
    [yKey]: isNaN(Number(r[yKey])) ? 0 : Number(r[yKey]),
  }))

  const commonProps = {
    data,
    margin: { top: 4, right: 16, bottom: compact ? 20 : 32, left: 8 },
  }

  const axisStyle = { fill: 'var(--text-muted)', fontSize: 11, fontFamily: 'DM Sans' }

  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
    >
      <ResponsiveContainer width="100%" height={height}>
        {chartType === 'bar' ? (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2e2e3e" vertical={false} />
            <XAxis dataKey={xKey} tick={axisStyle} tickLine={false} axisLine={false} interval="preserveStartEnd" />
            <YAxis tick={axisStyle} tickLine={false} axisLine={false} width={48} />
            <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: 'rgba(99,102,241,0.08)' }} />
            <Bar dataKey={yKey} fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={48} />
          </BarChart>
        ) : chartType === 'line' ? (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2e2e3e" vertical={false} />
            <XAxis dataKey={xKey} tick={axisStyle} tickLine={false} axisLine={false} interval="preserveStartEnd" />
            <YAxis tick={axisStyle} tickLine={false} axisLine={false} width={48} />
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            <Line
              type="monotone"
              dataKey={yKey}
              stroke="#6366f1"
              strokeWidth={2.5}
              dot={{ fill: '#6366f1', r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        ) : (
          <PieChart>
            <Pie
              data={data.slice(0, 8)}
              dataKey={yKey}
              nameKey={xKey}
              cx="50%"
              cy="50%"
              outerRadius={compact ? 70 : 100}
              innerRadius={compact ? 28 : 40}
              paddingAngle={3}
              label={!compact ? ({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%` : undefined}
              labelLine={!compact}
            >
              {data.slice(0, 8).map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            {!compact && <Legend wrapperStyle={{ fontSize: 12, color: 'var(--text-muted)' }} />}
          </PieChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}
