import { useState, useEffect } from 'react'
import { getDatasetSummary, generatePDF } from '../services/api'

const styles = {
  row: { display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' },
  card: {
    flex: '1 1 140px',
    minWidth: 140,
    background: '#fff',
    padding: '1rem 1.25rem',
    borderRadius: 8,
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
    border: '1px solid #e5e7eb',
  },
  label: { fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 },
  value: { fontSize: '1.25rem', fontWeight: 700, color: '#1a1a2e' },
  pdfBtn: {
    padding: '0.5rem 1rem',
    background: '#dc2626',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
    fontWeight: 600,
    fontSize: '0.9rem',
  },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' },
  title: { fontSize: '1.1rem', fontWeight: 600 },
  loading: { color: '#64748b' },
}

export default function SummaryStats({ datasetId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [pdfLoading, setPdfLoading] = useState(false)

  useEffect(() => {
    if (!datasetId) return
    setLoading(true)
    getDatasetSummary(datasetId)
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [datasetId])

  const handleDownloadPDF = async () => {
    if (!datasetId) return
    setPdfLoading(true)
    try {
      const res = await generatePDF(datasetId)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `report_dataset_${datasetId}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      alert(err.response?.data?.detail || 'PDF generation failed')
    } finally {
      setPdfLoading(false)
    }
  }

  if (loading) return <div style={styles.loading}>Loading summary...</div>
  if (!data) return null

  return (
    <div>
      <div style={styles.header}>
        <span style={styles.title}>Summary Statistics</span>
        <button
          style={styles.pdfBtn}
          onClick={handleDownloadPDF}
          disabled={pdfLoading}
        >
          {pdfLoading ? 'Generating...' : 'Download PDF Report'}
        </button>
      </div>
      <div style={styles.row}>
        <div style={styles.card}>
          <div style={styles.label}>Total Count</div>
          <div style={styles.value}>{data.total_count}</div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Avg Flowrate</div>
          <div style={styles.value}>{data.avg_flowrate != null ? data.avg_flowrate.toFixed(2) : '—'}</div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Avg Pressure</div>
          <div style={styles.value}>{data.avg_pressure != null ? data.avg_pressure.toFixed(2) : '—'}</div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Avg Temperature</div>
          <div style={styles.value}>{data.avg_temperature != null ? data.avg_temperature.toFixed(2) : '—'}</div>
        </div>
      </div>
    </div>
  )
}
