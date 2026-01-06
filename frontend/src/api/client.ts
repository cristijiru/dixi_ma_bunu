const API_BASE = '/api'

export interface DictionaryEntry {
  id: string
  headword: string
  pronunciation: string | null
  part_of_speech: string | null
  inflections: string | null
  definition: string | null
  translation_ro: string | null
  translation_en: string | null
  translation_fr: string | null
  etymology: string | null
  examples: string[]
  expressions: string[]
  related_terms: string[]
  context: string | null
  source: string | null
  source_url: string | null
}

export interface SearchResult {
  entry: DictionaryEntry
  score: number
  match_type: 'exact' | 'prefix' | 'contains' | 'fuzzy'
}

export interface Suggestion {
  headword: string
  part_of_speech: string | null
}

export interface LetterCount {
  letter: string
  count: number
}

export interface PosCount {
  part_of_speech: string
  count: number
}

export interface DictionaryStats {
  total_entries: number
  entries_by_letter: LetterCount[]
  entries_by_pos: PosCount[]
}

export interface ApiResponse<T> {
  data: T
  total?: number
}

async function fetchApi<T>(endpoint: string): Promise<ApiResponse<T>> {
  const response = await fetch(`${API_BASE}${endpoint}`)
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return response.json()
}

export async function search(
  query: string,
  options?: { lang?: string; pos?: string; limit?: number }
): Promise<SearchResult[]> {
  const params = new URLSearchParams({ q: query })
  if (options?.lang) params.set('lang', options.lang)
  if (options?.pos) params.set('pos', options.pos)
  if (options?.limit) params.set('limit', options.limit.toString())

  const response = await fetchApi<SearchResult[]>(`/search?${params}`)
  return response.data
}

export async function getWord(id: string): Promise<DictionaryEntry> {
  const response = await fetchApi<DictionaryEntry>(`/words/${id}`)
  return response.data
}

export async function getRandomWord(): Promise<DictionaryEntry> {
  const response = await fetchApi<DictionaryEntry>('/words/random')
  return response.data
}

export async function getLetters(): Promise<LetterCount[]> {
  const response = await fetchApi<LetterCount[]>('/letters')
  return response.data
}

export async function getByLetter(
  letter: string,
  options?: { limit?: number; offset?: number }
): Promise<{ entries: DictionaryEntry[]; total: number }> {
  const params = new URLSearchParams()
  if (options?.limit) params.set('limit', options.limit.toString())
  if (options?.offset) params.set('offset', options.offset.toString())

  const paramStr = params.toString()
  const response = await fetchApi<DictionaryEntry[]>(
    `/letters/${letter}${paramStr ? `?${paramStr}` : ''}`
  )
  return { entries: response.data, total: response.total ?? 0 }
}

export async function getSuggestions(query: string, limit = 10): Promise<Suggestion[]> {
  const params = new URLSearchParams({ q: query, limit: limit.toString() })
  const response = await fetchApi<Suggestion[]>(`/suggestions?${params}`)
  return response.data
}

export async function getStats(): Promise<DictionaryStats> {
  const response = await fetchApi<DictionaryStats>('/stats')
  return response.data
}
