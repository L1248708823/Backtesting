import React, { useState } from 'react'
import { DatePicker } from 'antd'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker

interface QuickDateOption {
  /** 选项标识 */
  key: string
  /** 显示标签 */
  label: string
  /** 日期范围生成函数 */
  getRange: () => [string, string]
}

interface QuickDateSelectorASCIIProps {
  /** 当前选中的日期范围 */
  value: [string, string]
  /** 选择变化回调 */
  onChange: (range: [string, string]) => void
  /** 自定义样式类名 */
  className?: string
}

/** 预定义的快捷时间选项 */
const QUICK_OPTIONS: QuickDateOption[] = [
  {
    key: '3months',
    label: '近3个月',
    getRange: () => {
      const end = dayjs()
      const start = end.subtract(3, 'month')
      return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
    }
  },
  {
    key: '1year',
    label: '近1年',
    getRange: () => {
      const end = dayjs()
      const start = end.subtract(1, 'year')
      return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
    }
  },
  {
    key: '3years',
    label: '近3年',
    getRange: () => {
      const end = dayjs()
      const start = end.subtract(3, 'year')
      return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
    }
  },
  {
    key: 'random',
    label: '🎲随机',
    getRange: () => {
      const end = dayjs()
      const randomMonths = Math.floor(Math.random() * 36) + 6 // 6-42个月
      const start = end.subtract(randomMonths, 'month')
      return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
    }
  }
]

/**
 * ASCII艺术风格的日期范围快速选择器
 * 用ASCII字符实现标签页样式的日期选择
 */
const QuickDateSelectorASCII: React.FC<QuickDateSelectorASCIIProps> = ({
  value,
  onChange,
  className = ""
}) => {
  /** 当前选择的模式：quick或manual */
  const [mode, setMode] = useState<'quick' | 'manual'>('quick')
  /** 当前选中的快捷选项 */
  const [selectedOption, setSelectedOption] = useState<string>('3years')

  /** 处理快捷选项点击 */
  const handleQuickSelect = (option: QuickDateOption) => {
    setSelectedOption(option.key)
    setMode('quick')
    const range = option.getRange()
    onChange(range)
  }

  /** 处理手动模式切换 */
  const handleManualMode = () => {
    setMode('manual')
  }

  /** 处理手动日期选择 */
  const handleManualDateChange = (dates: any) => {
    if (dates && dates[0] && dates[1]) {
      const range: [string, string] = [
        dates[0].format('YYYY-MM-DD'),
        dates[1].format('YYYY-MM-DD')
      ]
      onChange(range)
    }
  }

  /** 渲染ASCII标签卡片 */
  const renderASCIITab = (option: QuickDateOption, isSelected: boolean) => {
    const selectedClass = isSelected && mode === 'quick' 
      ? 'text-green-400 border-green-400 bg-green-400/10' 
      : 'text-gray-300 border-gray-600'
    const hoverClass = 'hover:text-green-300 hover:border-green-500 cursor-pointer transition-colors'
    
    return (
      <div
        key={option.key}
        onClick={() => handleQuickSelect(option)}
        className={`
          font-mono text-xs border rounded-sm p-2 min-w-[80px] text-center
          ${selectedClass} ${hoverClass}
        `}
      >
        <div className="font-bold">{option.label}</div>
        <div className="mt-1 text-[10px]">
          {isSelected && mode === 'quick' ? '●' : '○'}
        </div>
      </div>
    )
  }

  /** 渲染手动选择标签 */
  const renderManualTab = () => {
    const selectedClass = mode === 'manual' 
      ? 'text-green-400 border-green-400 bg-green-400/10' 
      : 'text-gray-300 border-gray-600'
    const hoverClass = 'hover:text-green-300 hover:border-green-500 cursor-pointer transition-colors'
    
    return (
      <div
        onClick={handleManualMode}
        className={`
          font-mono text-xs border rounded-sm p-2 min-w-[80px] text-center
          ${selectedClass} ${hoverClass}
        `}
      >
        <div className="font-bold">📅手动</div>
        <div className="mt-1 text-[10px]">
          {mode === 'manual' ? '●' : '○'}
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-4 font-mono ${className}`}>
      {/* 时间范围标题 */}
      <div className="text-green-400 font-bold">
        &gt; 📅 时间范围 (DATE_RANGE):
      </div>

      {/* ASCII标签选择器 */}
      <div className="ml-4">
        <div className="grid grid-cols-3 md:grid-cols-5 gap-2 mb-4">
          {QUICK_OPTIONS.map(option => 
            renderASCIITab(option, option.key === selectedOption)
          )}
          {renderManualTab()}
        </div>

        {/* 手动日期选择器 */}
        {mode === 'manual' && (
          <div className="mb-4">
            <div className="text-gray-400 text-sm mb-2">选择日期范围:</div>
            <RangePicker
              value={[dayjs(value[0]), dayjs(value[1])]}
              onChange={handleManualDateChange}
              format="YYYY-MM-DD"
              className="ninja-input font-mono"
              placeholder={['开始日期', '结束日期']}
            />
          </div>
        )}

        {/* 当前选择显示 */}
        <div className="p-3 border border-green-400/30 bg-green-400/5 rounded-sm">
          <span className="text-gray-400">📅 当前范围: </span>
          <span className="text-green-400 font-bold">
            {value[0]} ~ {value[1]}
          </span>
          <span className="text-gray-500 ml-2 text-sm">
            (约{Math.ceil(dayjs(value[1]).diff(dayjs(value[0]), 'day') / 30)}个月)
          </span>
        </div>
      </div>
    </div>
  )
}

export default QuickDateSelectorASCII