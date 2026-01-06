import { Link } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'

export default function Header() {
  return (
    <header className="bg-aromanian-700 dark:bg-aromanian-900 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold hover:text-aromanian-200 transition">
            Dixi Ma Bunu
          </Link>
          <div className="flex items-center gap-6">
            <nav className="flex gap-6">
              <Link to="/" className="hover:text-aromanian-200 transition">
                Home
              </Link>
              <Link to="/search" className="hover:text-aromanian-200 transition">
                Search
              </Link>
            </nav>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  )
}
