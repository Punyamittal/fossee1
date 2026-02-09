import { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Line, Pie } from 'react-chartjs-2'
import { getDataset } from '../services/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
  },
}

const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: '1.5rem' },
  title: { fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' },
  chartBox: { height: 280, background: '#fff', padding: '1rem', borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' },
}

export default function ChartsPanel({ datasetId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!datasetId) return
    setLoading(true)
    getDataset(datasetId)
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [datasetId])

  if (loading || !data) return <div>Loading charts...</div>

  const equipment = data.equipment_list || []
  const typeDist = data.type_summaries || []

  const barData = {
    labels: typeDist.map((t) => t.equipment_type),
    datasets: [{
      label: 'Count',
      data: typeDist.map((t) => t.count),
      backgroundColor: 'rgba(37, 99, 235, 0.7)',
      borderColor: 'rgb(37, 99, 235)',
      borderWidth: 1,
    }],
  }

  const lineData = {
    labels: equipment.map((e, i) => e.equipment_name || `#${i + 1}`),
    datasets: [{
      label: 'Flowrate',
      data: equipment.map((e) => parseFloat(e.flowrate)),
      borderColor: 'rgb(34, 197, 94)',
      backgroundColor: 'rgba(34, 197, 94, 0.2)',
      tension: 0.3,
    }],
  }

  const pieData = {
    labels: typeDist.map((t) => t.equipment_type),
    datasets: [{
      data: typeDist.map((t) => t.count),
      backgroundColor: [
        'rgba(37, 99, 235, 0.8)',
        'rgba(34, 197, 94, 0.8)',
        'rgba(234, 179, 8, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(168, 85, 247, 0.8)',
        'rgba(236, 72, 153, 0.8)',
      ],
      borderWidth: 1,
    }],
  }

  return (
    <div style={styles.container}>
      <div style={styles.title}>Charts</div>
      <div style={styles.grid}>
        <div style={styles.chartBox}>
          <div style={{ marginBottom: 8 }}>Equipment Type Distribution</div>
          <Bar data={barData} options={chartOptions} />
        </div>
        <div style={styles.chartBox}>
          <div style={{ marginBottom: 8 }}>Flowrate Trends</div>
          <Line data={lineData} options={chartOptions} />
        </div>
        <div style={styles.chartBox}>
          <div style={{ marginBottom: 8 }}>Type Percentages</div>
          <Pie data={pieData} options={chartOptions} />
        </div>
      </div>
    </div>
  )
}
