import React, { useState } from 'react'
import { InputNumber } from 'antd'

interface FrequencyOption {
  /** 选项标识 */
  key: string
  /** 显示标签 */
  label: string
  /** 天数值 */
  days: number
}

interface FrequencySelectorProps {
  /** 当前选中的天数 */
  value: number
  /** 选择变化回调 */
  onChange: (days: number) => void
  /** 自定义样式类名 */
  className?: string
}

/** 预定义的执行频率选项 */
const FREQUENCY_OPTIONS: FrequencyOption[] = [
  { key: 'weekly', label: '每周', days: 7 },
  { key: 'biweekly', label: '双周', days: 14 },
  { key: 'monthly', label: '每月', days: 30 },
  { key: 'quarterly', label: '每季', days: 90 }
]

/**
 * 执行频率快捷选择器
 * ASCII风格的频率选择组件，支持快捷选择和自定义输入
 */
const FrequencySelector: React.FC<FrequencySelectorProps> = ({
  value,
  onChange,
  className = ""
}) => {
  /** 当前选择模式：quick或custom */
  const [mode, setMode] = useState<'quick' | 'custom'>(() => {
    // 根据当前值判断初始模式
    const matchedOption = FREQUENCY_OPTIONS.find(opt => opt.days === value)
    return matchedOption ? 'quick' : 'custom'
  })

  /** 当前选中的快捷选项 */
  const [selectedOption, setSelectedOption] = useState<string>(() => {
    const matchedOption = FREQUENCY_OPTIONS.find(opt => opt.days === value)
    return matchedOption?.key || 'monthly'
  })

  /** 处理快捷选项点击 */
  const handleQuickSelect = (option: FrequencyOption) => {
    setSelectedOption(option.key)
    setMode('quick')
    onChange(option.days)
  }

  /** 处理自定义模式 */
  const handleCustomMode = () => {
    setMode('custom')
  }

  /** 处理自定义天数输入 */
  const handleCustomInput = (days: number | null) => {
    if (days && days > 0) {
      onChange(days)
    }
  }

  /** 渲染ASCII标签卡片 */
  const renderFrequencyTab = (option: FrequencyOption, isSelected: boolean) => {
    const selectedClass = isSelected && mode === 'quick'
      ? 'text-green-400 border-green-400 bg-green-400/10'
      : 'text-gray-300 border-gray-600'
    const hoverClass = 'hover:text-green-300 hover:border-green-500 cursor-pointer transition-colors'
    
    return (
      <div
        key={option.key}
        onClick={() => handleQuickSelect(option)}
        className={`
          font-mono text-xs border rounded-sm p-2 min-w-[60px] text-center
          ${selectedClass} ${hoverClass}
        `}
      >
        <div className="font-bold">{option.label}</div>
        <div className="text-[10px] text-gray-500">{option.days}天</div>
        <div className="mt-1 text-[10px]">
          {isSelected && mode === 'quick' ? '●' : '○'}
        </div>
      </div>
    )
  }

  /** 渲染自定义标签 */
  const renderCustomTab = () => {
    const selectedClass = mode === 'custom'
      ? 'text-green-400 border-green-400 bg-green-400/10'
      : 'text-gray-300 border-gray-600'
    const hoverClass = 'hover:text-green-300 hover:border-green-500 cursor-pointer transition-colors'
    
    return (
      <div
        onClick={handleCustomMode}
        className={`
          font-mono text-xs border rounded-sm p-2 min-w-[60px] text-center
          ${selectedClass} ${hoverClass}
        `}
      >
        <div className="font-bold">自定义</div>
        <div className="text-[10px] text-gray-500">天数</div>
        <div className="mt-1 text-[10px]">
          {mode === 'custom' ? '●' : '○'}
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-4 font-mono ${className}`}>
      {/* 执行频率标题 */}
      <div className="text-green-400 font-bold">
        &gt; ⏰ 执行频率 (FREQUENCY_DAYS):
      </div>

      {/* ASCII标签选择器 */}
      <div className="ml-4">
        <div className="grid grid-cols-3 md:grid-cols-5 gap-2 mb-4">
          {FREQUENCY_OPTIONS.map(option => 
            renderFrequencyTab(option, option.key === selectedOption)
          )}
          {renderCustomTab()}
        </div>

        {/* 自定义输入框 */}
        {mode === 'custom' && (
          <div className="mb-4">
            <div className="text-gray-400 text-sm mb-2">自定义间隔天数:</div>
            <InputNumber
              value={value}
              onChange={handleCustomInput}
              className="ninja-input font-mono"
              placeholder="输入天数"
              min={1}
              max={365}
              step={1}
              addonAfter="天"
            />
          </div>
        )}

        {/* 当前选择显示 */}
        <div className="p-3 border border-green-400/30 bg-green-400/5 rounded-sm">
          <span className="text-gray-400">⏰ 当前频率: </span>
          <span className="text-green-400 font-bold">
            每{value}天投资一次
          </span>
          <span className="text-gray-500 ml-2 text-sm">
            (约每{Math.round(value/30 * 10) / 10}个月)
          </span>
        </div>
      </div>
    </div>
  )
}

export default FrequencySelector