/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          teal: '#0E7C86',
          tealDk: '#0A5F68',
          accent: '#10B981',
        },
        status: {
          scheduled: { bg: '#F1F5F9', fg: '#0F172A' },
          completed: { bg: '#D1FAE5', fg: '#065F46' },
          cancelled: { bg: '#FEE2E2', fg: '#991B1B' },
          rescheduled: { bg: '#FEF3C7', fg: '#92400E' },
        },
      },
      borderRadius: {
        xl: '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        modal: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      },
    },
  },
  plugins: [],
}
