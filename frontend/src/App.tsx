import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Search from './pages/Search'
import Word from './pages/Word'
import Browse from './pages/Browse'
import Header from './components/Header'

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/word/:id" element={<Word />} />
          <Route path="/browse/:letter" element={<Browse />} />
        </Routes>
      </main>
      <footer className="bg-gray-100 py-4 text-center text-sm text-gray-600">
        <p>Dixi Ma Bunu - Aromanian Dictionary</p>
        <p className="text-xs mt-1">Data from dixionline.net</p>
      </footer>
    </div>
  )
}

export default App
