import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import { Upload, FileText, Briefcase, Link as LinkIcon } from 'lucide-react'
import FileUploadZone from '../components/FileUploadZone'

export default function UploadStep() {
  const navigate = useNavigate()
  const {
    uploads,
    uploadFile,
    uploadJobPosting,
    scrapeLinkedIn,
    uploadLinkedInPDF,
    crawlCompany,
    loading,
    updateStep
  } = useSession()

  const [jobPostingText, setJobPostingText] = useState('')
  const [jobPostingUrl, setJobPostingUrl] = useState('')
  const [linkedInUrl, setLinkedInUrl] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [companyWebsite, setCompanyWebsite] = useState('')
  const [uploadMethod, setUploadMethod] = useState('text') // 'text', 'file', or 'url'

  const handleNext = async () => {
    await updateStep(2)
    navigate('/qa')
  }

  const canProceed = uploads.resume && uploads.jobPosting

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Upload Your Materials</h2>
        <p className="mt-2 text-gray-600">
          Upload your resume and job posting to get started. Optional: Add LinkedIn profile and company website for deeper analysis.
        </p>
      </div>

      {/* Required Uploads */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Resume Upload */}
        <div className="card">
          <div className="flex items-center mb-4">
            <FileText className="w-6 h-6 text-primary-600 mr-2" />
            <h3 className="text-lg font-semibold">Resume</h3>
            <span className="ml-2 px-2 py-1 bg-red-100 text-red-800 text-xs rounded">Required</span>
          </div>

          {uploads.resume ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-800 font-medium">✓ {uploads.resume.file_name}</p>
              <p className="text-xs text-green-600 mt-1">Status: {uploads.resume.processing_status}</p>
            </div>
          ) : (
            <FileUploadZone
              onFileSelect={(file) => uploadFile('resume', file)}
              accept=".pdf,.docx"
              label="Drop your resume here or click to browse"
              sublabel="PDF or DOCX, max 10MB"
            />
          )}
        </div>

        {/* Job Posting Upload */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Briefcase className="w-6 h-6 text-primary-600 mr-2" />
            <h3 className="text-lg font-semibold">Job Posting</h3>
            <span className="ml-2 px-2 py-1 bg-red-100 text-red-800 text-xs rounded">Required</span>
          </div>

          {uploads.jobPosting ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-800 font-medium">✓ Job posting uploaded</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex space-x-2">
                <button
                  onClick={() => setUploadMethod('text')}
                  className={`flex-1 py-2 px-4 rounded-lg border text-sm ${
                    uploadMethod === 'text'
                      ? 'bg-primary-50 border-primary-600 text-primary-700'
                      : 'bg-white border-gray-300 text-gray-700'
                  }`}
                >
                  Paste Text
                </button>
                <button
                  onClick={() => setUploadMethod('url')}
                  className={`flex-1 py-2 px-4 rounded-lg border text-sm ${
                    uploadMethod === 'url'
                      ? 'bg-primary-50 border-primary-600 text-primary-700'
                      : 'bg-white border-gray-300 text-gray-700'
                  }`}
                >
                  From URL
                </button>
                <button
                  onClick={() => setUploadMethod('file')}
                  className={`flex-1 py-2 px-4 rounded-lg border text-sm ${
                    uploadMethod === 'file'
                      ? 'bg-primary-50 border-primary-600 text-primary-700'
                      : 'bg-white border-gray-300 text-gray-700'
                  }`}
                >
                  Upload File
                </button>
              </div>

              {uploadMethod === 'text' ? (
                <div className="space-y-3">
                  <textarea
                    value={jobPostingText}
                    onChange={(e) => setJobPostingText(e.target.value)}
                    placeholder="Paste the job description here..."
                    className="input min-h-[200px]"
                  />
                  <button
                    onClick={() => uploadJobPosting(jobPostingText)}
                    disabled={!jobPostingText || loading}
                    className="btn-primary w-full disabled:opacity-50"
                  >
                    {loading ? 'Processing...' : 'Upload Job Posting'}
                  </button>
                </div>
              ) : uploadMethod === 'url' ? (
                <div className="space-y-3">
                  <input
                    type="url"
                    value={jobPostingUrl}
                    onChange={(e) => setJobPostingUrl(e.target.value)}
                    placeholder="https://company.com/careers/job/senior-engineer"
                    className="input"
                  />
                  <p className="text-xs text-gray-500">
                    Paste a direct link to a job posting (LinkedIn, Indeed, company career page, etc.)
                  </p>
                  <button
                    onClick={() => uploadJobPosting(jobPostingUrl, true)}
                    disabled={!jobPostingUrl || loading}
                    className="btn-primary w-full disabled:opacity-50"
                  >
                    {loading ? 'Scraping...' : 'Scrape Job Posting'}
                  </button>
                </div>
              ) : (
                <FileUploadZone
                  onFileSelect={(file) => uploadFile('jobPosting', file)}
                  accept=".pdf,.docx,.txt"
                  label="Drop job posting file here"
                  sublabel="PDF, DOCX, or TXT"
                />
              )}
            </div>
          )}
        </div>
      </div>

      {/* Optional Uploads */}
      <div className="border-t pt-8">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">Optional: Enhance Your Analysis</h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* LinkedIn */}
          <div className="card">
            <div className="flex items-center mb-4">
              <LinkIcon className="w-6 h-6 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold">LinkedIn Profile</h3>
              <span className="ml-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">Optional</span>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Add your LinkedIn to include additional experience and recommendations.
            </p>

            <div className="space-y-3">
              <input
                type="url"
                value={linkedInUrl}
                onChange={(e) => setLinkedInUrl(e.target.value)}
                placeholder="https://linkedin.com/in/yourprofile"
                className="input"
              />
              <button
                onClick={() => scrapeLinkedIn(linkedInUrl)}
                disabled={!linkedInUrl || loading}
                className="btn-secondary w-full disabled:opacity-50"
              >
                {loading ? 'Scraping...' : 'Scrape LinkedIn Profile'}
              </button>

              <div className="text-center text-sm text-gray-500">or</div>

              <FileUploadZone
                onFileSelect={(file) => uploadLinkedInPDF(file)}
                accept=".pdf"
                label="Upload LinkedIn PDF export"
                sublabel="More reliable than scraping"
                compact
              />
            </div>
          </div>

          {/* Company Website */}
          <div className="card">
            <div className="flex items-center mb-4">
              <Briefcase className="w-6 h-6 text-purple-600 mr-2" />
              <h3 className="text-lg font-semibold">Company Research</h3>
              <span className="ml-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">Optional</span>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              We'll crawl the company website to understand their culture and values.
            </p>

            <div className="space-y-3">
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Company name"
                className="input"
              />
              <input
                type="url"
                value={companyWebsite}
                onChange={(e) => setCompanyWebsite(e.target.value)}
                placeholder="https://company.com"
                className="input"
              />
              <button
                onClick={() => crawlCompany(companyName, companyWebsite)}
                disabled={!companyName || !companyWebsite || loading}
                className="btn-secondary w-full disabled:opacity-50"
              >
                {loading ? 'Crawling...' : 'Crawl Company Website'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Cover Letter (Optional) */}
      <div className="card">
        <div className="flex items-center mb-4">
          <FileText className="w-6 h-6 text-green-600 mr-2" />
          <h3 className="text-lg font-semibold">Cover Letter</h3>
          <span className="ml-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">Optional</span>
        </div>

        {uploads.coverLetter ? (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-sm text-green-800 font-medium">✓ {uploads.coverLetter.file_name}</p>
          </div>
        ) : (
          <FileUploadZone
            onFileSelect={(file) => uploadFile('coverLetter', file)}
            accept=".pdf,.docx,.txt"
            label="Drop your cover letter here (optional)"
            sublabel="Helps us understand your motivations"
            compact
          />
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t">
        <p className="text-sm text-gray-600">
          {canProceed ? '✓ Ready to continue' : 'Upload resume and job posting to continue'}
        </p>
        <button
          onClick={handleNext}
          disabled={!canProceed}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue to Q&A →
        </button>
      </div>
    </div>
  )
}
