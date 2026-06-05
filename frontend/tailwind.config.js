/** TRK OS — paleta preservada do original: neutral + emerald/amber/red, Inter. */
import colors from 'tailwindcss/colors'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: colors.neutral,
        success: colors.emerald,
        warning: colors.amber,
        danger: colors.red,
        ink: colors.neutral,
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 3px 0 rgb(0 0 0 / 0.04), 0 1px 2px -1px rgb(0 0 0 / 0.04)',
        float: '0 10px 30px -12px rgb(0 0 0 / 0.18)',
        modal: '0 20px 50px -12px rgb(0 0 0 / 0.25)',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { transform: 'translateY(12px)', opacity: '0' }, '100%': { transform: 'translateY(0)', opacity: '1' } },
        scaleIn: { '0%': { transform: 'scale(.96)', opacity: '0' }, '100%': { transform: 'scale(1)', opacity: '1' } },
        shimmer: { '100%': { transform: 'translateX(100%)' } },
      },
      animation: {
        'fade-in': 'fadeIn .25s ease-out',
        'slide-up': 'slideUp .35s cubic-bezier(0.16,1,0.3,1)',
        'scale-in': 'scaleIn .2s ease-out',
      },
    },
  },
  plugins: [],
}
