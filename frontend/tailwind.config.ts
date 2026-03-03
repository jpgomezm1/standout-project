import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#faf9f7',
          100: '#f5f0eb',
          200: '#e8dfd6',
          300: '#d4c8ba',
          400: '#b8a898',
          500: '#a39383',
          600: '#8a7a6b',
          700: '#6e6054',
          800: '#574b40',
          900: '#2a2420',
          950: '#1a1714',
        },
        status: {
          danger: {
            light: '#fdf2f0',
            DEFAULT: '#c4756a',
            dark: '#8b3a30',
          },
          warning: {
            light: '#fdf6ec',
            DEFAULT: '#c9a24d',
            dark: '#7a5f1e',
          },
          info: {
            light: '#f0f3f7',
            DEFAULT: '#7a8fa8',
            dark: '#3d4f68',
          },
          success: {
            light: '#f2f6f2',
            DEFAULT: '#7a9c7a',
            dark: '#3d5e3d',
          },
        },
      },
      fontFamily: {
        sans: ['Roboto', 'system-ui', 'sans-serif'],
        display: ['Domine', 'Georgia', 'serif'],
      },
      borderRadius: {
        pill: '50px',
        card: '16px',
      },
      boxShadow: {
        card: '0 1px 3px rgba(42,36,32,0.04), 0 1px 2px rgba(42,36,32,0.02)',
        'card-hover':
          '0 4px 12px rgba(42,36,32,0.08), 0 2px 4px rgba(42,36,32,0.04)',
        sidebar: '4px 0 12px rgba(42,36,32,0.12)',
      },
    },
  },
  plugins: [],
};

export default config;
