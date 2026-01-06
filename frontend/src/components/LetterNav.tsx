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
          <div key={i} className="w-10 h-10 bg-aromanian-100 dark:bg-neutral-800 rounded animate-pulse" />
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
              ? 'bg-aromanian-600 text-white'
              : 'bg-cream-50 dark:bg-neutral-900 border border-aromanian-200 dark:border-neutral-700 hover:border-aromanian-400 dark:hover:border-aromanian-500 hover:bg-aromanian-50 dark:hover:bg-neutral-800 text-aromanian-700 dark:text-aromanian-400'
          }`}
          title={`${count} entries`}
        >
          {letter}
        </Link>
      ))}
    </div>
  )
}
