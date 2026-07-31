/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'navy-dark': '#000F2E',
        navy: '#04132A',
        'teal-dark': '#072530',
        green: {
          DEFAULT: '#2A9C6F',
          dark: '#256F59',
        },
        surface: '#F8F7F5',
        'surface-warm': '#F8F4F1',
        'text-muted': '#5A7275',
        border: '#E1E4E0',
      },
      fontFamily: {
        sans: ['Manrope', 'Inter', 'Arial', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.8s ease-out forwards',
        'draw-line': 'drawLine 1.5s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        drawLine: {
          '0%': { strokeDashoffset: '1000' },
          '100%': { strokeDashoffset: '0' },
        },
      },
    },
  },
  plugins: [],
};
