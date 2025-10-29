import axios from 'axios'

const API_BASE = 'https://docuverse-o7b1.onrender.com'
// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Auth endpoints
export const signup = async (username, password) => {
  const response = await api.post('/signup', { username, password })
  return response.data
}

export const login = async (username, password) => {
  const response = await api.post('/login', { username, password })
  return response.data
}

// File upload
export const uploadFile = async (file, userId, token) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('user_id', String(userId))  // Convert to string for FormData

  const response = await axios.post(`${API_BASE}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      'Authorization': `Bearer ${token}`
    }
  })
  return response.data
}

// Ask question with user_id for document access
export const askQuestion = async (question, userId, token) => {
  const formData = new FormData()
  formData.append('question', question)
  formData.append('user_id', String(userId))

  const response = await axios.post(`${API_BASE}/ask`, formData, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  return response.data
}

// Summarize specific document
export const summarizeDocument = async (userId, docId, token) => {
  const formData = new FormData()
  formData.append('user_id', String(userId))
  formData.append('doc_id', String(docId))

  const response = await axios.post(`${API_BASE}/summarize`, formData, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  return response.data
}

// Get user documents
export const getUserDocuments = async (userId, token) => {
  const response = await axios.get(`${API_BASE}/documents/${userId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  return response.data
}

export default api

