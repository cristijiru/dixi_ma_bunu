import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import SearchBar from '../components/SearchBar'
import WordCard from '../components/WordCard'
import { search } from '../api/client'
import { useEffect } from 'react'

const RECENT_SEARCHES_KEY = 'dixi_recent_searches'
const MAX_RECENT = 10

function saveRecentSearch(query: string) {
  try {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
    const recent: string[] = stored ? JSON.parse(stored) : []
    const updated = [query, ...recent.filter(q => q !== query)].slice(0, MAX_RECENT)
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated))
  } catch {
    // Ignore localStorage errors
  }
}

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const query = searchParams.get('q') || ''

  const { data: results, isLoading, error } = useQuery({
    queryKey: ['search', query],
    queryFn: () => search(query),
    enabled: query.length > 0,
  })

  useEffect(() => {
    if (query && results && results.length > 0) {
      saveRecentSearch(query)
    }
  }, [query, results])

  const handleSearch = (newQuery: string) => {
    setSearchParams({ q: newQuery })
  }

  return (
    <div className="space-y-8">
      <section className="py-4">
        <SearchBar initialQuery={query} onSearch={handleSearch} />
      </section>

      {query && (
        <section>
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 5 }, (_, i) => (
                <div key={i} className="bg-cream-50 dark:bg-neutral-900 rounded-lg p-4 animate-pulse border border-aromanian-100 dark:border-neutral-800">
                  <div className="h-6 bg-aromanian-100 dark:bg-neutral-800 rounded w-1/4 mb-2" />
                  <div className="h-4 bg-aromanian-100 dark:bg-neutral-800 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="text-center py-8 text-aromanian-600 dark:text-aromanian-400">
              An error occurred while searching. Please try again.
            </div>
          ) : results && results.length > 0 ? (
            <>
              <p className="text-gray-600 dark:text-neutral-400 mb-4">
                Found {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
              </p>
              <div className="space-y-4">
                {results.map(result => (
                  <div key={result.entry.id} className="relative">
                    <WordCard entry={result.entry} compact />
                    <span className={`absolute top-2 right-2 text-xs px-2 py-1 rounded ${
                      result.match_type === 'exact' ? 'bg-aromanian-100 text-aromanian-700 dark:bg-aromanian-900/50 dark:text-aromanian-300' :
                      result.match_type === 'prefix' ? 'bg-aromanian-50 text-aromanian-600 dark:bg-neutral-800 dark:text-aromanian-400' :
                      result.match_type === 'contains' ? 'bg-cream-200 text-gray-700 dark:bg-neutral-800 dark:text-neutral-300' :
                      'bg-cream-100 text-gray-600 dark:bg-neutral-900 dark:text-neutral-400'
                    }`}>
                      {result.match_type}
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-600 dark:text-neutral-400">
              No results found for "{query}". Try a different search term.
            </div>
          )}
        </section>
      )}

      {!query && <RecentSearches onSelect={handleSearch} />}
    </div>
  )
}

function RecentSearches({ onSelect }: { onSelect: (query: string) => void }) {
  let recent: string[] = []
  try {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
    recent = stored ? JSON.parse(stored) : []
  } catch {
    // Ignore
  }

  if (recent.length === 0) return null

  return (
    <section>
      <h2 className="text-lg font-semibold text-aromanian-700 dark:text-aromanian-400 mb-4">Recent Searches</h2>
      <div className="flex flex-wrap gap-2">
        {recent.map(query => (
          <button
            key={query}
            onClick={() => onSelect(query)}
            className="px-4 py-2 bg-cream-50 dark:bg-neutral-900 border border-aromanian-200 dark:border-neutral-700 rounded-full hover:border-aromanian-400 dark:hover:border-aromanian-500 hover:bg-aromanian-50 dark:hover:bg-neutral-800 text-aromanian-700 dark:text-aromanian-400 transition"
          >
            {query}
          </button>
        ))}
      </div>
    </section>
  )
}
