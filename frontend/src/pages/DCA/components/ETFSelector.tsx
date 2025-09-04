import React from 'react'
import { Input, message } from 'antd'

interface ETFOption {
  code: string
  name: string
  desc: string
}

interface ETFSelectorProps {
  /** 当前选中的ETF代码 */
  value: string
  /** 选择变化时的回调函数 */
  onChange: (code: string) => void
  /** 热门ETF选项数据 */
  options?: ETFOption[]
}

const defaultETFs: ETFOption[] = [
  { code: '510300', name: '沪深300ETF', desc: '大盘蓝筹' },
  { code: '512100', name: '中证1000ETF', desc: '中小盘成长' },
  { code: '159915', name: '创业板ETF', desc: '创新成长' },
  { code: 'SPY', name: '标普500ETF', desc: '美股大盘' },
  { code: 'QQQ', name: '纳斯达克100ETF', desc: '美股科技' }
]

const ETFSelector: React.FC<ETFSelectorProps> = ({
  value,
  onChange,
  options = defaultETFs
}) => {
  /** 
   * 快速选择ETF标的
   * @param etfCode ETF代码
   */
  const handleQuickSelect = (etfCode: string) => {
    onChange(etfCode)
    const etf = options.find(e => e.code === etfCode)
    message.success(`已选择 ${etf?.name} (${etfCode})`)
  }

  return (
    <div>
      {/* 热门ETF快选 */}
      <div className="mb-4">
        <div className="text-gray-400 text-sm mb-2">快速选择热门ETF:</div>
        <div className="flex flex-wrap gap-2">
          {options.map(etf => (
            <button
              key={etf.code}
              onClick={() => handleQuickSelect(etf.code)}
              className={`px-3 py-1 border text-xs transition-colors ${
                value === etf.code 
                  ? 'border-green-400 bg-green-400/20 text-green-400' 
                  : 'border-green-400/50 hover:bg-green-400/10 text-gray-300'
              }`}
            >
              <div>{etf.code}</div>
              <div className="text-gray-500">{etf.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* 自定义标的输入 */}
      <div>
        <div className="text-gray-400 text-sm mb-2">投资标的代码:</div>
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value.toUpperCase())}
          placeholder="510300 / SPY"
          style={{
            backgroundColor: 'black',
            borderColor: '#4ade80',
            color: '#22c55e'
          }}
        />
        <div className="text-gray-500 text-xs mt-1">
          A股ETF: 510300, 512100 | 美股ETF: SPY, QQQ
        </div>
      </div>
    </div>
  )
}

export default ETFSelector