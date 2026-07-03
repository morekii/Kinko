/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#1a1a1a',
          alt: '#121212',
        },
        accent: {
          DEFAULT: '#2563eb',
          hover: '#3b82f6',
        },
      },
      borderRadius: {
        card: '1.25rem',
      },
    },
  },
  plugins: [],
}