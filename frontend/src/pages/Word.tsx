import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import WordCard from '../components/WordCard'
import { getWord } from '../api/client'

export default function Word() {
  const { id } = useParams<{ id: string }>()

  const { data: entry, isLoading, error } = useQuery({
    queryKey: ['word', id],
    queryFn: () => getWord(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-6 animate-pulse">
          <div className="h-10 bg-gray-200 rounded w-1/3 mb-4" />
          <div className="h-4 bg-gray-200 rounded w-full mb-2" />
          <div className="h-4 bg-gray-200 rounded w-2/3" />
        </div>
      </div>
    )
  }

  if (error || !entry) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Word Not Found</h1>
        <p className="text-gray-600 mb-6">
          The word you're looking for doesn't exist in our dictionary.
        </p>
        <Link
          to="/"
          className="px-6 py-2 bg-primary-600 text-white rounded-full hover:bg-primary-700 transition"
        >
          Go Home
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Link
        to="/"
        className="inline-flex items-center text-primary-600 hover:text-primary-800 mb-6 transition"
      >
        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </Link>
      <WordCard entry={entry} />
    </div>
  )
}
