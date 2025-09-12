import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Button, Table, Card, Statistic, Row, Col, Tooltip } from 'antd'
import { ColumnType } from 'antd/es/table'
import TerminalHeader from '@/components/TerminalHeader'
import DCACharts from '@/components/DCACharts'

interface BacktestResult {
  /** 策略唯一标识 */
  strategy_id: string
  /** 策略参数配置 */
  parameters: Record<string, any>
  /** 回测开始日期 YYYY-MM-DD */
  start_date: string
  /** 回测结束日期 YYYY-MM-DD */
  end_date: string
  /** 初始资金(元) */
  initial_cash: number
  /** 最终资产价值(元) */
  final_value: number
  /** 总收益率(%) */
  total_return: number
  /** 总交易次数 */
  total_trades: number
  performance_metrics: {
    // 基础指标
    /** 初始资金(元) */
    start_value: number
    /** 最终资产价值(元) */
    end_value: number
    /** 总收益率(%) - 公式: (期末-期初)/期初×100% */
    total_return: number
    /** 年化收益率(%) - 复合增长率，考虑复利效应 */
    annual_return: number
    /** 投资总天数 */
    total_days: number
    
    // 交易统计
    /** 总交易笔数 */
    total_trades: number
    /** 总订单数 */
    total_orders: number
    /** 买入订单数 */
    buy_orders: number
    /** 卖出订单数 */
    sell_orders: number
    
    // 风险指标
    /** 年化波动率(%) - 公式: 日收益率标准差×√252×100%，衡量收益不确定性 */
    volatility: number
    /** 最大回撤(%) - 从峰值到谷值的最大下跌幅度 */
    max_drawdown: number
    /** 夏普比率 - 风险调整后收益，数值越高越好(大于1为优秀) */
    sharpe_ratio: number
    /** 最大回撤持续期(天) - 最长的亏损持续时间 */
    max_drawdown_duration: number
    
    // DCA特殊数据
    /** 定投执行记录 - 每次买入的详细信息 */
    investment_records?: Array<{
      /** 买入日期 YYYY-MM-DD */
      date: string
      /** 定投期数(第几次) */
      round: number
      /** 买入价格(元/份) */
      price: number
      /** 买入份额数 */
      shares: number
      /** 实际投入金额(元) */
      amount: number
      /** 目标投入金额(元) */
      target_amount: number
      /** 当时总资产价值(元) */
      market_value: number
    }>
    /** 累计投入总金额(元) */
    total_invested?: number
    /** 累计持有份额总数 */
    total_shares?: number
    /** 平均持仓成本(元/份) - 总投入÷总份额 */
    average_cost?: number
    /** 成本摊薄效果(%) - 相比均价买入的成本优势 */
    cost_reduction_effect?: number
    /** 投资执行效率(%) - 实际投资与计划投资的比例 */
    investment_efficiency?: number
    /** 当前持仓市值(元) */
    current_position_value?: number
    /** 未实现盈亏(元) - 当前市值减去投入成本 */
    unrealized_pnl?: number
    /** 未实现收益率(%) */
    unrealized_return?: number
    /** 价格波动区间信息 */
    price_range?: {
      /** 定投期间最低价(元) */
      min_price: number
      /** 定投期间最高价(元) */
      max_price: number
      /** 价格波动幅度(%) - (最高-最低)/最低×100% */
      price_volatility: number
    }
    
    // 时间序列数据
    /** 每日资产净值序列 - 用于绘制净值曲线 */
    daily_values: number[]
    /** 每日收益率序列 - 用于计算波动率 */
    daily_returns: number[]
    /** 每日日期序列 - 对应净值和收益率的时间轴 */
    daily_dates: string[]
    /** 买入交易记录 - 详细的买入执行信息 */
    buy_records: Array<any>
    /** 卖出交易记录 - 详细的卖出执行信息 */
    sell_records: Array<any>
    
    // 基准对比数据  
    /** 基准对比分析 - DCA止盈策略 vs DCA纯持有对比 */
    benchmark_comparison?: {
      /** DCA纯持有投资金额(元) */
      benchmark_investment: number
      /** DCA纯持有份额数 */
      benchmark_shares: number
      /** DCA纯持有平均成本(元/份) */
      benchmark_average_cost: number
      /** DCA纯持有当前价值(元) */
      benchmark_current_value: number
      /** DCA纯持有收益率(%) */
      benchmark_return: number
      /** 止盈策略超额收益(%) - 止盈收益率减去纯持有收益率 */
      return_difference: number
      /** 因止盈减少的份额数 */
      shares_difference: number
      /** 当前价值差异(元) */
      value_difference: number
      /** 止盈策略是否更优 */
      exit_strategy_better: boolean
      /** 是否为相同策略（纯持有vs纯持有） */
      is_same_strategy: boolean
      /** 当前止盈策略类型 */
      current_exit_strategy: string
      /** 策略描述 */
      strategy_description: string
      /** 期间价格波动率(%) */
      price_volatility_during_period: number
    }
  }
}

interface LocationState {
  backtestResult: BacktestResult
  timestamp: number
}

const DCAResult: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as LocationState | null
  const result = state?.backtestResult

  if (!result) {
    return (
      <div className="min-h-screen bg-black text-green-400 font-mono flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">⚠️</div>
          <div className="text-xl mb-4">未找到回测结果数据</div>
          <Button onClick={() => navigate('/dca/config')} className="ninja-button">
            返回配置页面
          </Button>
        </div>
      </div>
    )
  }

  const metrics = result.performance_metrics

  // 定投明细表格列定义
  const investmentColumns: ColumnType<any>[] = [
    {
      title: '期数',
      dataIndex: 'round',
      key: 'round',
      width: 60,
      render: (value: number) => <span className="text-green-400">#{value}</span>
    },
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      width: 120,
    },
    {
      title: '买入价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (value: number) => <span className="text-yellow-400">¥{value.toFixed(2)}</span>
    },
    {
      title: '买入份额',
      dataIndex: 'shares',
      key: 'shares',
      width: 100,
      render: (value: number) => <span className="text-cyan-400">{value}</span>
    },
    {
      title: '实际金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 120,
      render: (value: number) => <span className="text-green-400">¥{value.toFixed(2)}</span>
    },
    {
      title: '当时总资产',
      dataIndex: 'market_value',
      key: 'market_value',
      width: 120,
      render: (value: number) => <span className="text-gray-300">¥{value.toLocaleString()}</span>
    }
  ]

  // 卖出记录表格列定义
  const sellColumns: ColumnType<any>[] = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      width: 120,
    },
    {
      title: '卖出价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (value: number) => <span className="text-orange-400">¥{value.toFixed(2)}</span>
    },
    {
      title: '卖出份额',
      dataIndex: 'size',
      key: 'size',
      width: 100,
      render: (value: number) => <span className="text-red-400">{value}</span>
    },
    {
      title: '卖出金额',
      dataIndex: 'value',
      key: 'value',
      width: 120,
      render: (value: number) => <span className="text-red-400">¥{Math.abs(value).toFixed(2)}</span>
    },
    {
      title: '手续费',
      dataIndex: 'commission',
      key: 'commission',
      width: 100,
      render: (value: number) => <span className="text-gray-400">¥{value.toFixed(2)}</span>
    },
    {
      title: '净收入',
      dataIndex: 'value',
      key: 'net_value',
      width: 120,
      render: (value: number, record: any) => {
        const netValue = Math.abs(value) - (record.commission || 0)
        return <span className="text-yellow-400">¥{netValue.toFixed(2)}</span>
      }
    }
  ]

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono">
      <div className="pb-8 px-8 overflow-y-auto">
        <TerminalHeader
          title="DCA回测结果分析终端"
          hostname="dca-result"
          taskDescription="任务完成 - 专业定投分析报告"
        />

        <div className="max-w-7xl mx-auto space-y-6">
          
          {/* 核心指标概览 */}
          <div className="border border-green-400/30 p-6">
            <div className="text-green-400 mb-4 text-lg">[CORE_METRICS] 核心指标总览 📊</div>
            
            <Row gutter={[16, 16]}>
              <Col span={6}>
                <Card className="bg-black border-green-400/30 ninja-card">
                  <Statistic
                    title={
                      <Tooltip 
                        title={
                          <div className="text-xs">
                            <div className="font-bold mb-1">总收益率</div>
                            <div>公式: (期末价值 - 期初价值) / 期初价值 × 100%</div>
                            <div>参考: &gt;0%为盈利, &gt;10%为良好, &gt;20%为优秀</div>
                          </div>
                        }
                        placement="top"
                      >
                        <span className="text-gray-400 cursor-help border-b border-dotted border-gray-500">总收益率</span>
                      </Tooltip>
                    }
                    value={result.total_return}
                    precision={2}
                    suffix="%"
                    valueStyle={{ color: result.total_return >= 0 ? '#22c55e' : '#ef4444' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card className="bg-black border-green-400/30 ninja-card">
                  <Statistic
                    title={
                      <Tooltip 
                        title={
                          <div className="text-xs">
                            <div className="font-bold mb-1">年化收益率</div>
                            <div>公式: (期末价值/期初价值)^(1/投资年数) - 1</div>
                            <div>含义: 复合年增长率，考虑复利效应</div>
                            <div>参考: &gt;5%为良好, &gt;10%为优秀, &gt;15%为杰出</div>
                          </div>
                        }
                        placement="top"
                      >
                        <span className="text-gray-400 cursor-help border-b border-dotted border-gray-500">年化收益率</span>
                      </Tooltip>
                    }
                    value={metrics?.annual_return || 0}
                    precision={2}
                    suffix="%"
                    valueStyle={{ color: '#f59e0b' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card className="bg-black border-green-400/30 ninja-card">
                  <Statistic
                    title={
                      <Tooltip 
                        title={
                          <div className="text-xs">
                            <div className="font-bold mb-1">最大回撤</div>
                            <div>含义: 从峰值到谷值的最大下跌幅度</div>
                            <div>衡量: 投资风险和损失控制能力</div>
                            <div>参考: &lt;5%为低风险, &lt;15%为中风险, &gt;20%为高风险</div>
                          </div>
                        }
                        placement="top"
                      >
                        <span className="text-gray-400 cursor-help border-b border-dotted border-gray-500">最大回撤</span>
                      </Tooltip>
                    }
                    value={metrics?.max_drawdown || 0}
                    precision={2}
                    suffix="%"
                    valueStyle={{ color: '#ef4444' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card className="bg-black border-green-400/30 ninja-card">
                  <Statistic
                    title={
                      <Tooltip 
                        title={
                          <div className="text-xs">
                            <div className="font-bold mb-1">夏普比率</div>
                            <div>公式: (投资收益率 - 无风险利率) / 波动率</div>
                            <div>含义: 风险调整后收益，数值越高越好</div>
                            <div>参考: &gt;1为优秀, &gt;2为杰出, &lt;0为不佳</div>
                          </div>
                        }
                        placement="top"
                      >
                        <span className="text-gray-400 cursor-help border-b border-dotted border-gray-500">夏普比率</span>
                      </Tooltip>
                    }
                    value={metrics?.sharpe_ratio || 0}
                    precision={2}
                    valueStyle={{ color: '#06b6d4' }}
                  />
                </Card>
              </Col>
            </Row>

            <Row gutter={[16, 16]} className="mt-4">
              <Col span={6}>
                <Card className="bg-black border-green-400/30 ninja-card">
                  <Statistic
                    title={
                      <Tooltip 
                        title={
                          <div className="text-xs">
                            <div className="font-bold mb-1">年化波动率</div>
                            <div>公式: 日收益率标准差 × √252 × 100%</div>
                            <div>含义: 衡量收益的不确定性，数值越高风险越大</div>
                            <div>参考: &lt;15%为低风险, 15-25%为中风险, &gt;25%为高风险</div>
                          </div>
                        }
                        placement="top"
                      >
                        <span className="text-gray-400 cursor-help border-b border-dotted border-gray-500">波动率</span>
                      </Tooltip>
                    }
                    value={metrics?.volatility || 0}
                    precision={2}
                    suffix="%"
                    valueStyle={{ color: '#8b5cf6' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card className="bg-black border-green-400/30 ninja-card">
                  <Statistic
                    title={
                      <Tooltip 
                        title={
                          <div className="text-xs">
                            <div className="font-bold mb-1">定投次数</div>
                            <div>含义: 实际执行的买入次数</div>
                            <div>影响: 次数越多，分散效果越好</div>
                            <div>参考: 月投12次/年，周投52次/年</div>
                          </div>
                        }
                        placement="top"
                      >
                        <span className="text-gray-400 cursor-help border-b border-dotted border-gray-500">定投次数</span>
                      </Tooltip>
                    }
                    value={result.total_trades}
                    valueStyle={{ color: '#22c55e' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card className="bg-black border-green-400/30 ninja-card">
                  <Statistic
                    title={
                      <Tooltip 
                        title={
                          <div className="text-xs">
                            <div className="font-bold mb-1">累计投入</div>
                            <div>含义: 定投期间投入的总金额</div>
                            <div>计算: 各期实际投入金额之和</div>
                            <div>注意: 可能因价格不整除略小于计划投入</div>
                          </div>
                        }
                        placement="top"
                      >
                        <span className="text-gray-400 cursor-help border-b border-dotted border-gray-500">累计投入</span>
                      </Tooltip>
                    }
                    value={metrics?.total_invested || 0}
                    precision={0}
                    prefix="¥"
                    valueStyle={{ color: '#f59e0b' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card className="bg-black border-green-400/30 ninja-card">
                  <Statistic
                    title={
                      <Tooltip 
                        title={
                          <div className="text-xs">
                            <div className="font-bold mb-1">平均成本</div>
                            <div>公式: 累计投入金额 ÷ 累计持有份额</div>
                            <div>含义: 定投的平均买入价格</div>
                            <div>优势: 通常低于算术平均价格</div>
                          </div>
                        }
                        placement="top"
                      >
                        <span className="text-gray-400 cursor-help border-b border-dotted border-gray-500">平均成本</span>
                      </Tooltip>
                    }
                    value={metrics?.average_cost || 0}
                    precision={2}
                    prefix="¥"
                    valueStyle={{ color: '#06b6d4' }}
                  />
                </Card>
              </Col>
            </Row>
          </div>

          {/* DCA策略特殊分析 */}
          <div className="border border-green-400/30 p-6">
            <div className="text-green-400 mb-4 text-lg">[DCA_ANALYSIS] DCA策略效果分析 💡</div>
            
            <Row gutter={[24, 16]}>
              <Col span={12}>
                <div className="space-y-4">
                  <div>
                    <div className="text-gray-400 text-sm mb-1">成本摊薄效果</div>
                    <div className="text-2xl">
                      <span className={`${(metrics?.cost_reduction_effect || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {(metrics?.cost_reduction_effect || 0) >= 0 ? '+' : ''}
                        {(metrics?.cost_reduction_effect || 0).toFixed(2)}%
                      </span>
                    </div>
                    <div className="text-gray-500 text-xs">相比均价买入的成本优势</div>
                  </div>
                  
                  <div>
                    <div className="text-gray-400 text-sm mb-1">投资执行效率</div>
                    <div className="text-2xl text-cyan-400">
                      {(metrics?.investment_efficiency || 0).toFixed(1)}%
                    </div>
                    <div className="text-gray-500 text-xs">实际投资与计划投资的比例</div>
                  </div>
                </div>
              </Col>
              
              <Col span={12}>
                <div className="space-y-4">
                  <div>
                    <div className="text-gray-400 text-sm mb-1">价格区间</div>
                    <div className="text-sm">
                      <div>最低价: <span className="text-green-400">¥{metrics?.price_range?.min_price?.toFixed(2) || 0}</span></div>
                      <div>最高价: <span className="text-red-400">¥{metrics?.price_range?.max_price?.toFixed(2) || 0}</span></div>
                      <div>价格波动: <span className="text-yellow-400">{metrics?.price_range?.price_volatility?.toFixed(2) || 0}%</span></div>
                    </div>
                  </div>

                  <div>
                    <div className="text-gray-400 text-sm mb-1">持仓分析</div>
                    <div className="text-sm">
                      <div>持有份额: <span className="text-cyan-400">{metrics?.total_shares || 0}</span></div>
                      <div>未实现盈亏: <span className={`${(metrics?.unrealized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {(metrics?.unrealized_pnl || 0) >= 0 ? '+' : ''}¥{(metrics?.unrealized_pnl || 0).toFixed(2)}
                      </span></div>
                    </div>
                  </div>
                </div>
              </Col>
            </Row>
          </div>

          {/* 基准对比分析 - 只有非纯持有策略才显示 */}
          {metrics?.benchmark_comparison && !metrics.benchmark_comparison.is_same_strategy && (
            <div className="border border-green-400/30 p-6">
              <div className="text-green-400 mb-4 text-lg">
                [BENCHMARK] 策略对比分析 ⚖️
                <span className="text-gray-400 text-sm ml-2">
                  当前策略: {metrics.benchmark_comparison.strategy_description || '未知'}
                </span>
              </div>
              
              
              <Row gutter={[24, 16]}>
                <Col span={12}>
                  <div className="bg-blue-400/10 p-4 rounded border border-blue-400/20">
                    <div className="text-blue-400 text-sm mb-3 font-bold">
                      📈 DCA纯持有策略
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">平均成本:</span>
                        <span className="text-blue-400">¥{metrics.benchmark_comparison.benchmark_average_cost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">持有份额:</span>
                        <span className="text-blue-400">{metrics.benchmark_comparison.benchmark_shares.toFixed(0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">累计投入:</span>
                        <span className="text-blue-400">¥{metrics.benchmark_comparison.benchmark_investment.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">当前价值:</span>
                        <span className="text-blue-400">¥{metrics.benchmark_comparison.benchmark_current_value.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between border-t border-blue-400/20 pt-2">
                        <span className="text-gray-400 font-bold">收益率:</span>
                        <span className={`font-bold ${metrics.benchmark_comparison.benchmark_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {metrics.benchmark_comparison.benchmark_return >= 0 ? '+' : ''}{metrics.benchmark_comparison.benchmark_return.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </Col>
                
                <Col span={12}>
                  <div className="bg-green-400/10 p-4 rounded border border-green-400/20">
                    <div className="text-green-400 text-sm mb-3 font-bold">
                      🔄 DCA止盈策略
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">平均成本:</span>
                        <span className="text-green-400">¥{metrics.average_cost?.toFixed(2) || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">持有份额:</span>
                        <span className="text-green-400">{metrics.total_shares || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">累计投入:</span>
                        <span className="text-green-400">¥{metrics.total_invested?.toLocaleString() || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">当前价值:</span>
                        <span className="text-green-400">¥{result.final_value.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between border-t border-green-400/20 pt-2">
                        <span className="text-gray-400 font-bold">收益率:</span>
                        <span className={`font-bold ${result.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {result.total_return >= 0 ? '+' : ''}{result.total_return.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </Col>
              </Row>

              {/* 对比结论 */}
              <div className="mt-4 p-4 bg-gray-800/50 rounded border border-gray-600/30">
                <div className="text-center">
                  <div className="text-lg mb-2">
                    {metrics.benchmark_comparison.return_difference === 0 ? (
                      <span className="text-gray-400">📊 两种策略表现相同</span>
                    ) : metrics.benchmark_comparison.exit_strategy_better ? (
                      <span className="text-green-400">🎯 止盈策略表现更优！</span>
                    ) : (
                      <span className="text-yellow-400">📊 纯持有策略表现更好</span>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                    <div className="text-center">
                      <div className="text-gray-400">超额收益</div>
                      <div className={`text-lg font-bold ${
                        metrics.benchmark_comparison.return_difference === 0 ? 'text-gray-400' :
                        metrics.benchmark_comparison.return_difference > 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {metrics.benchmark_comparison.return_difference === 0 ? '0.00' : 
                         (metrics.benchmark_comparison.return_difference >= 0 ? '+' : '') + 
                         metrics.benchmark_comparison.return_difference.toFixed(2)}%
                      </div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-gray-400">减持份额</div>
                      <div className="text-lg font-bold text-orange-400">
                        {metrics.benchmark_comparison.shares_difference.toFixed(0)}
                      </div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-gray-400">价值差异</div>
                      <div className={`text-lg font-bold ${
                        metrics.benchmark_comparison.value_difference === 0 ? 'text-gray-400' :
                        metrics.benchmark_comparison.value_difference > 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {metrics.benchmark_comparison.value_difference === 0 ? '¥0' :
                         (metrics.benchmark_comparison.value_difference >= 0 ? '+' : '') + 
                         '¥' + Math.abs(metrics.benchmark_comparison.value_difference).toFixed(0)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-gray-500 text-xs mt-3">
                    💡 {metrics.benchmark_comparison.return_difference === 0 
                        ? '策略未执行止盈操作，与纯持有效果相同' 
                        : metrics.benchmark_comparison.exit_strategy_better 
                          ? '止盈策略通过适时退出获得了额外收益'
                          : '在上涨趋势中，纯持有策略可能获得更多收益'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 定投明细记录 */}
          {metrics?.investment_records && metrics.investment_records.length > 0 && (
            <div className="border border-green-400/30 p-6">
              <div className="text-green-400 mb-4 text-lg">[INVESTMENT_LOG] 定投执行记录 📋</div>
              
              <Table
                columns={investmentColumns}
                dataSource={metrics.investment_records}
                rowKey="round"
                pagination={{
                  pageSize: 10,
                  className: 'ninja-pagination'
                }}
                className="ninja-table"
                size="small"
              />
            </div>
          )}

          {/* 卖出记录 */}
          {metrics?.sell_records && metrics.sell_records.length > 0 && (
            <div className="border border-green-400/30 p-6">
              <div className="text-green-400 mb-4 text-lg">[SELL_LOG] 止盈卖出记录 💰</div>
              
              <div className="mb-4 text-gray-400 text-sm">
                📊 策略执行的卖出操作记录，包含止盈、分批止盈等退出行为
              </div>
              
              <Table
                columns={sellColumns}
                dataSource={metrics.sell_records}
                rowKey={(record, index) => `sell-${index}`}
                pagination={{
                  pageSize: 10,
                  className: 'ninja-pagination'
                }}
                className="ninja-table"
                size="small"
              />
            </div>
          )}

          {/* 可视化分析图表 */}
          <div className="border border-green-400/30 p-6">
            <div className="text-green-400 mb-4 text-lg">[CHARTS] 可视化分析 📈</div>
            
            <DCACharts
              daily_prices={metrics?.daily_prices || []}
              daily_portfolio_values={metrics?.daily_portfolio_values || []}
              daily_returns={metrics?.daily_returns || []}
              daily_dates={metrics?.daily_dates || []}
              investment_records={metrics?.investment_records || []}
              sell_records={metrics?.sell_records || []}
            />
          </div>

          {/* 操作按钮 */}
          <div className="border border-green-400/30 p-6 text-center">
            <div className="text-green-400 mb-4 text-lg">[ACTIONS] 下一步操作 🎯</div>
            
            <div className="flex justify-center gap-4">
              <Button
                onClick={() => navigate('/dca/config')}
                size="large"
                className="ninja-button"
              >
                🔄 重新配置策略
              </Button>
              
              <Button
                onClick={() => navigate('/')}
                size="large"
                className="ninja-button-secondary"
              >
                🏠 返回策略选择
              </Button>
            </div>

            <div className="mt-4 text-gray-500 text-sm">
              <div>🥷 忍者心得: {result.total_return >= 0 ? '定投策略显示正收益，保持投资纪律是关键' : '短期回撤是正常现象，长期定投见真章'}</div>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default DCAResult