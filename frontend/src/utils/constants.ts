// API基础配置
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// 应用配置
export const APP_CONFIG = {
  title: '量化回测系统',
  version: '1.0.0',
  author: 'Quantitative Team'
}

// 风险等级配置
export const RISK_LEVELS = {
  low: { text: '低风险', color: '#52c41a' },
  medium: { text: '中风险', color: '#faad14' },
  high: { text: '高风险', color: '#f5222d' }
}

// 市场配置
export const MARKETS = {
  'A股': { name: 'A股', icon: '🇨🇳' },
  '美股': { name: '美股', icon: '🇺🇸' }
}

// 策略类别配置
export const STRATEGY_CATEGORIES = {
  'dca': '定投类',
  'rotation': '轮动类',
  'momentum': '动量类',
  'mean_reversion': '均值回归类'
}