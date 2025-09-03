import api from './api'

/** 策略元数据信息 */
export interface StrategyMetadata {
  /** 策略唯一标识 */
  id: string
  /** 策略显示名称 */
  name: string
  /** 策略详细描述 */
  description: string
  /** 策略分类 */
  category: string
  /** 策略类型 - dca, rotation, mean_reversion等 */
  strategy_type: string
  /** 风险等级 - 低、中、高 */
  risk_level: string
  /** 支持的市场类型 - a_stock, us_stock等 */
  supported_markets: string[]
  /** 策略作者 */
  author: string
  /** 策略版本号 */
  version: string
  /** 创建日期 - YYYY-MM-DD格式，可选 */
  created_date?: string
  /** 策略标签 - 用于分类和搜索 */
  tags: string[]
  /** 策略特性列表 - 突出优势和特点 */
  features: string[]
  /** 参数定义列表 - 包含参数类型、默认值、验证规则等 */
  parameters: any[]
}

/** 策略完整信息 */
export interface Strategy {
  /** 策略元数据 */
  metadata: StrategyMetadata
  /** 策略状态 - available, disabled等 */
  status: string
  /** 使用次数统计 */
  usage_count: number
  /** 最后更新时间 - ISO格式，可选 */
  last_updated?: string
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