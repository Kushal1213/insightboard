import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Datasets ───────────────────────────────────────────────────────────────────

export const uploadDataset = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const fetchDatasets = () => api.get('/datasets')
export const fetchDataset  = (id) => api.get(`/datasets/${id}`)
export const deleteDataset = (id) => api.delete(`/datasets/${id}`)

// ── Queries ────────────────────────────────────────────────────────────────────

export const runQuery = (question, dataset_id) =>
  api.post('/query', { question, dataset_id })

export const fetchHistory = (datasetId, limit = 50) =>
  api.get(`/datasets/${datasetId}/history`, { params: { limit } })

// ── Dashboard / Widgets ────────────────────────────────────────────────────────

export const fetchDashboard = (datasetId) =>
  api.get(`/dashboard/${datasetId}`)

export const createWidget = (payload) => api.post('/widgets', payload)
export const deleteWidget  = (id)      => api.delete(`/widgets/${id}`)

export const reorderWidgets = (datasetId, orderedIds) =>
  api.put(`/dashboard/${datasetId}/reorder`, { ordered_ids: orderedIds })

export default api
