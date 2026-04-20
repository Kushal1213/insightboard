export default function ResultTable({ columns = [], rows = [] }) {
  if (!rows.length) {
    return (
      <div
        className="rounded-xl border p-8 text-center text-sm"
        style={{ borderColor: 'var(--border)', color: 'var(--text-muted)', background: 'var(--bg-secondary)' }}
      >
        No results returned.
      </div>
    )
  }

  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
    >
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr style={{ background: 'var(--bg-hover)' }}>
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-3 text-left font-medium text-xs uppercase tracking-wider whitespace-nowrap"
                  style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={i}
                className="transition-colors"
                style={{ borderBottom: '1px solid var(--border)' }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                {columns.map((col) => (
                  <td
                    key={col}
                    className="px-4 py-2.5 font-mono text-xs whitespace-nowrap max-w-xs truncate"
                    style={{ color: 'var(--text-primary)' }}
                    title={String(row[col] ?? '')}
                  >
                    {row[col] === null || row[col] === undefined
                      ? <span style={{ color: 'var(--text-muted)' }}>null</span>
                      : String(row[col])
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div
        className="px-4 py-2 text-xs border-t"
        style={{ borderColor: 'var(--border)', color: 'var(--text-muted)', background: 'var(--bg-hover)' }}
      >
        {rows.length} row{rows.length !== 1 ? 's' : ''}
      </div>
    </div>
  )
}
