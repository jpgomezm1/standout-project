import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        /* ── Sidebar ── */
        sidebar: {
          bg: '#111827',
          text: '#9CA3AF',
          'text-hover': '#F9FAFB',
          'active-bg': '#1E3A8A',
          'active-text': '#FFFFFF',
          border: '#1F2937',
          label: '#4B5563',
        },
        /* ── Page / Surfaces ── */
        page: '#F1F5F9',
        card: {
          bg: '#FFFFFF',
          border: '#E2E8F0',
        },
        /* ── Typography ── */
        text: {
          primary: '#0F172A',
          secondary: '#475569',
          muted: '#94A3B8',
          link: '#3B4FE0',
        },
        /* ── Indigo (brand accent) ── */
        indigo: {
          900: '#1E3A8A',
          700: '#3B4FE0',
          300: '#A5B4FC',
          subtle: '#EEF2FF',
        },
        /* ── Teal ── */
        teal: {
          600: '#0D9488',
          subtle: '#CCFBF1',
        },
        /* ── Green ── */
        green: {
          500: '#22C55E',
          600: '#16A34A',
          subtle: '#F0FDF4',
        },
        /* ── Slate neutrals ── */
        slate: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          400: '#94A3B8',
          600: '#475569',
          900: '#0F172A',
        },
        /* ── Status badges ── */
        badge: {
          'danger-bg': '#FEF2F2',
          'danger-text': '#DC2626',
          'danger-border': '#FECACA',
          'progress-bg': '#EEF2FF',
          'progress-text': '#3B4FE0',
          'progress-border': '#C7D2FE',
          'acknowledged-bg': '#F5F3FF',
          'acknowledged-text': '#7C3AED',
          'acknowledged-border': '#DDD6FE',
          'resolved-bg': '#F0FDF4',
          'resolved-text': '#16A34A',
          'resolved-border': '#BBF7D0',
          'sent-bg': '#EEF2FF',
          'sent-text': '#3B4FE0',
          'sent-border': '#C7D2FE',
          'priority-high-bg': '#FFF7ED',
          'priority-high-text': '#C2410C',
          'priority-high-border': '#FED7AA',
          'priority-medium-bg': '#FEFCE8',
          'priority-medium-text': '#A16207',
          'priority-medium-border': '#FEF08A',
          'inventory-low-bg': '#CCFBF1',
          'inventory-low-text': '#0D9488',
          'inventory-ok-bg': '#F0FDF4',
          'inventory-ok-text': '#16A34A',
        },
      },
      fontFamily: {
        sans: ['Roboto', 'system-ui', 'sans-serif'],
        display: ['Domine', 'Georgia', 'serif'],
      },
      borderRadius: {
        pill: '999px',
        card: '12px',
      },
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,0.06)',
        'card-hover': '0 10px 25px rgba(0,0,0,0.08), 0 4px 10px rgba(0,0,0,0.04)',
        modal: '0 20px 60px rgba(0,0,0,0.2)',
      },
    },
  },
  plugins: [],
};

export default config;
