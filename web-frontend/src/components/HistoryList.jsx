const styles = {
  section: { marginTop: '1rem' },
  title: { fontWeight: 600, marginBottom: '0.5rem', fontSize: '0.9rem' },
  list: { listStyle: 'none' },
  item: {
    padding: '0.5rem 0.75rem',
    marginBottom: '0.35rem',
    background: '#f8fafc',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: '0.85rem',
    border: '1px solid transparent',
  },
  itemActive: { background: '#dbeafe', borderColor: '#2563eb' },
  empty: { color: '#64748b', fontSize: '0.85rem', padding: '0.5rem 0' },
}

export default function HistoryList({ datasets, currentId, onSelect }) {
  if (!datasets?.length) {
    return (
      <div style={styles.section}>
        <div style={styles.title}>History</div>
        <div style={styles.empty}>No datasets yet</div>
      </div>
    )
  }

  return (
    <div style={styles.section}>
      <div style={styles.title}>Recent Datasets (last 5)</div>
      <ul style={styles.list}>
        {datasets.map((d) => (
          <li
            key={d.id}
            style={{
              ...styles.item,
              ...(d.id === currentId ? styles.itemActive : {}),
            }}
            onClick={() => onSelect(d.id)}
          >
            <div style={{ fontWeight: 500 }}>{d.filename}</div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: 2 }}>
              {new Date(d.upload_timestamp).toLocaleString()} · {d.total_equipment_count} equipment
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
