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
                <div key={i} className="bg-white rounded-lg p-4 animate-pulse">
                  <div className="h-6 bg-gray-200 rounded w-1/4 mb-2" />
                  <div className="h-4 bg-gray-200 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="text-center py-8 text-red-600">
              An error occurred while searching. Please try again.
            </div>
          ) : results && results.length > 0 ? (
            <>
              <p className="text-gray-600 mb-4">
                Found {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
              </p>
              <div className="space-y-4">
                {results.map(result => (
                  <div key={result.entry.id} className="relative">
                    <WordCard entry={result.entry} compact />
                    <span className={`absolute top-2 right-2 text-xs px-2 py-1 rounded ${
                      result.match_type === 'exact' ? 'bg-green-100 text-green-700' :
                      result.match_type === 'prefix' ? 'bg-blue-100 text-blue-700' :
                      result.match_type === 'contains' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {result.match_type}
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-600">
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
      <h2 className="text-lg font-semibold text-gray-700 mb-4">Recent Searches</h2>
      <div className="flex flex-wrap gap-2">
        {recent.map(query => (
          <button
            key={query}
            onClick={() => onSelect(query)}
            className="px-4 py-2 bg-white border border-gray-200 rounded-full hover:border-primary-400 hover:bg-primary-50 transition"
          >
            {query}
          </button>
        ))}
      </div>
    </section>
  )
}
