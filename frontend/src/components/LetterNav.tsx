import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getLetters } from '../api/client'

interface LetterNavProps {
  activeLetter?: string
}

export default function LetterNav({ activeLetter }: LetterNavProps) {
  const { data: letters, isLoading } = useQuery({
    queryKey: ['letters'],
    queryFn: getLetters,
  })

  if (isLoading) {
    return (
      <div className="flex flex-wrap gap-2 justify-center">
        {Array.from({ length: 26 }, (_, i) => (
          <div key={i} className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        ))}
      </div>
    )
  }

  return (
    <div className="flex flex-wrap gap-2 justify-center">
      {letters?.map(({ letter, count }) => (
        <Link
          key={letter}
          to={`/browse/${letter}`}
          className={`w-10 h-10 flex items-center justify-center rounded font-medium transition ${
            activeLetter === letter
              ? 'bg-primary-600 text-white'
              : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-gray-700'
          }`}
          title={`${count} entries`}
        >
          {letter}
        </Link>
      ))}
    </div>
  )
}
