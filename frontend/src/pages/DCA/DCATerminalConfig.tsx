import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { InputNumber, Select, message } from 'antd'
import dayjs from 'dayjs'
import { Typewriter } from 'react-simple-typewriter'
import TerminalShell from '@/components/TerminalShell'
import PixelButton from '@/components/PixelButton'
import StockSelectorASCII from '@/components/StockSelectorASCII'
import QuickDateSelectorASCII from '@/components/QuickDateSelectorASCII'
import FrequencySelector from '@/components/FrequencySelector'
import MatrixNinjaAnimation from '@/components/MatrixNinjaAnimation'
import { backtestService } from '@/services/backtest'

/** DCA任务配置数据接口 */
interface DCAConfig {
  symbol: string
  investmentAmount: number
  frequencyDays: number
  dateRange: [string, string]
  initialCash: number
  // 止盈策略配置
  exitStrategy: string
  profitTarget?: number
  timeLimitMonths?: number
  batchExitLevels?: number[]
  batchExitRatios?: number[]
}

/** 页面状态枚举 */
type PagePhase = 'intro' | 'config' | 'confirm' | 'execute' | 'result'

/**
 * DCA终端化配置页面
 * 单页面完成：任务简介 → 参数配置 → 确认 → 执行 → 结果
 */
const DCATerminalConfig: React.FC = () => {
  const navigate = useNavigate()

  /** 当前页面阶段 */
  const [phase, setPhase] = useState<PagePhase>('intro')
  
  /** DCA配置数据 - 都有默认值避免校验错误 */
  const [config, setConfig] = useState<DCAConfig>({
    symbol: '510300',
    investmentAmount: 1000,
    frequencyDays: 30,
    dateRange: ['2021-01-01', '2024-01-01'],
    initialCash: 100000,
    exitStrategy: 'hold',
    profitTarget: 30,
    timeLimitMonths: 36,
    batchExitLevels: [20, 40, 60],
    batchExitRatios: [0.3, 0.5, 1.0]
  })

  /** 执行结果数据 */
  const [executionResult, setExecutionResult] = useState<any>(null)
  /** 执行错误信息 */
  const [executionError, setExecutionError] = useState<string>('')
  /** 是否正在执行 */
  const [isExecuting, setIsExecuting] = useState(false)

  // 自动跳转到详情页
  useEffect(() => {
    if (executionResult) {
      // 立即跳转，不等待
      navigate('/dca/result', { 
        state: { 
          backtestResult: executionResult,
          timestamp: Date.now()
        }
      })
    }
  }, [executionResult, navigate])

  /** 进入配置阶段 */
  const handleStartConfig = () => {
    setPhase('config')
  }

  /** 直接开始执行任务 - 跳过确认步骤 */
  const handleConfirmConfig = async () => {
    await handleStartExecution()
  }

  /** 修改配置 */
  const handleModifyConfig = () => {
    setPhase('config')
  }

  /** 开始执行任务 */
  const handleStartExecution = async () => {
    setPhase('execute')
    setIsExecuting(true)
    setExecutionError('')

    try {
      const backtestParams = {
        symbol: config.symbol,
        investment_amount: config.investmentAmount,
        frequency_days: config.frequencyDays,
        start_date: config.dateRange[0],
        end_date: config.dateRange[1],
        initial_cash: config.initialCash,
        exit_strategy: config.exitStrategy,
        profit_target: config.profitTarget,
        time_limit_months: config.timeLimitMonths,
        batch_exit_levels: config.batchExitLevels,
        batch_exit_ratios: config.batchExitRatios
      }

      const result = await backtestService.runDCABacktest(backtestParams)
      setExecutionResult(result)
      setPhase('result')
      
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          '任务执行失败，请检查网络连接'
      setExecutionError(errorMessage)
    } finally {
      setIsExecuting(false)
    }
  }

  /** 查看结果详情 */
  const handleViewResult = () => {
    if (executionResult) {
      navigate('/dca/result', {
        state: {
          backtestResult: executionResult,
          timestamp: Date.now()
        }
      })
    }
  }

  /** 返回策略大厅 */
  const handleBackToHall = () => {
    navigate('/')
  }

  /** 重新配置任务 */
  const handleNewMission = () => {
    setPhase('intro')
    setExecutionResult(null)
    setExecutionError('')
  }

  // 渲染不同阶段的内容
  const renderPhaseContent = () => {
    switch (phase) {
      case 'intro':
        return (
          <div className="space-y-6">
            <div className="font-mono space-y-2">
              <div className="text-green-400">&gt; 🚀 init dca-mission</div>
              <div className="text-cyan-400 text-lg whitespace-pre-line">
                <Typewriter
                  words={[
                    `⚡ DCA定投渗透任务已载入
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📜 【DCA定投渗透任务】
🎯 难度: ★★☆☆☆ | 💰 预期收益: 8-12% | ⏰ 执行方式: 定期定额
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 策略简介: 通过固定时间间隔投资固定金额，利用时间复利效应和成本平均化降低投资风险，适合长期财富积累。`
                  ]}
                  loop={1}
                  cursor={false}
                  typeSpeed={30}
                  deleteSpeed={999999}
                  delaySpeed={999999}
                />
              </div>
            </div>
            
            <div className="flex justify-center gap-6 mt-8">
              <PixelButton
                variant="primary"
                size="large"
                onClick={handleStartConfig}
              >
                🚀 开始配置
              </PixelButton>
              <PixelButton
                variant="secondary"
                size="large"
                onClick={handleBackToHall}
              >
                🏠 返回大厅
              </PixelButton>
            </div>
          </div>
        )

      case 'config':
        return (
          <div className="space-y-6">
            <div className="text-green-400 font-mono text-lg mb-6">
              🚀 config --interactive
            </div>
            
            {/* ASCII艺术股票选择器 */}
            <StockSelectorASCII
              value={config.symbol}
              onChange={(symbol) => setConfig(prev => ({ ...prev, symbol }))}
              className="mb-6"
            />

            {/* ASCII艺术时间选择器 */}
            <QuickDateSelectorASCII
              value={config.dateRange}
              onChange={(range) => setConfig(prev => ({ ...prev, dateRange: range }))}
              className="mb-6"
            />

            {/* ASCII艺术频率选择器 */}
            <FrequencySelector
              value={config.frequencyDays}
              onChange={(days) => setConfig(prev => ({ ...prev, frequencyDays: days }))}
              className="mb-6"
            />

            {/* 其他参数配置 */}
            <div className="space-y-4">
              <div>
                <div className="text-green-400 font-mono font-bold mb-2">
                  &gt; 💰 投资金额 (INVESTMENT_AMOUNT):
                </div>
                <div className="ml-4 space-y-2">
                  <InputNumber
                    value={config.investmentAmount}
                    onChange={(value) => setConfig(prev => ({ ...prev, investmentAmount: value || 1000 }))}
                    className="ninja-input font-mono !w-full"
                    placeholder="每次投资金额 (元)"
                    min={100}
                    max={50000}
                    step={100}
                  />
                  {/* 快速金额选择 */}
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span className="text-gray-500 text-xs">快选:</span>
                    {[
                      { label: '500', value: 500 },
                      { label: '1000', value: 1000 },
                      { label: '2000', value: 2000 },
                      { label: '3000', value: 3000 },
                      { label: '5000', value: 5000 }
                    ].map((option) => (
                      <button
                        key={option.value}
                        onClick={() => setConfig(prev => ({ ...prev, investmentAmount: option.value }))}
                        className={`px-2 py-1 text-xs font-mono rounded border transition-colors ${
                          config.investmentAmount === option.value
                            ? 'bg-green-400 text-black border-green-400'
                            : 'bg-black text-green-400 border-green-400/50 hover:border-green-400'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <div className="text-green-400 font-mono font-bold mb-2">
                  &gt; 💳 初始资金 (INITIAL_CASH):
                </div>
                <div className="ml-4 space-y-2">
                  <InputNumber
                    value={config.initialCash}
                    onChange={(value) => setConfig(prev => ({ ...prev, initialCash: value || 100000 }))}
                    className="ninja-input font-mono !w-full"
                    placeholder="初始可用资金 (元)"
                    min={1000}
                    max={1000000}
                    step={1000}
                  />
                  {/* 快速资金选择 */}
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span className="text-gray-500 text-xs ">快选:</span>
                    {[
                      { label: '5万', value: 50000 },
                      { label: '10万', value: 100000 },
                      { label: '20万', value: 200000 },
                      { label: '50万', value: 500000 }
                    ].map((option) => (
                      <button
                        key={option.value}
                        onClick={() => setConfig(prev => ({ ...prev, initialCash: option.value }))}
                        className={`px-2 py-1 text-xs font-mono rounded border transition-colors ${
                          config.initialCash === option.value
                            ? 'bg-green-400 text-black border-green-400'
                            : 'bg-black text-green-400 border-green-400/50 hover:border-green-400'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* 止盈策略配置 */}
              <div>
                <div className="text-green-400 font-mono font-bold mb-2">
                  &gt; 🎯 止盈策略 (EXIT_STRATEGY):
                </div>
                <div className="ml-4 space-y-3">
                  <Select
                    value={config.exitStrategy}
                    onChange={(value) => setConfig(prev => ({ ...prev, exitStrategy: value }))}
                    className="ninja-input font-mono !w-full"
                    options={[
                      { value: 'hold', label: '🔒 纯持有 - 长期价值投资' },
                      { value: 'profit_target', label: '🎯 目标收益止盈 - 达到目标即卖出' },
                      { value: 'time_limit', label: '⏰ 时间止盈 - 定期到期卖出' },
                      { value: 'batch_exit', label: '📊 分批止盈 - 多层次逐步退出' }
                    ]}
                  />
                  
                  {/* 目标收益止盈参数 */}
                  {config.exitStrategy === 'profit_target' && (
                    <div>
                      <div className="text-cyan-400 text-sm mb-1">目标收益率 (%)</div>
                      <InputNumber
                        value={config.profitTarget}
                        onChange={(value) => setConfig(prev => ({ ...prev, profitTarget: value || 30 }))}
                        className="ninja-input font-mono !w-full"
                        placeholder="目标收益率"
                        min={5}
                        max={500}
                        step={5}
                      />
                    </div>
                  )}
                  
                  {/* 时间止盈参数 */}
                  {config.exitStrategy === 'time_limit' && (
                    <div>
                      <div className="text-cyan-400 text-sm mb-1">持有时长 (月)</div>
                      <InputNumber
                        value={config.timeLimitMonths}
                        onChange={(value) => setConfig(prev => ({ ...prev, timeLimitMonths: value || 36 }))}
                        className="ninja-input font-mono !w-full"
                        placeholder="持有月数"
                        min={6}
                        max={120}
                        step={6}
                      />
                    </div>
                  )}
                  
                  {/* 分批止盈参数 */}
                  {config.exitStrategy === 'batch_exit' && (
                    <div className="space-y-2">
                      <div className="text-cyan-400 text-sm">分批卖出配置</div>
                      <div className="text-xs text-gray-400">
                        收益率达到 20%/40%/60% 时分别卖出 30%/50%/100%
                      </div>
                      <div className="text-xs text-yellow-400">
                        💡 高级策略：逐步锁定收益，平衡风险与收益
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-center gap-6 mt-8">
              <PixelButton
                variant="primary"
                size="large"
                onClick={handleConfirmConfig}
              >
                🚀 开始执行
              </PixelButton>
              <PixelButton
                variant="secondary"
                size="large"
                onClick={() => setPhase('intro')}
              >
                ⬅️ 返回简介
              </PixelButton>
            </div>
          </div>
        )

      case 'confirm':
        return (
          <div className="space-y-6">
            <div className="font-mono space-y-2">
              <div className="text-green-400">&gt; 📋 cat dca_mission_config.json</div>
              <div className="text-cyan-400 whitespace-pre-line">
                <Typewriter
                  words={[
                    `✅ DCA_MISSION_CONFIG:
🎯 TARGET_SYMBOL=${config.symbol}
💰 INVESTMENT_AMOUNT=${config.investmentAmount}
⏰ FREQUENCY_DAYS=${config.frequencyDays}
📅 DATE_RANGE=${config.dateRange[0]}:${config.dateRange[1]}
💳 INITIAL_CASH=${config.initialCash}
🔢 EXPECTED_TRADES=${Math.ceil(dayjs(config.dateRange[1]).diff(dayjs(config.dateRange[0]), 'day') / config.frequencyDays)}
🎯 EXIT_STRATEGY=${config.exitStrategy}${config.exitStrategy === 'profit_target' ? `\n💹 PROFIT_TARGET=${config.profitTarget}%` : ''}${config.exitStrategy === 'time_limit' ? `\n⏱️ TIME_LIMIT=${config.timeLimitMonths}months` : ''}${config.exitStrategy === 'batch_exit' ? `\n📊 BATCH_LEVELS=[20%,40%,60%]` : ''}`
                  ]}
                  loop={1}
                  cursor={false}
                  typeSpeed={40}
                  deleteSpeed={999999}
                  delaySpeed={999999}
                />
              </div>
            </div>
            
            <div className="flex justify-center gap-6 mt-8">
              <PixelButton
                variant="success"
                size="large"
                onClick={handleStartExecution}
              >
                🚀 开始执行
              </PixelButton>
              <PixelButton
                variant="secondary"
                size="large"
                onClick={handleModifyConfig}
              >
                ✏️ 修改配置
              </PixelButton>
            </div>
          </div>
        )

      case 'execute':
        return (
          <div className="space-y-6">
            {/* 黑客帝国风格加载动画 */}
            <MatrixNinjaAnimation 
              isActive={isExecuting}
              onComplete={() => {}}
              duration={30000}
            />
            
            {executionError && (
              <>
                <div className="p-4 bg-red-400/10 border border-red-400/30 rounded">
                  <div className="text-red-400 font-mono text-center">
                    <div className="text-lg mb-2">💀 执行失败</div>
                    <div className="text-sm">✗ {executionError}</div>
                  </div>
                </div>
                
                <div className="flex justify-center gap-6">
                  <PixelButton
                    variant="warning"
                    size="large"
                    onClick={handleStartExecution}
                  >
                    🔄 重试
                  </PixelButton>
                  <PixelButton
                    variant="secondary"
                    size="large"
                    onClick={handleModifyConfig}
                  >
                    ✏️ 修改
                  </PixelButton>
                </div>
              </>
            )}
          </div>
        )

      case 'result':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="text-green-400 font-mono text-xl mb-4">
                ✅ 任务执行完成！
              </div>
            </div>

            {/* 直接跳转详情页，不显示结果摘要 */}
            {executionResult && (
              <div className="text-center">
                <div className="text-green-400 font-mono mb-4">
                  正在跳转到详细分析页面...
                </div>
              </div>
            )}

            <div className="flex justify-center gap-6">
              <PixelButton
                variant="primary"
                size="large"
                onClick={handleViewResult}
              >
                📋 查看详情
              </PixelButton>
              <PixelButton
                variant="secondary"
                size="large"
                onClick={handleNewMission}
              >
                🚀 新任务
              </PixelButton>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-black text-green-400 p-8">
      <div className="max-w-6xl mx-auto">
        <TerminalShell 
          title="DCA Mission Terminal"
          hostname="ninja"
          workingDir="~/dca-mission"
        >
          {renderPhaseContent()}
        </TerminalShell>
      </div>
    </div>
  )
}

export default DCATerminalConfig