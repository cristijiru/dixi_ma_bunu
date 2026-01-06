/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Aromanian wine/maroon - deeper, less bright
        aromanian: {
          50: '#faf5f5',
          100: '#f5eaea',
          200: '#ebd4d4',
          300: '#d4a0a0',
          400: '#cc5f5f',
          500: '#a85555',
          600: '#8b4545',
          700: '#733838',
          800: '#5f3030',
          900: '#4d2828',
          950: '#2a1414',
        },
        // Keep primary as alias
        primary: {
          50: '#faf5f5',
          100: '#f5eaea',
          200: '#ebd4d4',
          300: '#d4a0a0',
          400: '#cc5f5f',
          500: '#a85555',
          600: '#8b4545',
          700: '#733838',
          800: '#5f3030',
          900: '#4d2828',
          950: '#2a1414',
        },
        // Off-white / cream colors
        cream: {
          50: '#fefdfb',
          100: '#fdf9f3',
          200: '#faf3e8',
          300: '#f5ead8',
          400: '#eddcc0',
        },
      },
    },
  },
  plugins: [],
}
