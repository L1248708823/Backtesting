import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { InputNumber, message } from 'antd'
import dayjs from 'dayjs'
import { Typewriter } from 'react-simple-typewriter'
import TerminalShell from '@/components/TerminalShell'
import PixelButton from '@/components/PixelButton'
import StockSelectorASCII from '@/components/StockSelectorASCII'
import QuickDateSelectorASCII from '@/components/QuickDateSelectorASCII'
import FrequencySelector from '@/components/FrequencySelector'
import { backtestService } from '@/services/backtest'

/** DCA任务配置数据接口 */
interface DCAConfig {
  symbol: string
  investmentAmount: number
  frequencyDays: number
  dateRange: [string, string]
  initialCash: number
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
    initialCash: 10000
  })

  /** 执行结果数据 */
  const [executionResult, setExecutionResult] = useState<any>(null)
  /** 执行错误信息 */
  const [executionError, setExecutionError] = useState<string>('')
  /** 是否正在执行 */
  const [isExecuting, setIsExecuting] = useState(false)


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
        initial_cash: config.initialCash
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
                <div className="ml-4">
                  <InputNumber
                    value={config.investmentAmount}
                    onChange={(value) => setConfig(prev => ({ ...prev, investmentAmount: value || 1000 }))}
                    className="ninja-input font-mono !w-full"
                    placeholder="每次投资金额 (元)"
                    min={100}
                    max={50000}
                    step={100}
                  />
                </div>
              </div>

              <div>
                <div className="text-green-400 font-mono font-bold mb-2">
                  &gt; 💳 初始资金 (INITIAL_CASH):
                </div>
                <div className="ml-4">
                  <InputNumber
                    value={config.initialCash}
                    onChange={(value) => setConfig(prev => ({ ...prev, initialCash: value || 10000 }))}
                    className="ninja-input font-mono !w-full"
                    placeholder="初始可用资金 (元)"
                    min={1000}
                    max={1000000}
                    step={1000}
                  />
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
🔢 EXPECTED_TRADES=${Math.ceil(dayjs(config.dateRange[1]).diff(dayjs(config.dateRange[0]), 'day') / config.frequencyDays)}`
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
            <div className="text-center">
              <div className="text-yellow-400 font-mono text-lg mb-4">
                🚀 execute dca-mission
              </div>
              <div className="text-green-400 font-mono animate-pulse">
                ⚡ 正在执行DCA渗透任务...
              </div>
            </div>

            {/* 执行进度显示 */}
            <div className="bg-gray-900/30 p-6 rounded border border-yellow-400/20">
              <div className="space-y-2 font-mono text-sm">
                <div className="text-gray-300">&gt; 🎯 目标锁定: {config.symbol}</div>
                <div className="text-gray-300">&gt; 📊 数据获取中...</div>
                <div className="text-gray-300">&gt; ⚡ 策略执行中...</div>
                <div className="text-gray-300">&gt; 💰 收益分析中...</div>
              </div>
              
              {isExecuting && (
                <div className="mt-4 text-center text-yellow-400 animate-pulse">
                  请稍候，任务执行中...
                </div>
              )}
              
              {executionError && (
                <div className="mt-4 p-3 bg-red-400/10 border border-red-400/30 rounded">
                  <div className="text-red-400 font-mono text-sm">
                    ✗ 执行失败: {executionError}
                  </div>
                </div>
              )}
            </div>

            {executionError && (
              <div className="flex justify-center gap-6">
                <PixelButton
                  variant="warning"
                  size="large"
                  onClick={handleStartExecution}
                >
                  🔄 重试执行
                </PixelButton>
                <PixelButton
                  variant="secondary"
                  size="large"
                  onClick={handleModifyConfig}
                >
                  ✏️ 修改配置
                </PixelButton>
              </div>
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

            {executionResult && (
              <div className="bg-green-400/10 p-6 rounded border border-green-400/30">
                <div className="text-green-400 font-mono font-bold mb-4">任务执行结果:</div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center font-mono">
                  <div>
                    <div className="text-gray-400 text-sm">执行次数</div>
                    <div className="text-cyan-400 font-bold text-lg">
                      {executionResult.total_trades || 0} 次
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">总收益率</div>
                    <div className={`font-bold text-lg ${
                      (executionResult.total_return || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {(executionResult.total_return || 0).toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">最终资产</div>
                    <div className="text-yellow-400 font-bold text-lg">
                      ¥{(executionResult.final_value || 0).toLocaleString()}
                    </div>
                  </div>
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