import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SessionProvider } from './context/SessionContext'
import WizardLayout from './components/WizardLayout'
import UploadStep from './pages/UploadStep'
import QAStep from './pages/QAStep'
import AnalysisStep from './pages/AnalysisStep'
import ResumeEditStep from './pages/ResumeEditStep'
import StudyGuideStep from './pages/StudyGuideStep'
import ExportStep from './pages/ExportStep'

function App() {
  return (
    <BrowserRouter>
      <SessionProvider>
        <Routes>
          <Route path="/" element={<WizardLayout />}>
            <Route index element={<Navigate to="/upload" replace />} />
            <Route path="upload" element={<UploadStep />} />
            <Route path="qa" element={<QAStep />} />
            <Route path="analysis" element={<AnalysisStep />} />
            <Route path="resume" element={<ResumeEditStep />} />
            <Route path="study" element={<StudyGuideStep />} />
            <Route path="export" element={<ExportStep />} />
          </Route>
        </Routes>
      </SessionProvider>
    </BrowserRouter>
  )
}

export default App
