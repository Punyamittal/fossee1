import { useState, useEffect } from 'react'
import { getDataset } from '../services/api'

const styles = {
  container: { background: '#fff', borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)', overflow: 'hidden' },
  header: { padding: '1rem', borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' },
  title: { fontSize: '1rem', fontWeight: 600 },
  input: {
    padding: '0.4rem 0.75rem',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    minWidth: 200,
    fontSize: '0.9rem',
  },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' },
  th: {
    padding: '0.75rem 1rem',
    textAlign: 'left',
    background: '#f8fafc',
    fontWeight: 600,
    color: '#475569',
    borderBottom: '1px solid #e5e7eb',
  },
  td: { padding: '0.75rem 1rem', borderBottom: '1px solid #f1f5f9' },
  trHover: { background: '#f8fafc' },
  pagination: { padding: '0.75rem 1rem', display: 'flex', gap: '0.5rem', alignItems: 'center', borderTop: '1px solid #e5e7eb' },
  pageBtn: {
    padding: '0.35rem 0.75rem',
    border: '1px solid #d1d5db',
    background: '#fff',
    borderRadius: 4,
    cursor: 'pointer',
    fontSize: '0.85rem',
  },
}

export default function DataTable({ datasetId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [sortKey, setSortKey] = useState(null)
  const [sortDir, setSortDir] = useState(1)

  useEffect(() => {
    if (!datasetId) return
    setLoading(true)
    getDataset(datasetId)
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [datasetId])

  if (loading || !data) return <div>Loading table...</div>

  let equipment = [...(data.equipment_list || [])]

  if (filter) {
    const f = filter.toLowerCase()
    equipment = equipment.filter(
      (e) =>
        String(e.equipment_name || '').toLowerCase().includes(f) ||
        String(e.equipment_type || '').toLowerCase().includes(f)
    )
  }

  if (sortKey) {
    equipment.sort((a, b) => {
      const va = a[sortKey]
      const vb = b[sortKey]
      const numA = parseFloat(va)
      const numB = parseFloat(vb)
      if (!isNaN(numA) && !isNaN(numB)) return (numA - numB) * sortDir
      return String(va).localeCompare(String(vb)) * sortDir
    })
  }

  const toggleSort = (key) => {
    setSortKey(key)
    setSortDir((d) => (sortKey === key ? -d : 1))
  }

  const SortHeader = ({ label, keyName }) => (
    <th style={{ ...styles.th, cursor: 'pointer' }} onClick={() => toggleSort(keyName)}>
      {label} {sortKey === keyName && (sortDir > 0 ? '↑' : '↓')}
    </th>
  )

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <span style={styles.title}>Equipment Data</span>
        <input
          type="text"
          placeholder="Search..."
          style={styles.input}
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
      </div>
      <div style={{ overflowX: 'auto', maxHeight: 400, overflowY: 'auto' }}>
        <table style={styles.table}>
          <thead>
            <tr>
              <SortHeader label="Name" keyName="equipment_name" />
              <SortHeader label="Type" keyName="equipment_type" />
              <SortHeader label="Flowrate" keyName="flowrate" />
              <SortHeader label="Pressure" keyName="pressure" />
              <SortHeader label="Temperature" keyName="temperature" />
            </tr>
          </thead>
          <tbody>
            {equipment.map((e, i) => (
              <tr key={e.id || i} style={styles.trHover}>
                <td style={styles.td}>{e.equipment_name}</td>
                <td style={styles.td}>{e.equipment_type}</td>
                <td style={styles.td}>{e.flowrate}</td>
                <td style={styles.td}>{e.pressure}</td>
                <td style={styles.td}>{e.temperature}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
