/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark-blue': '#0a1a2a',
        'dark-gray': '#9aa0a6',
      },
    },
  },
  plugins: [],
}

