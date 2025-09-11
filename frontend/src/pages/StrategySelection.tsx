import React, { useState, useEffect } from 'react'
import { Typewriter } from 'react-simple-typewriter'
import { useNavigate } from 'react-router-dom'
import { strategyService, Strategy, marketService, MarketDashboardData } from '@/services/backtest'
import TerminalHeader from '@/components/TerminalHeader'

const StrategySelection: React.FC = () => {
  /** 策略列表数据 - 从后端API获取的可用策略数组 */
  const [strategies, setStrategies] = useState<Strategy[]>([])
  /** 加载状态 - 控制策略列表的加载显示 */
  const [loading, setLoading] = useState(true)
  /** 市场数据 - 从后端API获取的实时市场指数和恐慌指数数据 */
  const [marketData, setMarketData] = useState<MarketDashboardData | null>(null)
  /** 市场数据加载状态 */
  const [marketLoading, setMarketLoading] = useState(true)
  const navigate = useNavigate()


  // 加载策略
  useEffect(() => {
    loadStrategies()
  }, [])

  // 加载市场数据
  useEffect(() => {
    loadMarketData()
    
    // 每30秒更新一次市场数据
    const timer = setInterval(() => {
      loadMarketData()
    }, 30000)
    
    return () => clearInterval(timer)
  }, [])

  /** 
   * 加载策略列表数据
   * 从后端API获取可用策略并更新state
   */
  const loadStrategies = async () => {
    try {
      setLoading(true)
      const data = await strategyService.getStrategies()
      setStrategies(data)
    } catch (error) {
      console.error('加载策略失败:', error)
    } finally {
      setLoading(false)
    }
  }

  /** 
   * 加载市场仪表盘数据
   * 从后端API获取实时指数、VIX、热门ETF数据
   */
  const loadMarketData = async () => {
    try {
      if (marketLoading) {
        setMarketLoading(true)
      }
      const data = await marketService.getDashboard()
      setMarketData(data)
    } catch (error) {
      console.error('加载市场数据失败:', error)
    } finally {
      if (marketLoading) {
        setMarketLoading(false)
      }
    }
  }

  /** 
   * 跳转到DCA定投策略配置页面 (增强版，支持止盈配置)
   */
  const handleDCAStrategy = () => {
    navigate('/dca/config')
  }

  /** 
   * 处理策略选择 - 跳转到对应策略的参数配置页
   * @param strategyId 策略ID
   */
  const handleSelectStrategy = (strategyId: string) => {
    navigate(`/config/${strategyId}`)
  }

  /** 
   * 根据涨跌幅生成情感化文案
   * @param changePct 涨跌幅
   * @param isUSStock 是否美股
   */
  const getEmotionText = (changePct: number | null, isUSStock: boolean = false) => {
    if (changePct === null) return "数据获取中..."
    
    if (changePct > 0) {
      return isUSStock 
        ? `📈马踏旧金山 +${changePct.toFixed(1)}%`
        : `📈奇袭得手 +${changePct.toFixed(1)}%`
    } else if (changePct < 0) {
      return isUSStock
        ? `📉败走华尔街 ${changePct.toFixed(1)}%`
        : `📉中了埋伏 ${changePct.toFixed(1)}%`
    } else {
      return isUSStock
        ? `➖蛰伏大洋彼岸 ${changePct.toFixed(1)}%`
        : `➖按兵不动 ${changePct.toFixed(1)}%`
    }
  }

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono overflow-hidden">
      {/* 页面容器 - 计算实际可用高度 */}
      <div className="h-screen relative z-10  pb-8 px-8 overflow-y-auto">
        {/* 终端头部 - 自定义版本包含Typewriter效果 */}
        <div className="mb-12">
          {/* 终端窗口头部 - 复用样式 */}
          <div className="flex items-center gap-4 mb-4">
            {/* macOS风格窗口控制按钮 */}
            <div className="flex gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full" title="关闭"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full" title="最小化"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full" title="全屏"></div>
            </div>
            
            {/* 终端标题和版本 */}
            <span className="text-gray-500 font-mono">
              量化回测终端 v2.0.0
            </span>
          </div>
          
          {/* 命令行提示符区域 - 带Typewriter效果 */}
          <div className="border-l-4 border-green-400 pl-4 py-2 bg-green-400/5 mb-6">
            {/* 命令行提示符 */}
            <div className="text-gray-400 text-sm mb-1 font-mono">
              ninja@quant-terminal:~$
            </div>
            
            {/* Typewriter效果任务描述 */}
            <div className="text-xl font-mono text-green-400">
              <Typewriter
                words={['别人恐惧我贪婪，别人小亏我破产~']}
                loop={0}
                cursor
                cursorStyle='|'
                typeSpeed={150}
                deleteSpeed={80}
                delaySpeed={3000}
                deleteDelay={2000}
              />
            </div>
          </div>
        </div>

        {/* 主要内容区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* 左侧 - 系统信息 */}
          <div className="lg:col-span-1 space-y-6">
            <div className="border border-green-400/30 p-4">
              <div className="text-green-400 mb-3">[NINJA_INTEL] 忍者情报网 🕵️</div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">⚡ 执行状态:</span>
                  <span className="text-green-400 animate-pulse">STRATEGY_STANDBY</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">
                    <span className="animate-pulse">🗡️</span> 大A情报:
                  </span>
                  <span className={`font-mono text-xs ${
                    marketData?.shanghai_index.change_pct && marketData.shanghai_index.change_pct > 0 
                      ? 'text-green-400' 
                      : marketData?.shanghai_index.change_pct && marketData.shanghai_index.change_pct < 0 
                      ? 'text-red-400' 
                      : 'text-yellow-400'
                  }`}>
                    上证 {marketData?.shanghai_index.value ? Math.round(marketData.shanghai_index.value) : "---"} {getEmotionText(marketData?.shanghai_index.change_pct || null)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">
                    <span className="animate-bounce">💨</span> 美股动向:
                  </span>
                  <span className={`font-mono text-xs ${
                    marketData?.nasdaq_index.change_pct && marketData.nasdaq_index.change_pct > 0 
                      ? 'text-green-400' 
                      : marketData?.nasdaq_index.change_pct && marketData.nasdaq_index.change_pct < 0 
                      ? 'text-red-400' 
                      : 'text-cyan-400'
                  }`}>
                    纳指 {marketData?.nasdaq_index.value ? Math.round(marketData.nasdaq_index.value) : "---"} {getEmotionText(marketData?.nasdaq_index.change_pct || null, true)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">
                    <span className="animate-pulse" style={{animationDelay: '0.5s'}}>🔥</span> 热门目标:
                  </span>
                  <span className="text-white text-xs">
                    {marketData?.hot_etfs?.slice(0, 2).join(' | ') || "数据获取中..."}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">
                    <span className="animate-bounce" style={{animationDelay: '1s'}}>💀</span> 危险指数:
                  </span>
                  <span className={`animate-pulse ${
                    marketData?.vix_level.color === 'red' ? 'text-red-400' :
                    marketData?.vix_level.color === 'yellow' ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {marketData?.vix_level.level || "数据获取中..."}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">
                    <span className="animate-pulse" style={{animationDelay: '1.5s'}}>📊</span> 市场节奏:
                  </span>
                  <span className="text-yellow-400 text-xs">
                    {marketLoading ? "数据获取中..." : "震荡横盘中"}
                  </span>
                </div>
              </div>
            </div>

            <div className="border border-green-400/30 p-4">
              <div className="text-green-400 mb-3">[TRAINING_LOG] 修行记录 📜</div>
              <div className="space-y-3 text-sm">
                <div className="p-2 bg-gray-900/50 border-l-2 border-red-400">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-white text-xs">💀 上次任务: DCA策略潜行</span>
                    <span className="text-red-400 text-xs">失败 -23.5%</span>
                  </div>
                  <div className="text-gray-500 text-xs">2024-03-01 • 修行1年</div>
                </div>
                
                <div className="p-2 bg-gray-900/50 border-l-2 border-green-400">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-white text-xs">⚡ 小试牛刀: 轮动策略</span>
                    <span className="text-green-400 text-xs">小胜 +12.3%</span>
                  </div>
                  <div className="text-gray-500 text-xs">2024-02-15 • 6月试炼</div>
                </div>

                <div className="pt-2 border-t border-gray-700 space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">🥷 当前等级:</span>
                    <span className="text-yellow-400">下忍 (菜鸟)</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">📈 修行进度:</span>
                    <span className="text-red-400">还在割肉中...</span>
                  </div>
                </div>

                {/* 快速操作按钮 */}
                <div className="pt-3 space-y-2">
                  <button
                    onClick={handleDCAStrategy}
                    className="w-full text-left p-2 border border-green-400/50 hover:bg-green-400/10 transition-colors group cursor-pointer"
                  >
                    <div className="text-green-400 group-hover:text-green-300 text-xs">
                      &gt; 🥷 执行任务 (DCA)
                    </div>
                  </button>
                  
                  <button className="w-full text-left p-2 border border-yellow-400/50 hover:bg-yellow-400/10 transition-colors group">
                    <div className="text-yellow-400 group-hover:text-yellow-300 text-xs">
                      &gt; 📜 查看修行历史
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 中间和右侧 - 策略列表 */}
          <div className="lg:col-span-2">
            <div className="border border-green-400/30 p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="text-green-400">[可用策略]</div>
                <div className="text-gray-500 text-sm">
                  {loading ? '加载中...' : `${strategies.length} 个策略`}
                </div>
              </div>

              {/* 推荐策略 */}
              <div className="mb-6 p-4 border border-yellow-400/50 bg-yellow-400/5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-yellow-400 font-bold mb-1">
                      [推荐] DCA 定投策略
                    </div>
                    <div className="text-gray-400 text-sm mb-2">
                      傻瓜式操作，适合懒人和新韭菜
                    </div>
                    <div className="text-xs text-gray-500">
                      风险等级: 低 | 预期收益: 跑赢通胀 | 破产概率: 5%
                    </div>
                  </div>
                  <button
                    onClick={handleDCAStrategy}
                    className="px-6 py-2 border border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black transition-colors cursor-pointer"
                  >
                    执行
                  </button>
                </div>
              </div>

              {/* 策略列表 */}
              <div className="space-y-3">
                {loading ? (
                  <div className="text-center py-8 text-gray-500">
                    正在扫描策略库...
                  </div>
                ) : (
                  strategies.map((strategy, index) => (
                    <div
                      key={strategy.metadata.id}
                      className="p-3 border border-green-400/30 hover:border-green-400/60 hover:bg-green-400/5 transition-colors cursor-pointer group"
                      onClick={() => handleSelectStrategy(strategy.metadata.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <span className="text-green-400">
                              [{String(index + 1).padStart(2, '0')}]
                            </span>
                            <span className="text-white group-hover:text-green-300">
                              {strategy.metadata.name}
                            </span>
                            <span className={`text-xs px-2 py-1 border ${
                              strategy.metadata.risk_level === '低' 
                                ? 'border-green-400/50 text-green-400'
                                : strategy.metadata.risk_level === '中'
                                ? 'border-yellow-400/50 text-yellow-400'
                                : 'border-red-400/50 text-red-400'
                            }`}>
                              {strategy.metadata.risk_level}风险
                            </span>
                          </div>
                          <div className="text-gray-400 text-sm">
                            {strategy.metadata.description}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            支持市场: {strategy.metadata.supported_markets.join(', ')}
                          </div>
                        </div>
                        <div className="text-green-400 opacity-0 group-hover:opacity-100 transition-opacity">
                          &gt;
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 底部终端提示 */}
        <div className="mt-12 text-center text-gray-600 text-sm">
          <div>提示: 投资有风险，入市需谨慎。本系统仅供娱乐，不构成投资建议。</div>
          <div className="mt-2">
            按 <kbd className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-xs">Ctrl+C</kbd> 退出系统
          </div>
        </div>
      </div>
    </div>
  )
}

export default StrategySelection