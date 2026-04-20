import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Upload, Database, Trash2, ChevronRight, FileText, BarChart2 } from 'lucide-react'
import { uploadDataset, fetchDatasets, deleteDataset } from '../services/api'

export default function HomePage() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [uploading, setUploading] = useState(false)

  const { data: datasets = [], isLoading } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => fetchDatasets().then(r => r.data),
  })

  const uploadMut = useMutation({
    mutationFn: (file) => uploadDataset(file),
    onSuccess: (res) => {
      qc.invalidateQueries(['datasets'])
      toast.success(`"${res.data.name}" uploaded — ${res.data.row_count.toLocaleString()} rows`)
      navigate(`/dataset/${res.data.id}`)
    },
    onError: (err) => {
      toast.error(err.response?.data?.error || 'Upload failed')
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id) => deleteDataset(id),
    onSuccess: () => {
      qc.invalidateQueries(['datasets'])
      toast.success('Dataset deleted')
    },
  })

  const onDrop = useCallback((accepted) => {
    if (accepted.length === 0) return
    uploadMut.mutate(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    multiple: false,
    disabled: uploadMut.isPending,
  })

  return (
    <div className="p-8 max-w-4xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
          Datasets
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Upload a CSV file to start querying it with natural language.
        </p>
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className="relative rounded-2xl border-2 border-dashed p-12 text-center cursor-pointer transition-all duration-200 mb-10 overflow-hidden"
        style={{
          borderColor: isDragActive ? 'var(--accent)' : 'var(--border)',
          background: isDragActive ? 'rgba(99,102,241,0.06)' : 'var(--bg-secondary)',
        }}
      >
        <input {...getInputProps()} />

        {uploadMut.isPending ? (
          <div className="flex flex-col items-center gap-3">
            <div className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
            <p style={{ color: 'var(--text-muted)' }}>Processing CSV…</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center mb-1"
              style={{ background: isDragActive ? 'var(--accent)' : 'var(--bg-hover)' }}
            >
              <Upload size={22} color={isDragActive ? 'white' : 'var(--accent-light)'} />
            </div>
            <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
              {isDragActive ? 'Drop it here' : 'Drop CSV file here'}
            </p>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              or <span style={{ color: 'var(--accent-light)' }}>click to browse</span> — max 16 MB, 50 000 rows
            </p>
          </div>
        )}
      </div>

      {/* Dataset list */}
      <div>
        <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Your Datasets
        </h2>

        {isLoading && (
          <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
            <div className="spinner" /> Loading…
          </div>
        )}

        {!isLoading && datasets.length === 0 && (
          <div
            className="rounded-xl border p-8 text-center"
            style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
          >
            <Database size={32} className="mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
            <p style={{ color: 'var(--text-muted)' }}>No datasets yet. Upload a CSV above.</p>
          </div>
        )}

        <div className="flex flex-col gap-3">
          {datasets.map((ds) => (
            <div
              key={ds.id}
              className="group rounded-xl border p-4 flex items-center justify-between cursor-pointer transition-all hover:border-indigo-500/40"
              style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
              onClick={() => navigate(`/dataset/${ds.id}`)}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ background: 'var(--bg-hover)' }}
                >
                  <FileText size={18} style={{ color: 'var(--accent-light)' }} />
                </div>
                <div>
                  <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                    {ds.name}
                  </p>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    {ds.row_count.toLocaleString()} rows · {ds.column_names.length} columns ·{' '}
                    {new Date(ds.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  className="p-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:text-red-400"
                  style={{ color: 'var(--text-muted)' }}
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteMut.mutate(ds.id)
                  }}
                >
                  <Trash2 size={15} />
                </button>
                <ChevronRight size={16} style={{ color: 'var(--text-muted)' }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
