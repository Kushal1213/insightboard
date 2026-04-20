import { Outlet, NavLink, useParams, useLocation } from 'react-router-dom'
import { BarChart2, Upload, Clock, LayoutDashboard, Zap } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { fetchDatasets } from '../../services/api'

export default function Layout() {
  const location = useLocation()
  const { data } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => fetchDatasets().then(r => r.data),
    refetchInterval: 10_000,
  })
  const datasets = data || []

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* ── Sidebar ── */}
      <aside
        className="w-60 flex-shrink-0 flex flex-col border-r"
        style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}
      >
        {/* Logo */}
        <div className="px-5 py-5 border-b" style={{ borderColor: 'var(--border)' }}>
          <div className="flex items-center gap-2.5">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center glow-sm"
              style={{ background: 'var(--accent)' }}
            >
              <BarChart2 size={16} color="white" />
            </div>
            <div>
              <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>InsightBoard</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>AI Analytics</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 overflow-y-auto">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm mb-1 transition-all ${
                isActive
                  ? 'text-white font-medium'
                  : 'hover:text-white'
              }`
            }
            style={({ isActive }) => ({
              background: isActive ? 'var(--accent)' : 'transparent',
              color: isActive ? 'white' : 'var(--text-muted)',
            })}
          >
            <Upload size={15} />
            Datasets
          </NavLink>

          {/* Per-dataset links */}
          {datasets.map((ds) => (
            <div key={ds.id} className="mt-3">
              <p
                className="px-3 text-xs font-medium uppercase tracking-widest mb-1 truncate"
                style={{ color: 'var(--text-muted)' }}
                title={ds.name}
              >
                {ds.name}
              </p>
              <NavLink
                to={`/dataset/${ds.id}`}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs mb-0.5 transition-all ${
                    isActive ? 'text-white' : ''
                  }`
                }
                style={({ isActive }) => ({
                  background: isActive ? 'var(--bg-hover)' : 'transparent',
                  color: isActive ? 'var(--accent-light)' : 'var(--text-muted)',
                })}
              >
                <Zap size={13} /> Ask AI
              </NavLink>
              <NavLink
                to={`/dashboard/${ds.id}`}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs mb-0.5 transition-all`
                }
                style={({ isActive }) => ({
                  background: isActive ? 'var(--bg-hover)' : 'transparent',
                  color: isActive ? 'var(--accent-light)' : 'var(--text-muted)',
                })}
              >
                <LayoutDashboard size={13} /> Dashboard
              </NavLink>
              <NavLink
                to={`/history/${ds.id}`}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs mb-0.5 transition-all`
                }
                style={({ isActive }) => ({
                  background: isActive ? 'var(--bg-hover)' : 'transparent',
                  color: isActive ? 'var(--accent-light)' : 'var(--text-muted)',
                })}
              >
                <Clock size={13} /> History
              </NavLink>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-5 py-3 border-t text-xs" style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
          Powered by Claude AI
        </div>
      </aside>

      {/* ── Main content ── */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
