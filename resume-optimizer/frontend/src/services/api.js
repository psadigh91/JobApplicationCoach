import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

const api = {
  // Session endpoints
  createSession: async () => {
    const response = await apiClient.post('/sessions')
    return response.data
  },

  getSession: async (sessionId) => {
    const response = await apiClient.get(`/sessions/${sessionId}`)
    return response.data
  },

  updateSessionStep: async (sessionId, step) => {
    const response = await apiClient.put(`/sessions/${sessionId}/step`, { step })
    return response.data
  },

  // Upload endpoints
  uploadFile: async (sessionId, type, file) => {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('file', file)

    const endpoint = type === 'resume' ? '/upload/resume' : '/upload/cover-letter'
    const response = await apiClient.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  uploadJobPostingText: async (sessionId, text) => {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('text', text)

    const response = await apiClient.post('/upload/job-posting', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  uploadJobPostingFile: async (sessionId, file) => {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('file', file)

    const response = await apiClient.post('/upload/job-posting', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  scrapeJobPostingUrl: async (sessionId, url) => {
    const response = await apiClient.post('/upload/job-posting-url', {
      session_id: sessionId,
      url: url
    })
    return response.data
  },

  // LinkedIn endpoints
  scrapeLinkedIn: async (sessionId, linkedinUrl) => {
    const response = await apiClient.post('/linkedin/scrape', {
      session_id: sessionId,
      linkedin_url: linkedinUrl
    })
    return response.data
  },

  uploadLinkedInPDF: async (sessionId, file) => {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('file', file)

    const response = await apiClient.post('/linkedin/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  getLinkedInData: async (sessionId) => {
    const response = await apiClient.get(`/linkedin/${sessionId}`)
    return response.data
  },

  // Company endpoints
  startCompanyCrawl: async (sessionId, companyName, companyWebsite) => {
    const response = await apiClient.post('/company/crawl', {
      session_id: sessionId,
      company_name: companyName,
      company_website: companyWebsite,
      max_pages: 10
    })
    return response.data
  },

  getCompanyData: async (sessionId) => {
    const response = await apiClient.get(`/company/${sessionId}`)
    return response.data
  },

  // Analysis endpoints
  startAnalysis: async (sessionId) => {
    const response = await apiClient.post('/analyze/start', {
      session_id: sessionId
    })
    return response.data
  },

  getScorecard: async (sessionId) => {
    const response = await apiClient.get(`/analyze/${sessionId}/scorecard`)
    return response.data
  },

  getGaps: async (sessionId) => {
    const response = await apiClient.get(`/analyze/${sessionId}/gaps`)
    return response.data
  },

  getMatches: async (sessionId) => {
    const response = await apiClient.get(`/analyze/${sessionId}/matches`)
    return response.data
  },

  getImprovements: async (sessionId) => {
    const response = await apiClient.get(`/analyze/${sessionId}/improvements`)
    return response.data
  },

  // Resume endpoints
  generateResumes: async (sessionId) => {
    const response = await apiClient.post('/resume/generate', {
      session_id: sessionId
    })
    return response.data
  },

  getResumeVersion: async (versionId) => {
    const response = await apiClient.get(`/resume/${versionId}`)
    return response.data
  },

  getSessionResumes: async (sessionId) => {
    const response = await apiClient.get(`/resume/session/${sessionId}`)
    return response.data
  },

  updateResume: async (versionId, content) => {
    const response = await apiClient.put(`/resume/${versionId}`, { content })
    return response.data
  },

  getResumeDiff: async (versionId) => {
    const response = await apiClient.get(`/resume/${versionId}/diff`)
    return response.data
  },

  approveResume: async (versionId) => {
    const response = await apiClient.post(`/resume/${versionId}/approve`)
    return response.data
  },

  // Study guide endpoints
  generateStudyGuide: async (sessionId) => {
    const response = await apiClient.post('/study/generate', {
      session_id: sessionId,
      timeline: '3 months'
    })
    return response.data
  },

  getStudyGuide: async (sessionId) => {
    const response = await apiClient.get(`/study/${sessionId}`)
    return response.data
  },

  // Export endpoints
  exportToPDF: async (sessionId, versionId) => {
    const response = await apiClient.post('/export/pdf', {
      session_id: sessionId,
      version_id: versionId
    })
    return response.data
  },

  exportToHTML: async (sessionId, versionId) => {
    const response = await apiClient.post('/export/html', {
      session_id: sessionId,
      version_id: versionId
    })
    return response.data
  },

  downloadExport: (filename) => {
    return `${API_BASE_URL}/export/download/${filename}`
  }
}

export default api
