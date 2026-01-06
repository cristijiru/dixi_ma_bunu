import { useParams, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import WordCard from '../components/WordCard'
import LetterNav from '../components/LetterNav'
import { getByLetter } from '../api/client'

const PAGE_SIZE = 50

export default function Browse() {
  const { letter } = useParams<{ letter: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const page = parseInt(searchParams.get('page') || '1', 10)
  const offset = (page - 1) * PAGE_SIZE

  const { data, isLoading } = useQuery({
    queryKey: ['browse', letter, page],
    queryFn: () => getByLetter(letter!, { limit: PAGE_SIZE, offset }),
    enabled: !!letter,
  })

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0

  const handlePageChange = (newPage: number) => {
    setSearchParams({ page: newPage.toString() })
    window.scrollTo(0, 0)
  }

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-bold text-aromanian-700 dark:text-aromanian-400 mb-6 text-center">
          Browse Dictionary
        </h1>
        <LetterNav activeLetter={letter} />
      </section>

      {letter && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-aromanian-700 dark:text-aromanian-400">
              Words starting with "{letter}"
            </h2>
            {data && (
              <p className="text-gray-600 dark:text-neutral-400">
                {data.total.toLocaleString()} entries
              </p>
            )}
          </div>

          {isLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 12 }, (_, i) => (
                <div key={i} className="bg-cream-50 dark:bg-neutral-900 rounded-lg p-4 animate-pulse border border-aromanian-100 dark:border-neutral-800">
                  <div className="h-6 bg-aromanian-100 dark:bg-neutral-800 rounded w-1/2 mb-2" />
                  <div className="h-4 bg-aromanian-100 dark:bg-neutral-800 rounded w-3/4" />
                </div>
              ))}
            </div>
          ) : data && data.entries.length > 0 ? (
            <>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {data.entries.map(entry => (
                  <WordCard key={entry.id} entry={entry} compact />
                ))}
              </div>

              {totalPages > 1 && (
                <div className="flex justify-center gap-2 mt-8">
                  <button
                    onClick={() => handlePageChange(page - 1)}
                    disabled={page <= 1}
                    className="px-4 py-2 bg-cream-50 dark:bg-neutral-900 border border-aromanian-200 dark:border-neutral-700 rounded hover:bg-aromanian-50 dark:hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed text-aromanian-700 dark:text-aromanian-400 transition"
                  >
                    Previous
                  </button>
                  <span className="px-4 py-2 text-gray-600 dark:text-neutral-400">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => handlePageChange(page + 1)}
                    disabled={page >= totalPages}
                    className="px-4 py-2 bg-cream-50 dark:bg-neutral-900 border border-aromanian-200 dark:border-neutral-700 rounded hover:bg-aromanian-50 dark:hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed text-aromanian-700 dark:text-aromanian-400 transition"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          ) : (
            <p className="text-center text-gray-600 dark:text-neutral-400 py-8">
              No entries found for this letter.
            </p>
          )}
        </section>
      )}
    </div>
  )
}
