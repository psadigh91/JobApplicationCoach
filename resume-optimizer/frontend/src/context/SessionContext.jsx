import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const SessionContext = createContext()

export function useSession() {
  const context = useContext(SessionContext)
  if (!context) {
    throw new Error('useSession must be used within SessionProvider')
  }
  return context
}

export function SessionProvider({ children }) {
  const [sessionId, setSessionId] = useState(null)
  const [currentStep, setCurrentStep] = useState(1)
  const [uploads, setUploads] = useState({
    resume: null,
    coverLetter: null,
    jobPosting: null
  })
  const [linkedInData, setLinkedInData] = useState(null)
  const [companyData, setCompanyData] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [resumes, setResumes] = useState({
    tactical: null,
    extrapolated: null
  })
  const [studyGuide, setStudyGuide] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Initialize session on mount
  useEffect(() => {
    initializeSession()
  }, [])

  const initializeSession = async () => {
    try {
      setLoading(true)
      const response = await api.createSession()
      setSessionId(response.id)
      setError(null)
    } catch (err) {
      setError('Failed to initialize session')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const updateStep = async (step) => {
    if (!sessionId) return

    try {
      await api.updateSessionStep(sessionId, step)
      setCurrentStep(step)
    } catch (err) {
      console.error('Failed to update step:', err)
    }
  }

  const uploadFile = async (type, file) => {
    if (!sessionId) throw new Error('No session ID')

    setLoading(true)
    setError(null)

    try {
      const response = await api.uploadFile(sessionId, type, file)
      setUploads(prev => ({
        ...prev,
        [type]: response
      }))
      return response
    } catch (err) {
      setError(`Failed to upload ${type}`)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const uploadJobPosting = async (textOrUrl, isUrl = false) => {
    if (!sessionId) throw new Error('No session ID')

    setLoading(true)
    setError(null)

    try {
      const response = isUrl
        ? await api.scrapeJobPostingUrl(sessionId, textOrUrl)
        : await api.uploadJobPostingText(sessionId, textOrUrl)
      setUploads(prev => ({
        ...prev,
        jobPosting: response
      }))
      return response
    } catch (err) {
      setError(isUrl ? 'Failed to scrape job posting URL' : 'Failed to upload job posting')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const scrapeLinkedIn = async (url) => {
    if (!sessionId) throw new Error('No session ID')

    setLoading(true)
    try {
      const response = await api.scrapeLinkedIn(sessionId, url)
      setLinkedInData(response)
      return response
    } catch (err) {
      setError('Failed to scrape LinkedIn')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const uploadLinkedInPDF = async (file) => {
    if (!sessionId) throw new Error('No session ID')

    setLoading(true)
    try {
      const response = await api.uploadLinkedInPDF(sessionId, file)
      setLinkedInData(response)
      return response
    } catch (err) {
      setError('Failed to upload LinkedIn PDF')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const crawlCompany = async (companyName, website) => {
    if (!sessionId) throw new Error('No session ID')

    setLoading(true)
    try {
      const response = await api.startCompanyCrawl(sessionId, companyName, website)
      setCompanyData(response)
      return response
    } catch (err) {
      setError('Failed to crawl company website')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const startAnalysis = async () => {
    if (!sessionId) throw new Error('No session ID')

    setLoading(true)
    try {
      const response = await api.startAnalysis(sessionId)
      setAnalysis(response)

      // Poll for completion
      const pollInterval = setInterval(async () => {
        const scorecard = await api.getScorecard(sessionId)
        if (scorecard.analysis_status === 'completed') {
          setAnalysis(scorecard)
          clearInterval(pollInterval)
          setLoading(false)
        } else if (scorecard.analysis_status === 'failed') {
          clearInterval(pollInterval)
          setLoading(false)
          setError('Analysis failed')
        }
      }, 5000) // Poll every 5 seconds

      return response
    } catch (err) {
      setError('Failed to start analysis')
      setLoading(false)
      throw err
    }
  }

  const generateResumes = async () => {
    if (!sessionId) throw new Error('No session ID')

    setLoading(true)
    try {
      await api.generateResumes(sessionId)

      // Poll for completion
      const pollInterval = setInterval(async () => {
        const versions = await api.getSessionResumes(sessionId)
        const tactical = versions.versions.find(v => v.version_type === 'tactical')
        const extrapolated = versions.versions.find(v => v.version_type === 'extrapolated')

        if (tactical?.generation_status === 'completed' && extrapolated?.generation_status === 'completed') {
          const tacticalData = await api.getResumeVersion(tactical.version_id)
          const extrapolatedData = await api.getResumeVersion(extrapolated.version_id)

          setResumes({
            tactical: tacticalData,
            extrapolated: extrapolatedData
          })

          clearInterval(pollInterval)
          setLoading(false)
        }
      }, 5000)

    } catch (err) {
      setError('Failed to generate resumes')
      setLoading(false)
      throw err
    }
  }

  const generateStudyGuide = async () => {
    if (!sessionId) throw new Error('No session ID')

    setLoading(true)
    try {
      await api.generateStudyGuide(sessionId)

      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const guide = await api.getStudyGuide(sessionId)
          setStudyGuide(guide)
          clearInterval(pollInterval)
          setLoading(false)
        } catch (err) {
          // Still generating
        }
      }, 5000)

    } catch (err) {
      setError('Failed to generate study guide')
      setLoading(false)
      throw err
    }
  }

  const value = {
    sessionId,
    currentStep,
    uploads,
    linkedInData,
    companyData,
    analysis,
    resumes,
    studyGuide,
    loading,
    error,
    updateStep,
    uploadFile,
    uploadJobPosting,
    scrapeLinkedIn,
    uploadLinkedInPDF,
    crawlCompany,
    startAnalysis,
    generateResumes,
    generateStudyGuide,
    setError
  }

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  )
}
