/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'serif': ['Georgia', 'Cambria', 'serif'],
        'sans': ['Helvetica', 'Arial', 'sans-serif'],
      },
      colors: {
        'wsj-gray': '#f0f0f0',
        'wsj-dark': '#333333',
        'wsj-accent': '#0066cc',
      },
    },
  },
  plugins: [],
}