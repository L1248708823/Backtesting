import React from 'react'
import { Select } from 'antd'

const { Option } = Select

interface FrequencyOption {
  value: number
  label: string
  desc: string
}

interface FrequencySelectProps {
  /** 当前选中的频率天数 */
  value: number
  /** 频率变化时的回调函数 */
  onChange: (days: number) => void
  /** 频率选项数据 */
  options?: FrequencyOption[]
}

const defaultOptions: FrequencyOption[] = [
  { value: 7, label: '每周定投', desc: '分散度最高，成本略高' },
  { value: 30, label: '每月定投', desc: '经典选择，平衡效果' },
  { value: 90, label: '每季定投', desc: '降低成本，适合大额' }
]

const FrequencySelect: React.FC<FrequencySelectProps> = ({
  value,
  onChange,
  options = defaultOptions
}) => {
  return (
    <div>
      <div className="text-gray-400 text-sm mb-2">定投频率:</div>
      <Select
        value={value}
        onChange={onChange}
        className="w-full"
        dropdownStyle={{ 
          backgroundColor: 'black', 
          border: '1px solid #4ade80',
          color: '#22c55e'
        }}
        style={{
          color: '#22c55e'
        }}
      >
        {options.map(option => (
          <Option key={option.value} value={option.value}>
            <div className="text-green-400">
              {option.label} ({option.value}天)
            </div>
            <div className="text-gray-500 text-xs">
              {option.desc}
            </div>
          </Option>
        ))}
      </Select>
      <div className="text-gray-500 text-xs mt-1">
        推荐月投: 平衡风险分散和交易成本
      </div>
    </div>
  )
}

export default FrequencySelect