import { describe, it, expect } from 'vitest'
import { render, screen } from '../test/test-utils'
import WordCard from './WordCard'
import { DictionaryEntry } from '../api/client'

const mockEntry: DictionaryEntry = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  headword: 'casã',
  pronunciation: 'ká-sə',
  part_of_speech: 'sf',
  inflections: 'casã, case',
  definition: 'Construcție pentru locuit',
  translation_ro: 'casă',
  translation_en: 'house',
  translation_fr: 'maison',
  etymology: 'Latin: casa',
  examples: ['Casã mari', 'Noi casã'],
  expressions: ['acasã'],
  related_terms: ['cãsuțã'],
  context: null,
  source: 'DDA',
  source_url: null,
}

describe('WordCard', () => {
  describe('compact mode', () => {
    it('renders headword', () => {
      render(<WordCard entry={mockEntry} compact />)
      expect(screen.getByText('casã')).toBeInTheDocument()
    })

    it('renders part of speech', () => {
      render(<WordCard entry={mockEntry} compact />)
      expect(screen.getByText('sf')).toBeInTheDocument()
    })

    it('renders English translation', () => {
      render(<WordCard entry={mockEntry} compact />)
      expect(screen.getByText('house')).toBeInTheDocument()
    })

    it('links to word page', () => {
      render(<WordCard entry={mockEntry} compact />)
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', `/word/${mockEntry.id}`)
    })
  })

  describe('full mode', () => {
    it('renders headword', () => {
      render(<WordCard entry={mockEntry} />)
      expect(screen.getByText('casã')).toBeInTheDocument()
    })

    it('renders pronunciation', () => {
      render(<WordCard entry={mockEntry} />)
      expect(screen.getByText('/ká-sə/')).toBeInTheDocument()
    })

    it('renders definition', () => {
      render(<WordCard entry={mockEntry} />)
      expect(screen.getByText('Construcție pentru locuit')).toBeInTheDocument()
    })

    it('renders all translations', () => {
      render(<WordCard entry={mockEntry} />)
      expect(screen.getByText('casă')).toBeInTheDocument()
      expect(screen.getByText('house')).toBeInTheDocument()
      expect(screen.getByText('maison')).toBeInTheDocument()
    })

    it('renders examples', () => {
      render(<WordCard entry={mockEntry} />)
      expect(screen.getByText('Casã mari')).toBeInTheDocument()
      expect(screen.getByText('Noi casã')).toBeInTheDocument()
    })

    it('renders etymology', () => {
      render(<WordCard entry={mockEntry} />)
      expect(screen.getByText('Latin: casa')).toBeInTheDocument()
    })

    it('renders related terms', () => {
      render(<WordCard entry={mockEntry} />)
      expect(screen.getByText('cãsuțã')).toBeInTheDocument()
    })
  })
})
