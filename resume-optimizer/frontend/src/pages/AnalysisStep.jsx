import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import { BarChart3, TrendingUp, Target, Brain, Heart, ArrowLeft, Loader } from 'lucide-react'

function ScoreCircle({ score, label, color = 'primary' }) {
  const colorClasses = {
    primary: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    yellow: 'text-yellow-600 bg-yellow-50',
    purple: 'text-purple-600 bg-purple-50'
  }

  return (
    <div className="flex flex-col items-center">
      <div className={`relative w-24 h-24 rounded-full flex items-center justify-center ${colorClasses[color]}`}>
        <div className="text-center">
          <div className="text-2xl font-bold">{score}</div>
          <div className="text-xs">/ 100</div>
        </div>
      </div>
      <p className="mt-2 text-sm font-medium text-gray-700">{label}</p>
    </div>
  )
}

export default function AnalysisStep() {
  const navigate = useNavigate()
  const { analysis, loading, updateStep, generateResumes } = useSession()

  useEffect(() => {
    // If no analysis, redirect back
    if (!analysis && !loading) {
      navigate('/qa')
    }
  }, [analysis, loading, navigate])

  const handleGenerateResumes = async () => {
    try {
      await generateResumes()
      await updateStep(4)
      navigate('/resume')
    } catch (err) {
      console.error('Failed to generate resumes:', err)
    }
  }

  if (loading || !analysis) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader className="w-12 h-12 text-primary-600 animate-spin mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Analyzing Your Profile...</h3>
        <p className="text-gray-600">This usually takes 30-60 seconds</p>
      </div>
    )
  }

  const { overall_score, exact_match, transferable_match, growth_potential, culture_fit, recommendation } = analysis

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Analysis Results</h2>
        <p className="mt-2 text-gray-600">
          Here's your 4-dimension scorecard based on the job requirements.
        </p>
      </div>

      {/* Overall Score */}
      <div className="card bg-gradient-to-br from-primary-50 to-blue-50">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Overall Match Score</h3>
          <div className="text-6xl font-bold text-primary-600 mb-2">{overall_score}</div>
          <div className="text-sm text-gray-600 mb-4">out of 100</div>

          <div className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${
            recommendation === 'strong_fit' ? 'bg-green-100 text-green-800' :
            recommendation === 'moderate_fit' ? 'bg-yellow-100 text-yellow-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {recommendation === 'strong_fit' ? '✓ Strong Fit' :
             recommendation === 'moderate_fit' ? '~ Moderate Fit' :
             '○ Review Needed'}
          </div>
        </div>
      </div>

      {/* 4-Dimension Scores */}
      <div className="card">
        <h3 className="text-xl font-semibold mb-6">4-Dimension Breakdown</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <ScoreCircle
            score={exact_match?.score || 0}
            label="Exact Match"
            color="primary"
          />
          <ScoreCircle
            score={transferable_match?.score || 0}
            label="Transferable"
            color="green"
          />
          <ScoreCircle
            score={growth_potential?.score || 0}
            label="Growth"
            color="yellow"
          />
          <ScoreCircle
            score={culture_fit?.score || 0}
            label="Culture Fit"
            color="purple"
          />
        </div>
      </div>

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Matches */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Target className="w-5 h-5 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold">Your Strengths</h3>
          </div>

          <div className="space-y-3">
            {exact_match?.matches?.slice(0, 5).map((match, i) => (
              <div key={i} className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <div>
                  <p className="text-sm font-medium">{match.skill || match.from_skill}</p>
                  {match.evidence && (
                    <p className="text-xs text-gray-600">{match.evidence}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Gaps */}
        <div className="card">
          <div className="flex items-center mb-4">
            <TrendingUp className="w-5 h-5 text-yellow-600 mr-2" />
            <h3 className="text-lg font-semibold">Growth Opportunities</h3>
          </div>

          <div className="space-y-3">
            {exact_match?.gaps?.slice(0, 5).map((gap, i) => (
              <div key={i} className="flex items-start">
                <span className="text-yellow-600 mr-2">○</span>
                <div>
                  <p className="text-sm font-medium">{gap.skill}</p>
                  {gap.impact && (
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      gap.impact === 'high' ? 'bg-red-100 text-red-700' :
                      gap.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {gap.impact} impact
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Transferable Skills */}
      {transferable_match?.matches && transferable_match.matches.length > 0 && (
        <div className="card">
          <div className="flex items-center mb-4">
            <Brain className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold">Transferable Skills</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {transferable_match.matches.slice(0, 6).map((match, i) => (
              <div key={i} className="bg-blue-50 rounded-lg p-3">
                <p className="text-sm">
                  <span className="font-medium">{match.from_skill}</span>
                  <span className="text-gray-500 mx-2">→</span>
                  <span className="font-medium text-blue-600">{match.to_skill}</span>
                </p>
                {match.transferability && (
                  <p className="text-xs text-gray-600 mt-1">
                    {match.transferability} transferability
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t">
        <button
          onClick={() => navigate('/qa')}
          className="btn-secondary flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>

        <button
          onClick={handleGenerateResumes}
          disabled={loading}
          className="btn-primary disabled:opacity-50"
        >
          {loading ? 'Generating Resumes...' : 'Generate Optimized Resumes →'}
        </button>
      </div>
    </div>
  )
}
