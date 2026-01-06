import { describe, it, expect } from 'vitest'
import { render, screen } from '../test/test-utils'
import Header from './Header'

describe('Header', () => {
  it('renders the site title', () => {
    render(<Header />)
    expect(screen.getByText('Dixi Ma Bunu')).toBeInTheDocument()
  })

  it('has navigation links', () => {
    render(<Header />)
    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /search/i })).toBeInTheDocument()
  })

  it('has a theme toggle button', () => {
    render(<Header />)
    expect(screen.getByRole('button', { name: /switch to/i })).toBeInTheDocument()
  })

  it('links to correct routes', () => {
    render(<Header />)
    expect(screen.getByRole('link', { name: /home/i })).toHaveAttribute('href', '/')
    expect(screen.getByRole('link', { name: /search/i })).toHaveAttribute('href', '/search')
  })
})
