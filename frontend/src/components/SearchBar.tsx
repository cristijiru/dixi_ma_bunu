import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSuggestions, Suggestion } from '../api/client'

interface SearchBarProps {
  initialQuery?: string
  autoFocus?: boolean
  onSearch?: (query: string) => void
}

export default function SearchBar({ initialQuery = '', autoFocus = false, onSearch }: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery)
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<number>()

  useEffect(() => {
    if (query.length < 2) {
      setSuggestions([])
      return
    }

    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    debounceRef.current = window.setTimeout(async () => {
      try {
        const results = await getSuggestions(query)
        setSuggestions(results)
        setShowSuggestions(true)
      } catch {
        setSuggestions([])
      }
    }, 200)

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [query])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      setShowSuggestions(false)
      if (onSearch) {
        onSearch(query)
      } else {
        navigate(`/search?q=${encodeURIComponent(query)}`)
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex(prev => Math.min(prev + 1, suggestions.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex(prev => Math.max(prev - 1, -1))
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault()
      setQuery(suggestions[selectedIndex].headword)
      setShowSuggestions(false)
      if (onSearch) {
        onSearch(suggestions[selectedIndex].headword)
      } else {
        navigate(`/search?q=${encodeURIComponent(suggestions[selectedIndex].headword)}`)
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false)
    }
  }

  const handleSuggestionClick = (suggestion: Suggestion) => {
    setQuery(suggestion.headword)
    setShowSuggestions(false)
    if (onSearch) {
      onSearch(suggestion.headword)
    } else {
      navigate(`/search?q=${encodeURIComponent(suggestion.headword)}`)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative w-full max-w-2xl mx-auto">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={e => {
            setQuery(e.target.value)
            setSelectedIndex(-1)
          }}
          onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          onKeyDown={handleKeyDown}
          placeholder="Search for a word..."
          autoFocus={autoFocus}
          className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-full focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition"
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-primary-600 text-white rounded-full hover:bg-primary-700 transition"
        >
          Search
        </button>
      </div>

      {showSuggestions && suggestions.length > 0 && (
        <ul className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {suggestions.map((suggestion, index) => (
            <li
              key={suggestion.headword}
              onClick={() => handleSuggestionClick(suggestion)}
              className={`px-4 py-2 cursor-pointer flex justify-between ${
                index === selectedIndex ? 'bg-primary-100' : 'hover:bg-gray-100'
              }`}
            >
              <span className="font-medium">{suggestion.headword}</span>
              {suggestion.part_of_speech && (
                <span className="text-sm text-gray-500 italic">{suggestion.part_of_speech}</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </form>
  )
}
