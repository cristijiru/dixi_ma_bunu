import { useQuery } from '@tanstack/react-query'
import SearchBar from '../components/SearchBar'
import WordCard from '../components/WordCard'
import LetterNav from '../components/LetterNav'
import { getRandomWord, getStats } from '../api/client'

export default function Home() {
  const { data: wordOfDay, isLoading: loadingWord } = useQuery({
    queryKey: ['wordOfDay'],
    queryFn: getRandomWord,
    staleTime: 1000 * 60 * 60, // 1 hour
  })

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
  })

  return (
    <div className="space-y-12">
      <section className="text-center py-8">
        <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-100 mb-4">
          Aromanian Dictionary
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-xl mx-auto">
          Explore the rich vocabulary of the Aromanian language with translations
          in Romanian, English, and French.
        </p>
        <SearchBar autoFocus />
      </section>

      <section>
        <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-4 text-center">
          Browse by Letter
        </h2>
        <LetterNav />
      </section>

      <section className="max-w-2xl mx-auto">
        <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-4">
          Word of the Day
        </h2>
        {loadingWord ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 animate-pulse">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
          </div>
        ) : wordOfDay ? (
          <WordCard entry={wordOfDay} />
        ) : null}
      </section>

      {stats && (
        <section className="text-center py-8 bg-gray-100 dark:bg-gray-800 rounded-xl">
          <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-4">
            Dictionary Statistics
          </h2>
          <div className="flex justify-center gap-8">
            <div>
              <p className="text-3xl font-bold text-primary-600 dark:text-primary-400">
                {stats.total_entries.toLocaleString()}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Entries</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-primary-600 dark:text-primary-400">
                {stats.entries_by_letter.length}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Letters</p>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
