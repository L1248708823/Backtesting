import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Button } from 'antd'
import TerminalHeader from '@/components/TerminalHeader'

interface BacktestResult {
  strategy_id: string
  parameters: Record<string, any>
  start_date: string
  end_date: string
  initial_cash: number
  final_value: number
  total_return: number
  total_trades: number
  performance_metrics: Record<string, any>
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
  return (
    <div className="min-h-screen bg-black text-green-400 font-mono">
      {/* 页面容器 - 计算实际可用高度 */}
      <div className="h-screen  pb-8 px-8 overflow-y-auto">
      {/* 终端头部 - 使用通用组件 */}
      <TerminalHeader
        title="DCA回测结果分析终端"
        hostname="dca-result"
        taskDescription="任务完成 - 定投回测分析报告"
      />

      <div className="max-w-4xl mx-auto">
        
        {/* 回测结果概览 */}
        <div className="border border-green-400/30 p-6 mb-6">
          <div className="text-green-400 mb-4">[MISSION_REPORT] 任务执行报告 📊</div>
          
          {result ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-gray-400 text-sm">总收益率</div>
                <div className="text-2xl text-yellow-400">
                  {result.total_return?.toFixed(2) || '--'}%
                </div>
              </div>
              
              <div>
                <div className="text-gray-400 text-sm">最终资产</div>
                <div className="text-2xl text-green-400">
                  ¥{result.final_value?.toLocaleString() || '--'}
                </div>
              </div>
              
              <div>
                <div className="text-gray-400 text-sm">总交易次数</div>
                <div className="text-2xl text-cyan-400">
                  {result.total_trades || 0}
                </div>
              </div>
              
              <div>
                <div className="text-gray-400 text-sm">策略评级</div>
                <div className="text-2xl">
                  {result.total_return > 0 ? '🥷' : '💀'}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-4">⏳</div>
              <div>等待回测结果...</div>
            </div>
          )}
        </div>

        {/* 策略配置回顾 */}
        {result && (
          <div className="border border-green-400/30 p-6 mb-6">
            <div className="text-green-400 mb-4">[CONFIG] 策略配置回顾 ⚙️</div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="text-gray-400 mb-2">投资参数:</div>
                <div className="space-y-1 text-sm">
                  <div>• 投资标的: <span className="text-cyan-400">{result.parameters.symbol}</span></div>
                  <div>• 投资金额: <span className="text-yellow-400">¥{result.parameters.investment_amount?.toLocaleString()}</span></div>
                  <div>• 投资频率: <span className="text-green-400">每{result.parameters.frequency_days}天</span></div>
                </div>
              </div>
              
              <div>
                <div className="text-gray-400 mb-2">回测配置:</div>
                <div className="space-y-1 text-sm">
                  <div>• 时间范围: <span className="text-cyan-400">{result.start_date} ~ {result.end_date}</span></div>
                  <div>• 初始资金: <span className="text-yellow-400">¥{result.initial_cash?.toLocaleString()}</span></div>
                  <div>• 盈亏金额: <span className={result.total_return >= 0 ? 'text-green-400' : 'text-red-400'}>
                    {result.total_return >= 0 ? '+' : ''}¥{((result.final_value - result.initial_cash) || 0).toLocaleString()}
                  </span></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 详细分析 */}
        <div className="border border-green-400/30 p-6 mb-6">
          <div className="text-green-400 mb-4">[ANALYSIS] 深度分析 🔍</div>
          
          <div className="text-gray-400 text-center py-12">
            <div className="text-4xl mb-4">🚧</div>
            <div>详细分析功能开发中...</div>
            <div className="text-sm mt-2">包括收益曲线图、风险指标、交易记录等</div>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="border border-green-400/30 p-6 text-center">
          <div className="text-green-400 mb-4">[ACTIONS] 下一步操作 🎯</div>
          
          <div className="flex justify-center gap-4">
            <Button
              onClick={() => navigate('/dca/config')}
              className="ninja-button"
              style={{
                backgroundColor: 'transparent',
                borderColor: '#22c55e',
                color: '#22c55e',
                fontFamily: 'monospace'
              }}
            >
               重新配置策略
            </Button>
            
            <Button
              onClick={() => navigate('/')}
              className="ninja-button"
              style={{
                backgroundColor: 'transparent',
                borderColor: '#06b6d4',
                color: '#06b6d4',
                fontFamily: 'monospace'
              }}
            >
              返回策略选择
            </Button>
          </div>

          <div className="mt-4 text-gray-500 text-sm">
            <div>🥷 忍者心得: {result?.total_return >= 0 ? '定投有成效，保持纪律' : '市场有风险，长期持有'}</div>
          </div>
        </div>

      </div>
      </div>
    </div>
  )
}

export default DCAResult