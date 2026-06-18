import React from 'react'
import { FileQuestion, Upload, Search, FileX } from 'lucide-react'

export default function EmptyState({
  icon: Icon = FileQuestion,
  title,
  description,
  action,
  actionLabel
}) {
  return (
    <div className="text-center py-12">
      <Icon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">{description}</p>
      {action && actionLabel && (
        <button onClick={action} className="btn-primary">
          {actionLabel}
        </button>
      )}
    </div>
  )
}

export function NoDataEmptyState() {
  return (
    <EmptyState
      icon={FileX}
      title="No Data Available"
      description="The requested data could not be found. Please try again or contact support."
    />
  )
}

export function UploadEmptyState({ onUpload }) {
  return (
    <EmptyState
      icon={Upload}
      title="No Files Uploaded"
      description="Upload your resume and job posting to get started with the analysis."
      action={onUpload}
      actionLabel="Upload Files"
    />
  )
}

export function SearchEmptyState() {
  return (
    <EmptyState
      icon={Search}
      title="No Results Found"
      description="Try adjusting your search criteria or filters to find what you're looking for."
    />
  )
}
