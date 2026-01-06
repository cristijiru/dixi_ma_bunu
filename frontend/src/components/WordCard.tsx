import { Link } from 'react-router-dom'
import { DictionaryEntry } from '../api/client'

interface WordCardProps {
  entry: DictionaryEntry
  compact?: boolean
}

export default function WordCard({ entry, compact = false }: WordCardProps) {
  if (compact) {
    return (
      <Link
        to={`/word/${entry.id}`}
        className="block p-4 bg-cream-50 dark:bg-neutral-900 rounded-lg border border-aromanian-100 dark:border-neutral-800 hover:border-aromanian-300 dark:hover:border-neutral-600 hover:shadow-md transition"
      >
        <div className="flex items-baseline gap-2">
          <span className="text-lg font-semibold text-aromanian-700 dark:text-aromanian-400">{entry.headword}</span>
          {entry.part_of_speech && (
            <span className="text-sm text-gray-500 dark:text-neutral-400 italic">{entry.part_of_speech}</span>
          )}
        </div>
        {entry.translation_en && (
          <p className="text-gray-600 dark:text-neutral-300 mt-1 truncate">{entry.translation_en}</p>
        )}
      </Link>
    )
  }

  return (
    <div className="bg-cream-50 dark:bg-neutral-900 rounded-xl shadow-md p-6 border border-aromanian-100 dark:border-neutral-800">
      <div className="flex items-baseline gap-3 mb-4 flex-wrap">
        <h2 className="text-3xl font-bold text-aromanian-700 dark:text-aromanian-400">{entry.headword}</h2>
        {entry.pronunciation && (
          <span className="text-gray-500 dark:text-neutral-400">/{entry.pronunciation}/</span>
        )}
        {entry.part_of_speech && (
          <span className="px-2 py-1 bg-aromanian-50 dark:bg-neutral-800 text-aromanian-700 dark:text-aromanian-300 text-sm rounded">
            {entry.part_of_speech}
          </span>
        )}
      </div>

      {entry.inflections && (
        <p className="text-sm text-gray-600 dark:text-neutral-400 mb-4">
          <span className="font-medium">Forms:</span> {entry.inflections}
        </p>
      )}

      {entry.definition && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700 dark:text-neutral-300 mb-1">Definition</h3>
          <p className="text-gray-800 dark:text-neutral-200">{entry.definition}</p>
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-4 mb-4">
        {entry.translation_ro && (
          <div className="p-3 bg-cream-100 dark:bg-neutral-800 rounded-lg border border-aromanian-100 dark:border-neutral-700">
            <span className="text-xs font-medium text-aromanian-600 dark:text-aromanian-400 uppercase">Romanian</span>
            <p className="text-gray-800 dark:text-neutral-200">{entry.translation_ro}</p>
          </div>
        )}
        {entry.translation_en && (
          <div className="p-3 bg-cream-100 dark:bg-neutral-800 rounded-lg border border-aromanian-100 dark:border-neutral-700">
            <span className="text-xs font-medium text-aromanian-600 dark:text-aromanian-400 uppercase">English</span>
            <p className="text-gray-800 dark:text-neutral-200">{entry.translation_en}</p>
          </div>
        )}
        {entry.translation_fr && (
          <div className="p-3 bg-cream-100 dark:bg-neutral-800 rounded-lg border border-aromanian-100 dark:border-neutral-700">
            <span className="text-xs font-medium text-aromanian-600 dark:text-aromanian-400 uppercase">French</span>
            <p className="text-gray-800 dark:text-neutral-200">{entry.translation_fr}</p>
          </div>
        )}
      </div>

      {entry.examples.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700 dark:text-neutral-300 mb-2">Examples</h3>
          <ul className="space-y-1">
            {entry.examples.map((example, i) => (
              <li key={i} className="text-gray-700 dark:text-neutral-300 pl-4 border-l-2 border-aromanian-300 dark:border-neutral-600">
                {example}
              </li>
            ))}
          </ul>
        </div>
      )}

      {entry.expressions.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700 dark:text-neutral-300 mb-2">Expressions</h3>
          <ul className="space-y-1">
            {entry.expressions.map((expr, i) => (
              <li key={i} className="text-gray-700 dark:text-neutral-300 italic">{expr}</li>
            ))}
          </ul>
        </div>
      )}

      {entry.etymology && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700 dark:text-neutral-300 mb-1">Etymology</h3>
          <p className="text-gray-600 dark:text-neutral-400 text-sm">{entry.etymology}</p>
        </div>
      )}

      {entry.related_terms.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-700 dark:text-neutral-300 mb-2">Related Terms</h3>
          <div className="flex flex-wrap gap-2">
            {entry.related_terms.map((term, i) => (
              <span key={i} className="px-2 py-1 bg-aromanian-50 dark:bg-neutral-800 text-aromanian-700 dark:text-aromanian-300 text-sm rounded border border-aromanian-200 dark:border-neutral-700">
                {term}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
