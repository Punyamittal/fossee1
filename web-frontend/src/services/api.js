import axios from 'axios'

const API_BASE = '/api'
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
