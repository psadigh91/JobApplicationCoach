import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import { Edit3, FileText, Sparkles, ArrowLeft, Loader, Check } from 'lucide-react'

export default function ResumeEditStep() {
  const navigate = useNavigate()
  const { resumes, loading, updateStep } = useSession()
  const [selectedVersion, setSelectedVersion] = useState('tactical')

  useEffect(() => {
    if (!resumes.tactical && !resumes.extrapolated && !loading) {
      navigate('/analysis')
    }
  }, [resumes, loading, navigate])

  const handleContinue = async () => {
    await updateStep(5)
    navigate('/study')
  }

  if (loading || (!resumes.tactical && !resumes.extrapolated)) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader className="w-12 h-12 text-primary-600 animate-spin mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Generating Your Resumes...</h3>
        <p className="text-gray-600">Creating tactical and extrapolated versions</p>
      </div>
    )
  }

  const currentResume = selectedVersion === 'tactical' ? resumes.tactical : resumes.extrapolated

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Your Optimized Resumes</h2>
        <p className="mt-2 text-gray-600">
          Review and edit both versions. Tactical shows truthful improvements, Extrapolated includes 3-month growth potential.
        </p>
      </div>

      {/* Version Selector */}
      <div className="flex space-x-4">
        <button
          onClick={() => setSelectedVersion('tactical')}
          className={`flex-1 p-4 rounded-lg border-2 transition-all ${
            selectedVersion === 'tactical'
              ? 'border-primary-600 bg-primary-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <FileText className="w-5 h-5 text-primary-600 mr-2" />
              <h3 className="font-semibold">Tactical Version</h3>
            </div>
            {resumes.tactical?.approved && (
              <Check className="w-5 h-5 text-green-600" />
            )}
          </div>
          <p className="text-sm text-gray-600 text-left">
            100% truthful improvements. Keywords optimized, bullets reordered for impact.
          </p>
        </button>

        <button
          onClick={() => setSelectedVersion('extrapolated')}
          className={`flex-1 p-4 rounded-lg border-2 transition-all ${
            selectedVersion === 'extrapolated'
              ? 'border-purple-600 bg-purple-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <Sparkles className="w-5 h-5 text-purple-600 mr-2" />
              <h3 className="font-semibold">Extrapolated Version</h3>
            </div>
            {resumes.extrapolated?.approved && (
              <Check className="w-5 h-5 text-green-600" />
            )}
          </div>
          <p className="text-sm text-gray-600 text-left">
            3-month growth projection. Skills marked as "(Learning)" or "(In Progress)".
          </p>
        </button>
      </div>

      {/* Resume Content */}
      {currentResume && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Resume Preview */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Resume Preview</h3>

            <div className="space-y-6 text-sm">
              {/* Contact */}
              {currentResume.content?.sections?.contact && (
                <div>
                  <h4 className="font-bold text-lg">
                    {currentResume.content.sections.contact.name}
                  </h4>
                  <p className="text-gray-600">
                    {currentResume.content.sections.contact.email} | {currentResume.content.sections.contact.phone}
                  </p>
                </div>
              )}

              {/* Summary */}
              {currentResume.content?.sections?.summary && (
                <div>
                  <h5 className="font-semibold text-gray-900 mb-2">Professional Summary</h5>
                  <p className="text-gray-700">{currentResume.content.sections.summary}</p>
                </div>
              )}

              {/* Skills */}
              {currentResume.content?.sections?.skills && (
                <div>
                  <h5 className="font-semibold text-gray-900 mb-2">Skills</h5>
                  <div className="flex flex-wrap gap-2">
                    {currentResume.content.sections.skills.slice(0, 15).map((skill, i) => (
                      <span
                        key={i}
                        className={`px-3 py-1 rounded-full text-xs ${
                          skill.includes('(Learning)') || skill.includes('(In Progress)')
                            ? 'bg-purple-100 text-purple-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Experience */}
              {currentResume.content?.sections?.experience && (
                <div>
                  <h5 className="font-semibold text-gray-900 mb-2">Experience</h5>
                  {currentResume.content.sections.experience.slice(0, 3).map((exp, i) => (
                    <div key={i} className="mb-4">
                      <p className="font-medium">{exp.title}</p>
                      <p className="text-gray-600 text-xs">{exp.company} | {exp.dates}</p>
                      <ul className="mt-2 space-y-1 list-disc list-inside text-xs text-gray-700">
                        {exp.bullets?.slice(0, 3).map((bullet, j) => (
                          <li key={j}>{bullet}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Modifications */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">What Changed</h3>

            <div className="space-y-4">
              {currentResume.modifications?.slice(0, 10).map((mod, i) => (
                <div key={i} className="border-l-4 border-primary-200 pl-4 py-2">
                  <p className="text-sm font-medium text-gray-900">{mod.section}</p>
                  {mod.change_type && (
                    <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                      {mod.change_type}
                    </span>
                  )}
                  {mod.rationale && (
                    <p className="text-xs text-gray-600 mt-1">{mod.rationale}</p>
                  )}
                </div>
              ))}

              {(!currentResume.modifications || currentResume.modifications.length === 0) && (
                <p className="text-sm text-gray-500 italic">
                  No modifications recorded for this version.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Warnings for Extrapolated */}
      {selectedVersion === 'extrapolated' && resumes.extrapolated?.content?.warnings && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-yellow-800 mb-2">⚠️ Important Notes:</h4>
          <ul className="text-sm text-yellow-700 space-y-1">
            {resumes.extrapolated.content.warnings.map((warning, i) => (
              <li key={i}>• {warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t">
        <button
          onClick={() => navigate('/analysis')}
          className="btn-secondary flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>

        <button
          onClick={handleContinue}
          className="btn-primary"
        >
          Continue to Study Guide →
        </button>
      </div>
    </div>
  )
}
