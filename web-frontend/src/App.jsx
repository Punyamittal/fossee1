import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom'
import UploadForm from './components/UploadForm'
import DataTable from './components/DataTable'
import SummaryStats from './components/SummaryStats'
import ChartsPanel from './components/ChartsPanel'
import HistoryList from './components/HistoryList'
import Login from './components/Login'
import { getDatasets } from './services/api'

function App() {
  const [datasets, setDatasets] = useState([])
  const [currentDataset, setCurrentDataset] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('accessToken'))
  const [refreshKey, setRefreshKey] = useState(0)

  const refreshDatasets = () => {
    getDatasets()
      .then((res) => setDatasets(res.data))
      .catch(() => setDatasets([]))
  }

  useEffect(() => {
    refreshDatasets()
  }, [refreshKey])

  const onUploadSuccess = (data) => {
    setCurrentDataset(data.dataset_id)
    setRefreshKey((k) => k + 1)
  }

  const onSelectDataset = (id) => setCurrentDataset(id)

  return (
    <BrowserRouter>
      <div style={styles.layout}>
        <header style={styles.header}>
          <h1 style={styles.title}>Chemical Equipment Parameter Visualizer</h1>
          <div style={styles.headerRight}>
            {isAuthenticated ? (
              <button
                style={styles.logoutBtn}
                onClick={() => {
                  localStorage.removeItem('accessToken')
                  localStorage.removeItem('refreshToken')
                  setIsAuthenticated(false)
                }}
              >
                Logout
              </button>
            ) : (
              <a href="/login" style={styles.loginLink}>Login</a>
            )}
          </div>
        </header>

        <div style={styles.main}>
          <aside style={styles.sidebar}>
            <UploadForm onSuccess={onUploadSuccess} />
            <HistoryList
              datasets={datasets}
              currentId={currentDataset}
              onSelect={onSelectDataset}
            />
          </aside>
          <main style={styles.content}>
            <Routes>
              <Route path="/login" element={
                <Login onSuccess={() => setIsAuthenticated(true)} />
              } />
              <Route
                path="/"
                element={
                  currentDataset ? (
                    <Dashboard datasetId={currentDataset} />
                  ) : (
                    <Welcome />
                  )
                }
              />
              <Route path="/dataset/:id" element={
                <DatasetView onSelectDataset={setCurrentDataset} />
              } />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

function Welcome() {
  return (
    <div style={styles.welcome}>
      <p>Upload a CSV file to visualize chemical equipment data.</p>
      <p>CSV columns: Equipment Name, Type, Flowrate, Pressure, Temperature</p>
    </div>
  )
}

function Dashboard({ datasetId }) {
  return (
    <div style={styles.dashboard}>
      <SummaryStats datasetId={datasetId} />
      <ChartsPanel datasetId={datasetId} />
      <DataTable datasetId={datasetId} />
    </div>
  )
}

function DatasetView({ onSelectDataset }) {
  const { id } = useParams()
  const datasetId = id ? parseInt(id, 10) : null
  useEffect(() => {
    if (datasetId) onSelectDataset(datasetId)
  }, [datasetId, onSelectDataset])
  return <Navigate to="/" replace />
}

const styles = {
  layout: { minHeight: '100vh', display: 'flex', flexDirection: 'column' },
  header: {
    background: '#1a1a2e',
    color: '#fff',
    padding: '1rem 1.5rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: { fontSize: '1.25rem', fontWeight: 600 },
  headerRight: { display: 'flex', gap: '1rem' },
  loginLink: { color: '#fff', textDecoration: 'none' },
  logoutBtn: {
    background: 'transparent',
    color: '#fff',
    border: '1px solid rgba(255,255,255,0.5)',
    padding: '0.35rem 0.75rem',
    cursor: 'pointer',
    borderRadius: 4,
  },
  main: { flex: 1, display: 'flex', overflow: 'hidden' },
  sidebar: {
    width: 280,
    background: '#fff',
    borderRight: '1px solid #e0e0e0',
    padding: '1rem',
    overflowY: 'auto',
  },
  content: { flex: 1, padding: '1.5rem', overflowY: 'auto' },
  welcome: { padding: '2rem', color: '#666', lineHeight: 1.8 },
  dashboard: { display: 'flex', flexDirection: 'column', gap: '1.5rem' },
}

export default App
