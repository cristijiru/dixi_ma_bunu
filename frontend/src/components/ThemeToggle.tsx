import { useTheme } from '../hooks/useTheme'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <button
      onClick={toggleTheme}
      className="relative flex items-center w-16 h-8 rounded-full bg-white/20 hover:bg-white/30 transition p-1"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      {/* Sun icon */}
      <span className={`absolute left-1.5 transition-opacity ${isDark ? 'opacity-50' : 'opacity-100'}`}>
        <svg className="w-5 h-5 text-yellow-300" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
            stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" fill="none" />
        </svg>
      </span>

      {/* Moon icon */}
      <span className={`absolute right-1.5 transition-opacity ${isDark ? 'opacity-100' : 'opacity-50'}`}>
        <svg className="w-5 h-5 text-blue-200" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      </span>

      {/* Sliding indicator */}
      <span
        className={`absolute w-6 h-6 bg-white rounded-full shadow-md transition-transform duration-200 ${
          isDark ? 'translate-x-8' : 'translate-x-0'
        }`}
      />
    </button>
  )
}
