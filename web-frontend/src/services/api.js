import axios from 'axios'

// In production (Netlify), set VITE_API_URL to your Render API base, e.g. https://fossee1-1.onrender.com/api
let API_BASE = import.meta.env.VITE_API_URL || '/api'
// Ensure base ends with /api so paths like /datasets/ become .../api/datasets/
if (API_BASE.startsWith('http') && !API_BASE.endsWith('/api')) {
  API_BASE = API_BASE.replace(/\/?$/, '') + '/api'
}
const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const uploadCSV = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getDatasets = () => api.get('/datasets/')
export const getDataset = (id) => api.get(`/datasets/${id}/`)
export const getDatasetSummary = (id) => api.get(`/datasets/${id}/summary/`)
export const getEquipment = (id, page = 1) => api.get(`/datasets/${id}/equipment/?page=${page}`)
export const generatePDF = (id) =>
  api.post(`/datasets/${id}/generate-pdf/`, {}, { responseType: 'blob' })

export const login = (username, password) =>
  api.post('/auth/login/', { username, password })

export const register = (username, password, email = '') =>
  api.post('/auth/register/', { username, password, email })
