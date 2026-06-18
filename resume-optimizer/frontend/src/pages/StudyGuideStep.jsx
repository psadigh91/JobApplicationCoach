import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import { BookOpen, Youtube, FileText, Code, ArrowLeft, Loader } from 'lucide-react'

export default function StudyGuideStep() {
  const navigate = useNavigate()
  const { studyGuide, loading, updateStep, generateStudyGuide } = useSession()

  useEffect(() => {
    if (!studyGuide && !loading) {
      generateStudyGuide()
    }
  }, [])

  const handleContinue = async () => {
    await updateStep(6)
    navigate('/export')
  }

  if (loading || !studyGuide) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader className="w-12 h-12 text-primary-600 animate-spin mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Creating Your Study Guide...</h3>
        <p className="text-gray-600">Finding the best learning resources for your gaps</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Your Personalized Study Guide</h2>
        <p className="mt-2 text-gray-600">
          Based on your skill gaps, here's a 3-month learning plan with curated resources.
        </p>
      </div>

      {/* Learning Timeline */}
      {studyGuide.skills && studyGuide.skills.length > 0 && (
        <div className="space-y-6">
          {studyGuide.skills.map((skillGuide, index) => (
            <div key={index} className="card">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <BookOpen className="w-5 h-5 text-primary-600 mr-2" />
                  <h3 className="text-lg font-semibold">{skillGuide.skill}</h3>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  skillGuide.priority === 'high' ? 'bg-red-100 text-red-700' :
                  skillGuide.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {skillGuide.priority} priority
                </span>
              </div>

              {/* Learning Path */}
              {skillGuide.guide?.learning_path && (
                <div className="space-y-4">
                  {skillGuide.guide.learning_path.map((phase, phaseIndex) => (
                    <div key={phaseIndex} className="border-l-4 border-primary-200 pl-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{phase.phase}</h4>
                        <span className="text-xs text-gray-500">{phase.duration}</span>
                      </div>

                      {/* Topics */}
                      {phase.topics && (
                        <div className="mb-3">
                          <p className="text-sm text-gray-600">
                            {phase.topics.join(', ')}
                          </p>
                        </div>
                      )}

                      {/* Resources */}
                      {phase.resources && (
                        <div className="space-y-2">
                          {phase.resources.map((resource, resIndex) => (
                            <div key={resIndex} className="bg-gray-50 rounded-lg p-3">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center">
                                    {resource.type === 'video' && <Youtube className="w-4 h-4 text-red-600 mr-2" />}
                                    {resource.type === 'course' && <BookOpen className="w-4 h-4 text-blue-600 mr-2" />}
                                    {resource.type === 'documentation' && <FileText className="w-4 h-4 text-gray-600 mr-2" />}
                                    {resource.type === 'tutorial' && <Code className="w-4 h-4 text-green-600 mr-2" />}
                                    <p className="text-sm font-medium">{resource.title}</p>
                                  </div>

                                  <p className="text-xs text-gray-600 ml-6 mt-1">
                                    {resource.provider} | {resource.duration}
                                    {resource.free && <span className="ml-2 text-green-600 font-medium">Free</span>}
                                  </p>
                                </div>

                                <span className={`text-xs px-2 py-0.5 rounded ${
                                  resource.credibility === 'high' ? 'bg-green-100 text-green-700' :
                                  resource.credibility === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {resource.credibility}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Estimated Time */}
              {skillGuide.guide?.estimated_hours && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Estimated time:</span> {skillGuide.guide.estimated_hours} hours
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* No skills to learn */}
      {(!studyGuide.skills || studyGuide.skills.length === 0) && (
        <div className="card text-center py-12">
          <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            You're in great shape!
          </h3>
          <p className="text-gray-600">
            No critical skill gaps detected. Keep building on your strengths!
          </p>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t">
        <button
          onClick={() => navigate('/resume')}
          className="btn-secondary flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>

        <button
          onClick={handleContinue}
          className="btn-primary"
        >
          Continue to Export →
        </button>
      </div>
    </div>
  )
}
