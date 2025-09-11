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

/** 回测请求配置 - 与后端BacktestRequest模型对应 */
export interface BacktestRequest {
  /** 策略ID - 对应后端注册的策略标识 */
  strategy_id: string
  /** 策略参数 - 具体参数由各策略定义 */
  parameters: Record<string, any>
  /** 回测开始日期 - YYYY-MM-DD格式 */
  start_date: string
  /** 回测结束日期 - YYYY-MM-DD格式 */
  end_date: string
  /** 初始资金 - 默认10000元 */
  initial_cash: number
}

export interface BacktestStatus {
  task_id: string
  status: string
  progress: number
  message: string
  created_at: string
  completed_at?: string
}

/** 回测结果 - 与后端BacktestResult模型对应 */
export interface BacktestResult {
  /** 策略ID */
  strategy_id: string
  /** 策略参数 */
  parameters: Record<string, any>
  /** 回测开始日期 */
  start_date: string
  /** 回测结束日期 */
  end_date: string
  /** 初始资金 */
  initial_cash: number
  /** 最终资产值 */
  final_value: number
  /** 总收益率(%) */
  total_return: number
  /** 总交易次数 */
  total_trades: number
  /** 性能指标详情 */
  performance_metrics: Record<string, any>
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

// 回测相关API - 与后端接口完全对应
export const backtestService = {
  /** 执行回测 - 对应后端 /api/v1/backtest/run */
  runBacktest: (request: BacktestRequest): Promise<BacktestResult> => 
    api.post('/backtest/run', request),

  /** DCA策略专用回测方法 - 简化DCA策略调用，支持止盈策略 */
  runDCABacktest: (params: {
    symbol: string
    investment_amount: number
    frequency_days: number
    start_date: string
    end_date: string
    initial_cash: number
    exit_strategy?: string
    profit_target?: number
    time_limit_months?: number
    batch_exit_levels?: number[]
    batch_exit_ratios?: number[]
  }): Promise<BacktestResult> => {
    return backtestService.runBacktest({
      strategy_id: 'dca_strategy',
      parameters: {
        symbol: params.symbol,
        investment_amount: params.investment_amount,
        frequency_days: params.frequency_days,
        exit_strategy: params.exit_strategy || 'hold',
        profit_target: params.profit_target,
        time_limit_months: params.time_limit_months,
        batch_exit_levels: params.batch_exit_levels,
        batch_exit_ratios: params.batch_exit_ratios
      },
      start_date: params.start_date,
      end_date: params.end_date,
      initial_cash: params.initial_cash
    })
  }
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

/** 市场数据接口类型定义 */
export interface MarketIndexData {
  /** 指数值 */
  value: number | null
  /** 涨跌幅(%) */
  change_pct: number | null
  /** 涨跌额 */
  change_amount?: number | null
  /** 错误信息 */
  error?: string
  /** 时间戳 */
  timestamp: string
}

export interface VIXLevelData {
  /** VIX数值 */
  value: number | null
  /** 危险等级文字 */
  level: string
  /** 颜色标识 */
  color: string
  /** 错误信息 */
  error?: string
  /** 时间戳 */
  timestamp: string
}

export interface MarketDashboardData {
  /** 上证指数 */
  shanghai_index: MarketIndexData
  /** 纳指 */
  nasdaq_index: MarketIndexData
  /** VIX恐慌指数 */
  vix_level: VIXLevelData
  /** 热门ETF列表 */
  hot_etfs: string[]
  /** 时间戳 */
  timestamp: string
}

// 市场数据相关API
export const marketService = {
  /** 获取市场仪表盘数据 */
  getDashboard: (): Promise<MarketDashboardData> => 
    api.get('/market/dashboard'),

  /** 测试市场数据获取 */
  testMarketData: () => 
    api.get('/market/test')
}