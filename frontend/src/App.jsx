import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import DatasetPage from './pages/DatasetPage'
import DashboardPage from './pages/DashboardPage'
import HistoryPage from './pages/HistoryPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="/dataset/:id" element={<DatasetPage />} />
        <Route path="/dashboard/:id" element={<DashboardPage />} />
        <Route path="/history/:id" element={<HistoryPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
