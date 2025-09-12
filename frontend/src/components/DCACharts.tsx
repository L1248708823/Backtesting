import React from 'react'
import ReactECharts from 'echarts-for-react'
import { Card } from 'antd'

interface DCAChartsProps {
  /** 标的每日价格序列 - 用于绘制价格走势 */
  daily_prices: number[]
  /** 每日投资组合价值序列 - 用于绘制资产增长 */
  daily_portfolio_values: number[]
  /** 每日收益率序列 - 基于标的价格计算 */
  daily_returns: number[]
  /** 每日日期序列 - 对应价格和收益率的时间轴 */
  daily_dates: string[]
  /** 定投执行记录 - 每次买入的详细信息 */
  investment_records?: Array<{
    /** 买入日期 YYYY-MM-DD */
    date: string
    /** 定投期数(第几次) */
    round: number
    /** 买入价格(元/份) */
    price: number
    /** 买入份额数 */
    shares: number
    /** 实际投入金额(元) */
    amount: number
    /** 当时总资产价值(元) */
    market_value: number
  }>
  /** 卖出交易记录 - 详细的卖出执行信息 */
  sell_records?: Array<{
    /** 卖出日期 YYYY-MM-DD */
    date: string
    /** 卖出价格(元/份) */
    price: number
    /** 卖出份额数 */
    size: number
    /** 卖出金额(元) */
    value: number
  }>
}

const DCACharts: React.FC<DCAChartsProps> = ({
  daily_prices,
  daily_portfolio_values,
  daily_dates,
  investment_records = [],
  sell_records = []
}) => {
  // 忍者终端风格配色方案
  const ninjaColors = {
    bg: '#000000',
    text: '#22c55e',
    grid: '#1f2937',
    price: '#22c55e',      // 价格曲线 - 绿色
    portfolio: '#f59e0b',  // 投资组合曲线 - 黄色
    buyPoint: '#3b82f6',   // 买入点 - 蓝色
    sellPoint: '#ef4444',  // 卖出点 - 红色
    tooltip: '#1f2937'
  }

  /** 计算回撤数据 */
  const calculateDrawdowns = () => {
    if (!daily_prices || daily_prices.length === 0) return []
    
    const drawdowns = []
    let peak = daily_prices[0]
    
    for (let i = 0; i < daily_prices.length; i++) {
      const currentPrice = daily_prices[i]
      if (currentPrice > peak) {
        peak = currentPrice
      }
      
      const drawdown = ((peak - currentPrice) / peak) * 100
      drawdowns.push(drawdown)
    }
    
    return drawdowns
  }

  /** 回撤分析图配置 */
  const getDrawdownChartOption = () => {
    const drawdowns = calculateDrawdowns()
    
    return {
      backgroundColor: ninjaColors.bg,
      title: {
        text: '📉 最大回撤分析图',
        left: 'center',
        textStyle: {
          color: ninjaColors.text,
          fontSize: 16,
          fontFamily: 'monospace'
        }
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: ninjaColors.tooltip,
        borderColor: ninjaColors.text,
        textStyle: {
          color: ninjaColors.text,
          fontFamily: 'monospace'
        },
        formatter: function(params: any) {
          const dataIndex = params[0]?.dataIndex
          if (dataIndex === undefined) return ''
          
          const date = daily_dates[dataIndex]
          const drawdown = drawdowns[dataIndex]
          
          return `
            <div style="font-family: monospace;">
              <div style="color: #22c55e; font-weight: bold;">${date}</div>
              <div style="margin-top: 4px;">
                回撤: <span style="color: #ef4444;">-${drawdown?.toFixed(2) || 0}%</span>
              </div>
            </div>
          `
        }
      },
      grid: {
        left: '50px',
        right: '50px',
        top: '80px',
        bottom: '50px',
        borderColor: ninjaColors.grid
      },
      xAxis: {
        type: 'category',
        data: daily_dates,
        axisLine: {
          lineStyle: { color: ninjaColors.grid }
        },
        axisLabel: {
          color: ninjaColors.text,
          fontFamily: 'monospace',
          fontSize: 10,
          formatter: function(value: string) {
            return value.slice(5)
          }
        },
        splitLine: {
          show: true,
          lineStyle: {
            color: ninjaColors.grid,
            type: 'dashed'
          }
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: { color: ninjaColors.grid }
        },
        axisLabel: {
          color: ninjaColors.text,
          fontFamily: 'monospace',
          fontSize: 10,
          formatter: function(value: number) {
            return '-' + Math.abs(value).toFixed(1) + '%'
          }
        },
        splitLine: {
          lineStyle: {
            color: ninjaColors.grid,
            type: 'dashed'
          }
        },
        max: 0,
        min: function(value: any) {
          return value.min < -1 ? value.min : -1
        }
      },
      series: [
        {
          name: '回撤深度',
          type: 'line',
          data: drawdowns.map(d => -d), // 转为负值显示
          smooth: true,
          lineStyle: {
            color: ninjaColors.sellPoint,
            width: 2
          },
          itemStyle: {
            color: ninjaColors.sellPoint
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(239, 68, 68, 0.1)' },
                { offset: 1, color: 'rgba(239, 68, 68, 0.3)' }
              ]
            }
          }
        }
      ]
    }
  }

  /** 双Y轴价格与投资组合图配置 */
  const getDualAxisChartOption = () => {
    // 买入点数据 (在对应的价格点标记买入)
    const buyPoints = investment_records.map(record => ({
      name: `买入点 #${record.round}`,
      coord: [record.date, record.price],  // 使用买入价格
      value: record.price,
      amount: record.amount,
      price: record.price,
      shares: record.shares
    }))

    // 卖出点数据 (在对应的价格点标记卖出)
    const sellPoints = sell_records.map((record, index) => ({
      name: `卖出点 #${index + 1}`,
      coord: [record.date, record.price],  // 使用卖出价格
      value: record.price,
      price: record.price,
      shares: record.size
    }))

    return {
      backgroundColor: ninjaColors.bg,
      title: {
        text: '📈 每日价格走势 vs 💰 投资组合价值 (可缩放)',
        left: 'center',
        textStyle: {
          color: ninjaColors.text,
          fontSize: 16,
          fontFamily: 'monospace'
        },
        subtext: '鼠标滚轮缩放 | 底部滑块调整时间范围 | 显示完整交易日数据',
        subtextStyle: {
          color: '#9ca3af',
          fontSize: 12,
          fontFamily: 'monospace'
        }
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: ninjaColors.tooltip,
        borderColor: ninjaColors.text,
        textStyle: {
          color: ninjaColors.text,
          fontFamily: 'monospace'
        },
        formatter: function(params: any) {
          const dataIndex = params[0]?.dataIndex
          if (dataIndex === undefined) return ''
          
          const date = daily_dates[dataIndex]
          const price = daily_prices[dataIndex]
          const portfolioValue = daily_portfolio_values[dataIndex]
          
          return `
            <div style="font-family: monospace;">
              <div style="color: #22c55e; font-weight: bold;">${date}</div>
              <div style="margin-top: 4px;">
                标的价格: <span style="color: #22c55e;">¥${price?.toFixed(2) || 0}</span><br/>
                组合价值: <span style="color: #f59e0b;">¥${portfolioValue?.toLocaleString() || 0}</span>
              </div>
            </div>
          `
        }
      },
      legend: {
        data: ['标的价格', '投资组合价值', '买入点', '卖出点'],
        top: '30px',
        textStyle: {
          color: ninjaColors.text,
          fontFamily: 'monospace'
        }
      },
      grid: {
        left: '60px',
        right: '80px',
        top: '80px',
        bottom: '100px', // 增加底部空间给dataZoom
        borderColor: ninjaColors.grid
      },
      // 添加数据缩放功能
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100,
          filterMode: 'filter'
        },
        {
          type: 'slider',
          start: 0,
          end: 100,
          height: 30,
          bottom: 10,
          borderColor: ninjaColors.text,
          textStyle: {
            color: ninjaColors.text,
            fontFamily: 'monospace'
          },
          handleStyle: {
            color: ninjaColors.price,
            borderColor: ninjaColors.text
          },
          moveHandleStyle: {
            color: ninjaColors.portfolio
          },
          selectedDataBackground: {
            lineStyle: {
              color: ninjaColors.price
            },
            areaStyle: {
              color: 'rgba(34, 197, 94, 0.2)'
            }
          }
        }
      ],
      xAxis: {
        type: 'category',
        data: daily_dates,
        axisLine: {
          lineStyle: { color: ninjaColors.grid }
        },
        axisLabel: {
          color: ninjaColors.text,
          fontFamily: 'monospace',
          fontSize: 10,
          formatter: function(value: string) {
            return value.slice(5) // 只显示月-日
          }
        },
        splitLine: {
          show: true,
          lineStyle: {
            color: ninjaColors.grid,
            type: 'dashed'
          }
        }
      },
      yAxis: [
        {
          type: 'value',
          name: '标的价格 (¥)',
          nameTextStyle: {
            color: ninjaColors.price,
            fontFamily: 'monospace'
          },
          position: 'left',
          axisLine: {
            lineStyle: { color: ninjaColors.price }
          },
          axisLabel: {
            color: ninjaColors.price,
            fontFamily: 'monospace',
            fontSize: 10,
            formatter: function(value: number) {
              return '¥' + value.toFixed(2)
            }
          },
          splitLine: {
            lineStyle: {
              color: ninjaColors.grid,
              type: 'dashed'
            }
          }
        },
        {
          type: 'value',
          name: '投资组合价值 (¥)',
          nameTextStyle: {
            color: ninjaColors.portfolio,
            fontFamily: 'monospace'
          },
          position: 'right',
          axisLine: {
            lineStyle: { color: ninjaColors.portfolio }
          },
          axisLabel: {
            color: ninjaColors.portfolio,
            fontFamily: 'monospace',
            fontSize: 10,
            formatter: function(value: number) {
              return '¥' + (value / 1000).toFixed(0) + 'k'
            }
          },
          splitLine: {
            show: false // 右轴不显示网格线，避免重复
          }
        }
      ],
      series: [
        {
          name: '标的价格',
          type: 'line',
          yAxisIndex: 0, // 使用左Y轴
          data: daily_prices,
          smooth: true,
          lineStyle: {
            color: ninjaColors.price,
            width: 2
          },
          itemStyle: {
            color: ninjaColors.price
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(34, 197, 94, 0.15)' },
                { offset: 1, color: 'rgba(34, 197, 94, 0.02)' }
              ]
            }
          }
        },
        {
          name: '投资组合价值',
          type: 'line',
          yAxisIndex: 1, // 使用右Y轴
          data: daily_portfolio_values,
          smooth: true,
          lineStyle: {
            color: ninjaColors.portfolio,
            width: 2
          },
          itemStyle: {
            color: ninjaColors.portfolio
          }
        },
        // 买入点标记 (在左Y轴对应的价格位置)
        {
          name: '买入点',
          type: 'scatter',
          yAxisIndex: 0, // 使用左Y轴
          data: buyPoints.map(point => point.coord),
          symbolSize: 8,
          itemStyle: {
            color: ninjaColors.buyPoint,
            borderColor: '#ffffff',
            borderWidth: 1
          },
          tooltip: {
            formatter: function(params: any) {
              const pointIndex = params.dataIndex
              const point = buyPoints[pointIndex]
              if (!point) return ''
              
              return `
                <div style="font-family: monospace;">
                  <div style="color: #3b82f6; font-weight: bold;">买入点 #${point.name.split('#')[1]}</div>
                  <div style="margin-top: 4px;">
                    日期: <span style="color: #22c55e;">${point.coord[0]}</span><br/>
                    买入价格: <span style="color: #f59e0b;">¥${point.price.toFixed(2)}</span><br/>
                    买入金额: <span style="color: #22c55e;">¥${point.amount.toFixed(2)}</span><br/>
                    买入份额: <span style="color: #06b6d4;">${point.shares}</span>
                  </div>
                </div>
              `
            }
          }
        },
        // 卖出点标记
        ...(sellPoints.length > 0 ? [{
          name: '卖出点',
          type: 'scatter',
          yAxisIndex: 0, // 使用左Y轴
          data: sellPoints.map(point => point.coord),
          symbolSize: 10,
          symbol: 'triangle',
          itemStyle: {
            color: ninjaColors.sellPoint,
            borderColor: '#ffffff',
            borderWidth: 1
          },
          tooltip: {
            formatter: function(params: any) {
              const pointIndex = params.dataIndex
              const point = sellPoints[pointIndex]
              if (!point) return ''
              
              return `
                <div style="font-family: monospace;">
                  <div style="color: #ef4444; font-weight: bold;">卖出点 #${point.name.split('#')[1]}</div>
                  <div style="margin-top: 4px;">
                    日期: <span style="color: #22c55e;">${point.coord[0]}</span><br/>
                    卖出价格: <span style="color: #f59e0b;">¥${point.price.toFixed(2)}</span><br/>
                    卖出份额: <span style="color: #ef4444;">${point.shares}</span>
                  </div>
                </div>
              `
            }
          }
        }] : [])
      ]
    }
  }

  return (
    <div className="space-y-6 ninja-chart-container">
      {/* 双Y轴价格与投资组合图 */}
      <Card className="ninja-chart-card">
        <div className="p-4">
          <ReactECharts
            option={getDualAxisChartOption()}
            style={{ height: '450px', width: '100%' }}
            theme="dark"
            opts={{ renderer: 'canvas', devicePixelRatio: window.devicePixelRatio || 1 }}
          />
        </div>
      </Card>

      {/* 回撤分析图 */}
      <Card className="ninja-chart-card">
        <div className="p-4">
          <ReactECharts
            option={getDrawdownChartOption()}
            style={{ height: '300px', width: '100%' }}
            theme="dark"
            opts={{ renderer: 'canvas', devicePixelRatio: window.devicePixelRatio || 1 }}
          />
        </div>
      </Card>
    </div>
  )
}

export default DCACharts