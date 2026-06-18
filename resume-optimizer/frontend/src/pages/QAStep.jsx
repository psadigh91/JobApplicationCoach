import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import { MessageSquare, ArrowLeft } from 'lucide-react'

const commonQuestions = [
  {
    id: 'years_experience',
    question: 'How many years of professional experience do you have?',
    type: 'text'
  },
  {
    id: 'career_goals',
    question: 'What are your short-term career goals (next 1-2 years)?',
    type: 'textarea'
  },
  {
    id: 'strengths',
    question: 'What do you consider your top 3 strengths?',
    type: 'textarea'
  },
  {
    id: 'learning_preference',
    question: 'How do you prefer to learn new skills?',
    type: 'select',
    options: ['Courses', 'Documentation', 'Hands-on projects', 'Mentorship', 'Mixed approach']
  },
  {
    id: 'availability',
    question: 'When could you start a new role?',
    type: 'select',
    options: ['Immediately', '2 weeks notice', '1 month notice', '2+ months']
  }
]

export default function QAStep() {
  const navigate = useNavigate()
  const { updateStep, startAnalysis } = useSession()
  const [answers, setAnswers] = useState({})
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleAnswer = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }))
  }

  const handleSkip = async () => {
    await updateStep(3)
    navigate('/analysis')
  }

  const handleSubmitAndAnalyze = async () => {
    try {
      setIsAnalyzing(true)
      await updateStep(3)
      await startAnalysis()
      navigate('/analysis')
    } catch (err) {
      console.error('Failed to start analysis:', err)
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Quick Questions</h2>
        <p className="mt-2 text-gray-600">
          Help us understand your background better. These answers will improve the accuracy of our analysis.
        </p>
      </div>

      <div className="card">
        <div className="space-y-6">
          {commonQuestions.map((q) => (
            <div key={q.id}>
              <label className="label">
                {q.question}
              </label>

              {q.type === 'text' && (
                <input
                  type="text"
                  value={answers[q.id] || ''}
                  onChange={(e) => handleAnswer(q.id, e.target.value)}
                  className="input"
                  placeholder="Your answer..."
                />
              )}

              {q.type === 'textarea' && (
                <textarea
                  value={answers[q.id] || ''}
                  onChange={(e) => handleAnswer(q.id, e.target.value)}
                  className="input min-h-[100px]"
                  placeholder="Your answer..."
                />
              )}

              {q.type === 'select' && (
                <select
                  value={answers[q.id] || ''}
                  onChange={(e) => handleAnswer(q.id, e.target.value)}
                  className="input"
                >
                  <option value="">Select an option...</option>
                  {q.options.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-between items-center pt-6 border-t">
        <button
          onClick={() => navigate('/upload')}
          className="btn-secondary flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>

        <div className="flex space-x-3">
          <button
            onClick={handleSkip}
            className="btn-secondary"
          >
            Skip Q&A
          </button>
          <button
            onClick={handleSubmitAndAnalyze}
            disabled={isAnalyzing}
            className="btn-primary disabled:opacity-50"
          >
            {isAnalyzing ? 'Starting Analysis...' : 'Submit & Start Analysis →'}
          </button>
        </div>
      </div>
    </div>
  )
}
