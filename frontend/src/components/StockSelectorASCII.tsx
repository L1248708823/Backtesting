import React, { useState } from 'react'

interface StockOption {
  /** 股票代码 */
  code: string
  /** 股票名称 */
  name: string
  /** 分类：热门、常用等 */
  category: 'hot' | 'common' | 'custom'
}

interface StockSelectorASCIIProps {
  /** 当前选中的股票代码 */
  value: string
  /** 选择变化回调 */
  onChange: (code: string) => void
  /** 自定义样式类名 */
  className?: string
}

/** 预定义的热门股票选项 */
const HOT_STOCKS: StockOption[] = [
  { code: '510300', name: '沪深300ETF', category: 'hot' },
  { code: '510500', name: '中证500', category: 'hot' },
  { code: '512100', name: '中证1000', category: 'hot' },
  { code: 'QQQ', name: '纳斯达克', category: 'hot' },
  { code: 'SPY', name: '标普500', category: 'hot' },
  { code: 'VTI', name: '全市场', category: 'hot' }
]

/** 常用推荐股票 */
const COMMON_STOCKS: StockOption[] = [
  { code: '000300', name: '沪深300指数', category: 'common' },
  { code: '159919', name: '沪深300ETF', category: 'common' },
  { code: '513100', name: '纳指ETF', category: 'common' },
  { code: '518880', name: '黄金ETF', category: 'common' }
]

/**
 * ASCII艺术风格的股票选择器
 * 用ASCII字符画出卡片边框，实现终端风格的交互式选择
 */
const StockSelectorASCII: React.FC<StockSelectorASCIIProps> = ({
  value,
  onChange,
  className = ""
}) => {
  /** 自定义输入的股票代码 */
  const [customInput, setCustomInput] = useState('')
  
  /** 获取股票的显示信息 */
  const getStockInfo = (code: string) => {
    const allStocks = [...HOT_STOCKS, ...COMMON_STOCKS]
    const stock = allStocks.find(s => s.code === code)
    return stock ? `${stock.code} - ${stock.name}` : `${code} - 自定义股票`
  }

  /** 处理卡片点击 */
  const handleCardClick = (code: string) => {
    onChange(code)
  }

  /** 处理自定义输入 */
  const handleCustomInput = (inputValue: string) => {
    setCustomInput(inputValue)
    if (inputValue.trim()) {
      onChange(inputValue.trim().toUpperCase())
    }
  }

  /** 渲染ASCII卡片 */
  const renderASCIICard = (stock: StockOption, isSelected: boolean) => {
    const selectedClass = isSelected ? 'text-green-400 border-green-400' : 'text-gray-300 border-gray-600'
    const hoverClass = 'hover:text-green-300 hover:border-green-500 cursor-pointer transition-colors'
    
    return (
      <div
        key={stock.code}
        onClick={() => handleCardClick(stock.code)}
        className={`
          font-mono text-xs border rounded-sm p-2 min-w-[100px] text-center
          ${selectedClass} ${hoverClass}
        `}
      >
        <div className="font-bold">{stock.code}</div>
        <div className="text-xs mt-1">{stock.name}</div>
        <div className="mt-1">
          {isSelected ? '[●选中]' : '[○选择]'}
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-4 font-mono ${className}`}>
      {/* 目标锁定标题 */}
      <div className="text-green-400 font-bold">
        &gt; 🎯 目标锁定 (TARGET_SYMBOL):
      </div>

      {/* 热门推荐区域 */}
      <div className="ml-4">
        <div className="text-gray-400 mb-2">🔥 热门推荐:</div>
        
        {/* ASCII艺术卡片网格 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
          {HOT_STOCKS.map(stock => 
            renderASCIICard(stock, stock.code === value)
          )}
        </div>
      </div>

      {/* 常用推荐区域 */}
      <div className="ml-4">
        <div className="text-gray-400 mb-2">⭐ 常用推荐:</div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
          {COMMON_STOCKS.map(stock => 
            renderASCIICard(stock, stock.code === value)
          )}
        </div>
      </div>

      {/* 自选输入区域 */}
      <div className="ml-4">
        <div className="text-gray-400 mb-2">✏️ 自选输入:</div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={customInput}
            onChange={(e) => handleCustomInput(e.target.value)}
            placeholder="输入股票代码..."
            className="
              ninja-input font-mono 
              px-3 py-1 rounded-sm focus:outline-none
              placeholder-gray-500 min-w-[200px]
            "
          />
          <span className="text-gray-500">🔍搜索</span>
        </div>
      </div>

      {/* 当前选择显示 */}
      <div className="ml-4 p-3 border border-green-400/30 bg-green-400/5 rounded-sm">
        <span className="text-gray-400">🎯 当前选择: </span>
        <span className="text-green-400 font-bold">{getStockInfo(value)}</span>
      </div>
    </div>
  )
}

export default StockSelectorASCII