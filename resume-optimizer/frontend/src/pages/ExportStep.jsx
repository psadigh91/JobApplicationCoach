import React, { useState } from 'react'
import { useSession } from '../context/SessionContext'
import { Download, FileText, Code, CheckCircle, ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function ExportStep() {
  const navigate = useNavigate()
  const { sessionId, resumes } = useSession()
  const [exporting, setExporting] = useState(false)
  const [exportedFiles, setExportedFiles] = useState([])

  const handleExport = async (versionId, format) => {
    try {
      setExporting(true)

      const response = format === 'pdf'
        ? await api.exportToPDF(sessionId, versionId)
        : await api.exportToHTML(sessionId, versionId)

      setExportedFiles(prev => [...prev, {
        format,
        filename: response.filename,
        downloadUrl: response.download_url
      }])
    } catch (err) {
      console.error('Export failed:', err)
      alert('Export failed. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  const handleDownload = (downloadUrl, filename) => {
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Export Your Results</h2>
        <p className="mt-2 text-gray-600">
          Download your optimized resumes and analysis report in your preferred format.
        </p>
      </div>

      {/* Export Options */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tactical Resume */}
        {resumes.tactical && (
          <div className="card">
            <div className="flex items-center mb-4">
              <FileText className="w-6 h-6 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold">Tactical Resume</h3>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Your resume with truthful, verified improvements.
            </p>

            <div className="space-y-2">
              <button
                onClick={() => handleExport(resumes.tactical.version_id, 'pdf')}
                disabled={exporting}
                className="btn-primary w-full flex items-center justify-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Export as PDF
              </button>

              <button
                onClick={() => handleExport(resumes.tactical.version_id, 'html')}
                disabled={exporting}
                className="btn-secondary w-full flex items-center justify-center"
              >
                <Code className="w-4 h-4 mr-2" />
                Export as HTML
              </button>
            </div>
          </div>
        )}

        {/* Extrapolated Resume */}
        {resumes.extrapolated && (
          <div className="card">
            <div className="flex items-center mb-4">
              <FileText className="w-6 h-6 text-purple-600 mr-2" />
              <h3 className="text-lg font-semibold">Extrapolated Resume</h3>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Your resume with 3-month growth projections included.
            </p>

            <div className="space-y-2">
              <button
                onClick={() => handleExport(resumes.extrapolated.version_id, 'pdf')}
                disabled={exporting}
                className="btn-primary w-full flex items-center justify-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Export as PDF
              </button>

              <button
                onClick={() => handleExport(resumes.extrapolated.version_id, 'html')}
                disabled={exporting}
                className="btn-secondary w-full flex items-center justify-center"
              >
                <Code className="w-4 h-4 mr-2" />
                Export as HTML
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Exported Files */}
      {exportedFiles.length > 0 && (
        <div className="card">
          <div className="flex items-center mb-4">
            <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold">Ready to Download</h3>
          </div>

          <div className="space-y-2">
            {exportedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-4"
              >
                <div className="flex items-center">
                  {file.format === 'pdf' ? (
                    <FileText className="w-5 h-5 text-red-600 mr-3" />
                  ) : (
                    <Code className="w-5 h-5 text-blue-600 mr-3" />
                  )}
                  <div>
                    <p className="text-sm font-medium">{file.filename}</p>
                    <p className="text-xs text-gray-600">
                      {file.format.toUpperCase()} format
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => handleDownload(file.downloadUrl, file.filename)}
                  className="btn-primary"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h4 className="font-semibold text-blue-900 mb-3">📝 Tips for Using Your Resumes</h4>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>Tactical Resume:</strong> Use this for immediate applications. All claims are verified and truthful.</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>Extrapolated Resume:</strong> Use after completing the study guide. Be ready to discuss "In Progress" skills.</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>Study Guide:</strong> Follow the learning path to close your skill gaps and justify the extrapolated version.</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>Data Privacy:</strong> All your data will be automatically deleted after 24 hours.</span>
          </li>
        </ul>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card text-center">
          <p className="text-3xl font-bold text-primary-600">
            {resumes.tactical ? '2' : resumes.extrapolated ? '1' : '0'}
          </p>
          <p className="text-sm text-gray-600 mt-1">Resume Versions</p>
        </div>

        <div className="card text-center">
          <p className="text-3xl font-bold text-green-600">
            {exportedFiles.length}
          </p>
          <p className="text-sm text-gray-600 mt-1">Files Exported</p>
        </div>

        <div className="card text-center">
          <p className="text-3xl font-bold text-purple-600">
            24h
          </p>
          <p className="text-sm text-gray-600 mt-1">Until Auto-Delete</p>
        </div>
      </div>

      {/* Final Actions */}
      <div className="flex justify-between items-center pt-6 border-t">
        <button
          onClick={() => navigate('/study')}
          className="btn-secondary flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>

        <button
          onClick={() => navigate('/upload')}
          className="btn-secondary"
        >
          Start New Session
        </button>
      </div>
    </div>
  )
}
