import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Input, InputNumber, Select, DatePicker, message } from 'antd'
import dayjs from 'dayjs'
import { backtestService } from '@/services/backtest'

const { RangePicker } = DatePicker
const { Option } = Select

const DCAConfig: React.FC = () => {
  /** 投资标的代码 - A股ETF代码如510300，美股如SPY */
  const [symbol, setSymbol] = useState('510300')
  /** 每期投资金额（元） - 建议500-5000元，根据个人收入设定 */
  const [investmentAmount, setInvestmentAmount] = useState(1000)
  /** 投资频率天数 - 7天(周投)、30天(月投)、90天(季投) */
  const [frequencyDays, setFrequencyDays] = useState(30)
  /** 回测日期范围 - [开始日期, 结束日期] */
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null)
  /** 初始资金（元） - 用于回测的起始资金 */
  const [initialCash, setInitialCash] = useState(10000)
  /** 回测执行状态 - true:正在执行回测, false:待配置 */
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  // 热门ETF快选数据
  const popularETFs = [
    { code: '510300', name: '沪深300ETF', desc: '大盘蓝筹' },
    { code: '512100', name: '中证1000ETF', desc: '中小盘成长' },
    { code: '159915', name: '创业板ETF', desc: '创新成长' },
    { code: 'SPY', name: '标普500ETF', desc: '美股大盘' },
    { code: 'QQQ', name: '纳斯达克100ETF', desc: '美股科技' }
  ]

  // 投资频率选项
  const frequencyOptions = [
    { value: 7, label: '每周定投', desc: '分散度最高，成本略高' },
    { value: 30, label: '每月定投', desc: '经典选择，平衡效果' },
    { value: 90, label: '每季定投', desc: '降低成本，适合大额' }
  ]

  /** 
   * 快速选择ETF标的
   * @param etfCode ETF代码
   */
  const handleQuickSelect = (etfCode: string) => {
    setSymbol(etfCode)
    const etf = popularETFs.find(e => e.code === etfCode)
    message.success(`已选择 ${etf?.name} (${etfCode})`)
  }

  /** 
   * 启动定投回测
   * 使用统一的backtestService执行DCA策略
   */
  const handleStartBacktest = async () => {
    // 参数验证
    if (!symbol.trim()) {
      message.error('请输入投资标的代码')
      return
    }
    if (!dateRange) {
      message.error('请选择回测时间范围')
      return
    }

    setLoading(true)
    
    try {
      // 使用统一的API service调用DCA回测
      const result = await backtestService.runDCABacktest({
        symbol: symbol.trim(),
        investment_amount: investmentAmount,
        frequency_days: frequencyDays,
        start_date: dateRange[0].format('YYYY-MM-DD'),
        end_date: dateRange[1].format('YYYY-MM-DD'),
        initial_cash: initialCash
      })
      
      message.success(`定投回测完成！总收益率: ${result.total_return?.toFixed(2)}%`)
      console.log('回测结果:', result)
      
      // 跳转到DCA结果页面，传递结果数据
      navigate('/dca/result', { 
        state: { 
          backtestResult: result,
          timestamp: Date.now() 
        } 
      })
      
    } catch (error: any) {
      console.error('回测请求失败:', error)
      
      // 统一错误处理
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          '网络请求失败，请检查后端服务'
      message.error(`回测失败: ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono p-8">
      {/* 终端头部 */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="flex gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <span className="text-gray-500">DCA定投策略配置终端 v1.0</span>
        </div>
        
        <div className="border-l-4 border-green-400 pl-4 py-2 bg-green-400/5 mb-6">
          <div className="text-gray-400 text-sm mb-1">ninja@dca-config:~$</div>
          <div className="text-xl">执行潜行任务 - DCA定投策略配置</div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* 投资标的选择 */}
        <div className="border border-green-400/30 p-6">
          <div className="text-green-400 mb-4">[TARGET_SELECT] 选择修炼标的 🎯</div>
          
          {/* 热门ETF快选 */}
          <div className="mb-4">
            <div className="text-gray-400 text-sm mb-2">快速选择热门ETF:</div>
            <div className="flex flex-wrap gap-2">
              {popularETFs.map(etf => (
                <button
                  key={etf.code}
                  onClick={() => handleQuickSelect(etf.code)}
                  className={`px-3 py-1 border text-xs transition-colors ${
                    symbol === etf.code 
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-gray-400 text-sm mb-2">投资标的代码:</div>
              <Input
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="510300 / SPY"
                className="terminal-input"
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
            
            <div>
              <div className="text-gray-400 text-sm mb-2">每期投资金额 (元):</div>
              <InputNumber
                value={investmentAmount}
                onChange={(value) => setInvestmentAmount(value || 1000)}
                min={100}
                max={100000}
                step={100}
                placeholder="1000"
                className="w-full terminal-input"
                style={{
                  backgroundColor: 'black',
                  borderColor: '#4ade80',
                  color: '#22c55e'
                }}
              />
              <div className="text-gray-500 text-xs mt-1">
                建议金额: 500-5000元，根据收入设定
              </div>
            </div>
          </div>
        </div>

        {/* 投资策略设置 */}
        <div className="border border-green-400/30 p-6">
          <div className="text-green-400 mb-4">[STRATEGY_CONFIG] 投资频率设置 ⚡</div>
          
          <div>
            <div className="text-gray-400 text-sm mb-2">定投频率:</div>
            <Select
              value={frequencyDays}
              onChange={setFrequencyDays}
              className="w-full"
              dropdownStyle={{ backgroundColor: 'black', border: '1px solid #4ade80' }}
            >
              {frequencyOptions.map(option => (
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
        </div>

        {/* 回测时间设置 */}
        <div className="border border-green-400/30 p-6">
          <div className="text-green-400 mb-4">[TIME_RANGE] 时空穿越设置 🕒</div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-gray-400 text-sm mb-2">回测时间范围:</div>
              <RangePicker
                value={dateRange}
                onChange={setDateRange}
                className="w-full"
                style={{
                  backgroundColor: 'black',
                  borderColor: '#4ade80',
                  color: '#22c55e'
                }}
                disabledDate={(current) => current && current > dayjs().endOf('day')}
              />
              <div className="text-gray-500 text-xs mt-1">
                建议至少1年以上，长期定投效果更明显
              </div>
            </div>
            
            <div>
              <div className="text-gray-400 text-sm mb-2">初始资金 (元):</div>
              <InputNumber
                value={initialCash}
                onChange={(value) => setInitialCash(value || 10000)}
                min={1000}
                step={1000}
                placeholder="10000"
                className="w-full"
                style={{
                  backgroundColor: 'black',
                  borderColor: '#4ade80',
                  color: '#22c55e'
                }}
              />
              <div className="text-gray-500 text-xs mt-1">
                回测用资金，建议大于投资金额10倍
              </div>
            </div>
          </div>

          {/* 快速时间选择 */}
          <div className="mt-4">
            <div className="text-gray-400 text-sm mb-2">快速选择:</div>
            <div className="flex flex-wrap gap-2">
              {[
                { label: '最近1年', months: 12 },
                { label: '最近2年', months: 24 },
                { label: '最近3年', months: 36 },
                { label: '最近5年', months: 60 }
              ].map(period => (
                <button
                  key={period.label}
                  onClick={() => {
                    const end = dayjs()
                    const start = end.subtract(period.months, 'month')
                    setDateRange([start, end])
                  }}
                  className="px-3 py-1 border border-green-400/50 hover:bg-green-400/10 text-green-400 text-sm transition-colors"
                >
                  {period.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 执行按钮 */}
        <div className="border border-green-400/30 p-6 text-center">
          <div className="text-green-400 mb-4">[EXECUTE] 开始潜行任务 🥷</div>
          
          <Button
            type="primary"
            size="large"
            loading={loading}
            onClick={handleStartBacktest}
            className="ninja-button"
            style={{
              backgroundColor: 'transparent',
              borderColor: '#22c55e',
              color: '#22c55e',
              height: '48px',
              fontSize: '16px',
              fontFamily: 'monospace'
            }}
          >
            {loading ? '正在执行回测...' : '> 启动DCA定投回测'}
          </Button>

          <div className="mt-4 text-gray-500 text-sm">
            <div>⚠️ 忍者提醒: 投资有风险，历史数据仅供参考</div>
            <div>💡 修炼心得: 定投的精髓在于坚持，而非时机选择</div>
          </div>
        </div>

      </div>
    </div>
  )
}

export default DCAConfig