/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 深灰黑主题色
        chalkboard: {
          50: '#4a4a4a',
          100: '#3d3d3d',
          200: '#333333',
          300: '#2a2a2a',
          400: '#222222',
          500: '#1a1a1a',  // 主背景色 - 偏灰的黑色
          600: '#151515',
          700: '#111111',
          800: '#0d0d0d',
          900: '#080808',
        },
        // 粉笔色
        chalk: {
          white: '#f5f5f0',      // 白色粉笔
          yellow: '#fde68a',     // 黄色粉笔
          pink: '#fca5a5',       // 粉色粉笔
          blue: '#93c5fd',       // 蓝色粉笔
          green: '#86efac',      // 绿色粉笔
          orange: '#fdba74',     // 橙色粉笔
        },
        // 保留兼容性
        primary: {
          50: '#f5f5f0',
          100: '#e8e8e0',
          200: '#d4d4c8',
          300: '#b8b8a8',
          400: '#9a9a88',
          500: '#f5f5f0',
          600: '#e0e0d8',
          700: '#c8c8bc',
          800: '#a8a898',
          900: '#888878',
        },
        dark: {
          50: '#f5f5f0',
          100: '#e8e8e0',
          200: '#d4d4c8',
          300: '#b8b8a8',
          400: '#8a9a8a',
          500: '#6a7a6a',
          600: '#4a5a4a',
          700: '#3a4a3a',
          800: '#2a3a2a',
          900: '#1a2a1a',
          950: '#0a1a0a',
        }
      },
      fontFamily: {
        sans: ['"Inter"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'chalk-write': 'chalkWrite 0.3s ease-out',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        chalkWrite: {
          '0%': { opacity: '0', transform: 'translateX(-10px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      },
      boxShadow: {
        'chalk': '2px 2px 0 rgba(245, 245, 240, 0.3)',
        'chalk-lg': '4px 4px 0 rgba(245, 245, 240, 0.2)',
      }
    },
  },
  plugins: [],
}
