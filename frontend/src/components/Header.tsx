import { Link } from 'react-router-dom'

export default function Header() {
  return (
    <header className="bg-primary-700 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold hover:text-primary-200 transition">
            Dixi Ma Bunu
          </Link>
          <nav className="flex gap-6">
            <Link to="/" className="hover:text-primary-200 transition">
              Home
            </Link>
            <Link to="/search" className="hover:text-primary-200 transition">
              Search
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}
