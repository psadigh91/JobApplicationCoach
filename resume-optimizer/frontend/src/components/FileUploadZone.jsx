import React, { useState, useRef } from 'react'
import { Upload } from 'lucide-react'

export default function FileUploadZone({ onFileSelect, accept, label, sublabel, compact = false }) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      onFileSelect(file)
    }
  }

  const handleFileInput = (e) => {
    const file = e.target.files[0]
    if (file) {
      onFileSelect(file)
    }
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`border-2 border-dashed rounded-lg transition-colors cursor-pointer ${
        isDragging
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-300 hover:border-primary-400'
      } ${compact ? 'p-4' : 'p-8'}`}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileInput}
        className="hidden"
      />

      <div className="flex flex-col items-center text-center">
        <Upload className={`${compact ? 'w-8 h-8' : 'w-12 h-12'} text-gray-400 mb-3`} />
        <p className="text-sm font-medium text-gray-700">{label}</p>
        {sublabel && <p className="text-xs text-gray-500 mt-1">{sublabel}</p>}
      </div>
    </div>
  )
}
