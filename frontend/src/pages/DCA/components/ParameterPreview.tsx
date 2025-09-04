import React from 'react'
import dayjs from 'dayjs'

interface DCAParameters {
  /** 投资标的代码 */
  symbol: string
  /** 投资金额 */
  investmentAmount: number
  /** 频率天数 */
  frequencyDays: number
  /** 日期范围 */
  dateRange: [dayjs.Dayjs, dayjs.Dayjs] | null
  /** 初始资金 */
  initialCash: number
}

interface ParameterPreviewProps {
  /** DCA参数配置 */
  parameters: DCAParameters
}

const ParameterPreview: React.FC<ParameterPreviewProps> = ({ parameters }) => {
  const { symbol, investmentAmount, frequencyDays, dateRange, initialCash } = parameters

  // 计算预期投资次数
  const calculateInvestmentCount = () => {
    if (!dateRange) return 0
    const days = dateRange[1].diff(dateRange[0], 'day')
    return Math.floor(days / frequencyDays)
  }

  // 获取频率描述
  const getFrequencyLabel = () => {
    switch (frequencyDays) {
      case 7: return '每周'
      case 30: return '每月' 
      case 90: return '每季'
      default: return `每${frequencyDays}天`
    }
  }

  const investmentCount = calculateInvestmentCount()
  const totalInvestment = investmentCount * investmentAmount

  return (
    <div className="border border-green-400/30 p-4">
      <div className="text-green-400 mb-3">[PREVIEW] 配置预览 👁️</div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-gray-400 mb-2">基础配置:</div>
          <div className="space-y-1 text-gray-300">
            <div>• 投资标的: <span className="text-green-400">{symbol || '--'}</span></div>
            <div>• 投资金额: <span className="text-yellow-400">¥{investmentAmount.toLocaleString()}</span></div>
            <div>• 投资频率: <span className="text-cyan-400">{getFrequencyLabel()}</span></div>
          </div>
        </div>

        <div>
          <div className="text-gray-400 mb-2">回测配置:</div>
          <div className="space-y-1 text-gray-300">
            <div>• 时间范围: <span className="text-green-400">
              {dateRange 
                ? `${dateRange[0].format('YYYY-MM-DD')} ~ ${dateRange[1].format('YYYY-MM-DD')}`
                : '--'
              }
            </span></div>
            <div>• 初始资金: <span className="text-yellow-400">¥{initialCash.toLocaleString()}</span></div>
            <div>• 回测天数: <span className="text-cyan-400">
              {dateRange ? dateRange[1].diff(dateRange[0], 'day') : 0}天
            </span></div>
          </div>
        </div>
      </div>

      {dateRange && (
        <div className="mt-4 pt-3 border-t border-green-400/20">
          <div className="text-gray-400 mb-2">预期结果:</div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-gray-500">预计投资次数</div>
              <div className="text-lg text-green-400">{investmentCount} 次</div>
            </div>
            <div>
              <div className="text-gray-500">预计总投入</div>
              <div className="text-lg text-yellow-400">¥{totalInvestment.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-gray-500">资金利用率</div>
              <div className="text-lg text-cyan-400">
                {initialCash > 0 ? ((totalInvestment / initialCash) * 100).toFixed(1) : 0}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 风险提示 */}
      <div className="mt-4 pt-3 border-t border-red-400/20 text-xs text-gray-500">
        ⚠️ 忍者提醒: 以上为预期计算，实际结果受市场波动、节假日等因素影响
      </div>
    </div>
  )
}

export default ParameterPreview