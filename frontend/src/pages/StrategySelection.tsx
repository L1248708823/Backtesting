import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Typography, Tag, Button, Spin, message, Alert, Space } from 'antd'
import { useNavigate } from 'react-router-dom'
import { RocketOutlined, StarOutlined } from '@ant-design/icons'
import { strategyService, Strategy } from '@/services/backtest'
import { RISK_LEVELS, MARKETS } from '@/utils/constants'

const { Title, Paragraph } = Typography

const StrategySelection: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadStrategies()
  }, [])

  const loadStrategies = async () => {
    try {
      setLoading(true)
      const data = await strategyService.getStrategies()
      setStrategies(data)
    } catch (error) {
      message.error('加载策略列表失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectStrategy = (strategyId: string) => {
    navigate(`/config/${strategyId}`)
  }

  const handleDCAStrategy = () => {
    navigate('/dca/config')
  }

  const getRiskColor = (level: string) => {
    return RISK_LEVELS[level as keyof typeof RISK_LEVELS]?.color || '#666'
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <Spin size="large" />
        <div className="mt-4 text-gray-600">加载策略中...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Hero区域 - 现代简约风格 */}
      <div className="relative overflow-hidden">
        {/* 背景装饰 */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-950/20 via-gray-950 to-purple-950/20"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMxZTQwYWYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMTAiIGN5PSIxMCIgcj0iMiI+PC9jaXJjbGU+PC9nPjwvZz48L3N2Zz4=')] opacity-40"></div>
        
        <div className="relative container mx-auto px-6 py-24">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 bg-blue-950/30 border border-blue-500/20 rounded-full px-4 py-2 mb-8">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-blue-200 text-sm font-medium">量化回测系统 v2.0</span>
            </div>
            
            <h1 className="text-6xl md:text-7xl font-bold text-white mb-6">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
                量化回测
              </span>
              <br />
              <span className="text-gray-300">实验室</span>
            </h1>
            
            <p className="text-xl text-gray-400 mb-12 leading-relaxed">
              用数据驱动投资决策，用代码创造财富。<br />
              专业的策略回测平台，为量化交易者而生。
            </p>
            
            <div className="flex flex-wrap justify-center gap-4">
              <button 
                onClick={handleDCAStrategy}
                className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-8 py-4 rounded-xl font-semibold transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-blue-500/25"
              >
                <span className="flex items-center gap-2">
                  <RocketOutlined />
                  开始回测
                </span>
              </button>
              
              <button className="group bg-gray-800/50 hover:bg-gray-700/50 text-gray-300 hover:text-white border border-gray-700/50 hover:border-gray-600 px-8 py-4 rounded-xl font-semibold transition-all duration-300">
                <span className="flex items-center gap-2">
                  📊 查看策略
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 策略选择区域 */}
      <div className="container mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">选择投资策略</h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            每个策略都经过严格回测验证，支持灵活的参数配置和风险控制
          </p>
        </div>

        {/* 推荐策略卡片 */}
        <div className="bg-gradient-to-r from-green-900/20 to-emerald-900/20 border border-green-500/20 rounded-2xl p-8 mb-12 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-green-500/10 to-transparent rounded-full -translate-y-16 translate-x-16"></div>
          
          <div className="relative flex items-center justify-between flex-wrap gap-6">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-500 rounded-2xl flex items-center justify-center text-2xl">
                ⭐
              </div>
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-2xl font-bold text-white">定投策略 (DCA)</h3>
                  <span className="bg-green-500/20 text-green-400 text-xs font-medium px-3 py-1 rounded-full">推荐</span>
                </div>
                <p className="text-gray-300 text-lg">
                  最适合新手的长期投资策略，通过定期定额投资平滑市场波动
                </p>
              </div>
            </div>
            <button 
              onClick={handleDCAStrategy}
              className="bg-green-500 hover:bg-green-400 text-white px-8 py-3 rounded-xl font-semibold transition-all duration-300 hover:scale-105 shadow-lg shadow-green-500/25"
            >
              立即体验
            </button>
          </div>
        </div>

        {/* 策略网格 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {strategies.map((strategy) => (
            <div key={strategy.metadata.id} className="group bg-gray-900/50 hover:bg-gray-800/50 border border-gray-800 hover:border-gray-700 rounded-2xl p-6 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-xl font-semibold text-white group-hover:text-blue-400 transition-colors">
                  {strategy.metadata.name}
                </h3>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  strategy.metadata.risk_level === '低' 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                    : strategy.metadata.risk_level === '中'
                    ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}>
                  {strategy.metadata.risk_level}风险
                </span>
              </div>
              
              <p className="text-gray-400 text-sm mb-6 leading-relaxed">
                {strategy.metadata.description}
              </p>
              
              <div className="mb-6">
                <p className="text-gray-300 text-sm font-medium mb-3">支持市场</p>
                <div className="flex flex-wrap gap-2">
                  {strategy.metadata.supported_markets.map(market => (
                    <span key={market} className="bg-gray-800 text-gray-300 px-3 py-1 rounded-lg text-xs">
                      {MARKETS[market as keyof typeof MARKETS]?.icon} {market}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="mb-6">
                <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-lg text-xs font-medium">
                  {strategy.metadata.category}
                </span>
              </div>
              
              <button 
                onClick={() => handleSelectStrategy(strategy.metadata.id)}
                className="w-full bg-gray-800 hover:bg-blue-600 text-gray-300 hover:text-white py-3 rounded-xl font-medium transition-all duration-300 border border-gray-700 hover:border-blue-500"
              >
                选择策略
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default StrategySelection