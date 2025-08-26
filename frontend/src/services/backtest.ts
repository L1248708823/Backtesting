import api from './api'

export interface Strategy {
  id: string
  name: string
  description: string
  category: string
  risk_level: string
  supported_markets: string[]
  parameters: Record<string, any>
}

export interface BacktestConfig {
  strategy_id: string
  parameters: Record<string, any>
  start_date: string
  end_date: string
  initial_capital: number
  commission: number
  slippage: number
}

export interface BacktestStatus {
  task_id: string
  status: string
  progress: number
  message: string
  created_at: string
  completed_at?: string
}

export interface BacktestResult {
  task_id: string
  strategy_id: string
  config: BacktestConfig
  results: Record<string, any>
  performance_metrics: Record<string, number>
  created_at: string
}

// 策略相关API
export const strategyService = {
  // 获取所有策略
  getStrategies: (): Promise<Strategy[]> => 
    api.get('/strategies/'),

  // 获取特定策略
  getStrategy: (strategyId: string): Promise<Strategy> => 
    api.get(`/strategies/${strategyId}`)
}

// 回测相关API
export const backtestService = {
  // 启动回测
  startBacktest: (config: BacktestConfig): Promise<{ task_id: string; message: string }> => 
    api.post('/backtest/start', config),

  // 获取回测状态
  getBacktestStatus: (taskId: string): Promise<BacktestStatus> => 
    api.get(`/backtest/status/${taskId}`),

  // 获取回测结果
  getBacktestResult: (taskId: string): Promise<BacktestResult> => 
    api.get(`/backtest/result/${taskId}`)
}

// 数据相关API
export const dataService = {
  // 获取数据源状态
  getDataSources: () => 
    api.get('/data/sources'),

  // 更新数据
  updateData: () => 
    api.post('/data/update'),

  // 检查数据健康状态
  checkDataHealth: () => 
    api.get('/data/health')
}