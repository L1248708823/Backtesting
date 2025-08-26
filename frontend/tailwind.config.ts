import type { Config } from 'tailwindcss';

export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      // 色彩系统 - 基于设计规范
      colors: {
        // 主色调
        primary: {
          50: '#e6f4ff',
          100: '#bae0ff',
          200: '#91caff',
          300: '#69b1ff',
          400: '#4096ff',
          500: '#1890ff',  // 主色
          600: '#0958d9',
          700: '#003eb3',
          800: '#002c8c',
          900: '#001d66',
        },
        
        // 功能色彩
        success: {
          50: '#f6ffed',
          100: '#d9f7be',
          200: '#b7eb8f',
          300: '#95de64',
          400: '#73d13d',
          500: '#52c41a',  // 成功/盈利
          600: '#389e0d',
          700: '#237804',
          800: '#135200',
          900: '#092b00',
        },
        
        warning: {
          50: '#fffbe6',
          100: '#fff1b8',
          200: '#ffe58f',
          300: '#ffd666',
          400: '#ffc53d',
          500: '#faad14',  // 警告
          600: '#d48806',
          700: '#ad6800',
          800: '#874d00',
          900: '#613400',
        },
        
        error: {
          50: '#fff2f0',
          100: '#ffccc7',
          200: '#ffa39e',
          300: '#ff7875',
          400: '#ff4d4f',
          500: '#f5222d',  // 错误/亏损
          600: '#cf1322',
          700: '#a8071a',
          800: '#820014',
          900: '#5c0011',
        },
        
        // 金融专用色
        profit: '#52c41a',
        loss: '#f5222d',
        neutral: '#8c8c8c',
        
        // 灰度色系
        gray: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#f0f0f0',
          300: '#d9d9d9',
          400: '#bfbfbf',
          500: '#8c8c8c',
          600: '#595959',
          700: '#434343',
          800: '#262626',
          900: '#1f1f1f',
          950: '#141414',
        }
      },
      
      // 字体系统
      fontFamily: {
        'sans': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'Noto Sans', 'sans-serif'],
        'mono': ['SFMono-Regular', 'Consolas', 'Liberation Mono', 'Menlo', 'Courier', 'monospace'],
        'number': ['tabular-nums'], // 等宽数字
      },
      
      // 间距系统
      spacing: {
        '18': '4.5rem',   // 72px
        '88': '22rem',    // 352px
        '128': '32rem',   // 512px
      },
      
      // 断点系统
      screens: {
        'xs': '480px',
        'sm': '768px',
        'md': '1024px',
        'lg': '1280px',
        'xl': '1600px',
      },
      
      // 阴影系统
      boxShadow: {
        'sm': '0 1px 3px rgba(0, 0, 0, 0.12)',
        'md': '0 4px 12px rgba(0, 0, 0, 0.15)',
        'lg': '0 8px 24px rgba(0, 0, 0, 0.18)',
        'dark-sm': '0 1px 3px rgba(0, 0, 0, 0.24)',
        'dark-md': '0 4px 12px rgba(0, 0, 0, 0.30)',
        'dark-lg': '0 8px 24px rgba(0, 0, 0, 0.36)',
      },
      
      // 动画系统
      transitionTimingFunction: {
        'ease-out-quart': 'cubic-bezier(0.25, 1, 0.5, 1)',
        'ease-in-quart': 'cubic-bezier(0.5, 0, 0.75, 0)',
      },
      
      // 自定义动画
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
      },
    },
  },
  
  // 禁用 preflight 避免与 Ant Design 冲突
  corePlugins: {
    preflight: false,
  },
  
  // 深色模式配置
  darkMode: ['class', '[data-theme="dark"]'],
  
} satisfies Config;