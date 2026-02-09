import { useState } from 'react'
import { uploadCSV } from '../services/api'

const styles = {
  form: { marginBottom: '1.5rem' },
  label: { display: 'block', fontWeight: 600, marginBottom: '0.5rem', fontSize: '0.9rem' },
  input: { display: 'block', width: '100%', marginBottom: '0.75rem' },
  btn: {
    width: '100%',
    padding: '0.6rem 1rem',
    background: '#2563eb',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
    fontWeight: 600,
    fontSize: '0.9rem',
  },
  btnDisabled: { opacity: 0.6, cursor: 'not-allowed' },
  spinner: { display: 'inline-block', width: 16, height: 16, marginRight: 8, border: '2px solid #fff', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' },
  message: { marginTop: '0.75rem', padding: '0.5rem', borderRadius: 4, fontSize: '0.85rem' },
  success: { background: '#d1fae5', color: '#065f46' },
  error: { background: '#fee2e2', color: '#991b1b' },
}

export default function UploadForm({ onSuccess }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [isError, setIsError] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setMessage('Please select a CSV file')
      setIsError(true)
      return
    }
    setLoading(true)
    setMessage(null)
    setIsError(false)
    try {
      const res = await uploadCSV(file)
      setMessage(`Uploaded: ${res.data.filename} (${res.data.total_equipment_count} equipment)`)
      setIsError(false)
      onSuccess?.(res.data)
    } catch (err) {
      const msg = err.response?.data?.error || err.message || 'Upload failed'
      setMessage(msg)
      setIsError(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form style={styles.form} onSubmit={handleSubmit}>
      <label style={styles.label}>Upload CSV</label>
      <input
        type="file"
        accept=".csv"
        style={styles.input}
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        disabled={loading}
      />
      <button
        type="submit"
        style={{ ...styles.btn, ...(loading ? styles.btnDisabled : {}) }}
        disabled={loading}
      >
        {loading && (
          <span style={styles.spinner} />
        )}
        {loading ? 'Uploading...' : 'Upload'}
      </button>
      {message && (
        <div style={{ ...styles.message, ...(isError ? styles.error : styles.success) }}>
          {message}
        </div>
      )}
    </form>
  )
}

