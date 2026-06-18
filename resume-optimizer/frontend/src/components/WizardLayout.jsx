import React from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import { FileText, MessageSquare, BarChart3, Edit3, BookOpen, Download } from 'lucide-react'

const steps = [
  { id: 1, name: 'Upload', path: '/upload', icon: FileText },
  { id: 2, name: 'Q&A', path: '/qa', icon: MessageSquare },
  { id: 3, name: 'Analysis', path: '/analysis', icon: BarChart3 },
  { id: 4, name: 'Edit Resume', path: '/resume', icon: Edit3 },
  { id: 5, name: 'Study Guide', path: '/study', icon: BookOpen },
  { id: 6, name: 'Export', path: '/export', icon: Download }
]

export default function WizardLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { currentStep, error, setError } = useSession()

  const currentStepIndex = steps.findIndex(s => s.path === location.pathname)
  const activeStep = currentStepIndex >= 0 ? currentStepIndex + 1 : 1

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Resume Optimizer
          </h1>
          <p className="text-sm text-gray-600">
            AI-powered resume analysis with confidence scoring
          </p>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <nav aria-label="Progress">
            <ol className="flex items-center justify-between">
              {steps.map((step, index) => {
                const Icon = step.icon
                const isActive = activeStep === step.id
                const isCompleted = activeStep > step.id
                const isClickable = isCompleted || isActive

                return (
                  <li key={step.id} className="flex-1 relative">
                    {index !== steps.length - 1 && (
                      <div
                        className={`absolute top-5 left-1/2 w-full h-0.5 -ml-px ${
                          isCompleted ? 'bg-primary-600' : 'bg-gray-300'
                        }`}
                        style={{ width: 'calc(100% - 2rem)' }}
                      />
                    )}

                    <button
                      onClick={() => isClickable && navigate(step.path)}
                      disabled={!isClickable}
                      className={`relative flex flex-col items-center group ${
                        isClickable ? 'cursor-pointer' : 'cursor-not-allowed'
                      }`}
                    >
                      <span
                        className={`w-10 h-10 flex items-center justify-center rounded-full border-2 transition-colors ${
                          isActive
                            ? 'border-primary-600 bg-primary-600 text-white'
                            : isCompleted
                            ? 'border-primary-600 bg-primary-600 text-white'
                            : 'border-gray-300 bg-white text-gray-500'
                        } ${isClickable && !isActive ? 'group-hover:border-primary-500' : ''}`}
                      >
                        <Icon className="w-5 h-5" />
                      </span>
                      <span
                        className={`mt-2 text-xs font-medium ${
                          isActive
                            ? 'text-primary-600'
                            : isCompleted
                            ? 'text-gray-900'
                            : 'text-gray-500'
                        }`}
                      >
                        {step.name}
                      </span>
                    </button>
                  </li>
                )
              })}
            </ol>
          </nav>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-600 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <p className="text-sm text-red-800">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-600 hover:text-red-800"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-xs text-gray-500 text-center">
            All data is automatically deleted after 24 hours. No permanent storage.
          </p>
        </div>
      </footer>
    </div>
  )
}
