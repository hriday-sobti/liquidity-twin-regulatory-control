/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#F5F6F4',
        surface: '#FFFFFF',
        text: '#20262E',
        muted: '#667085',
        border: '#D9DEE5',
        accent: {
          DEFAULT: '#1E4D6B',
          hover: '#16384F',
          light: '#EBF2F7',
        },
        success: {
          DEFAULT: '#2E7D32',
          light: '#E8F5E9',
          border: '#A5D6A7',
        },
        warning: {
          DEFAULT: '#A15C00',
          light: '#FFF8E1',
          border: '#FFE082',
        },
        danger: {
          DEFAULT: '#B42318',
          light: '#FEE4E2',
          border: '#FECDCA',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'SFMono-Regular', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
