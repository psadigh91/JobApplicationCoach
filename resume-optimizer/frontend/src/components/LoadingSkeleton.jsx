import React from 'react'

export function CardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded w-full"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        <div className="h-4 bg-gray-200 rounded w-4/6"></div>
      </div>
    </div>
  )
}

export function ScoreCardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="text-center">
        <div className="h-8 bg-gray-200 rounded w-48 mx-auto mb-4"></div>
        <div className="w-32 h-32 bg-gray-200 rounded-full mx-auto mb-4"></div>
        <div className="h-6 bg-gray-200 rounded w-32 mx-auto"></div>
      </div>
    </div>
  )
}

export function ListSkeleton({ items = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-start space-x-3 animate-pulse">
          <div className="w-5 h-5 bg-gray-200 rounded"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 5, cols = 3 }) {
  return (
    <div className="animate-pulse">
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {/* Header */}
        {Array.from({ length: cols }).map((_, i) => (
          <div key={`header-${i}`} className="h-8 bg-gray-200 rounded"></div>
        ))}

        {/* Rows */}
        {Array.from({ length: rows }).map((_, rowIndex) =>
          Array.from({ length: cols }).map((_, colIndex) => (
            <div key={`${rowIndex}-${colIndex}`} className="h-6 bg-gray-200 rounded"></div>
          ))
        )}
      </div>
    </div>
  )
}

export default function LoadingSkeleton({ type = 'card', ...props }) {
  switch (type) {
    case 'scorecard':
      return <ScoreCardSkeleton {...props} />
    case 'list':
      return <ListSkeleton {...props} />
    case 'table':
      return <TableSkeleton {...props} />
    default:
      return <CardSkeleton {...props} />
  }
}
