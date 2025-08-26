import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Typography, Tag, Button, Spin, message } from 'antd'
import { useNavigate } from 'react-router-dom'
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
    <div className="p-6">
      <Title level={2} className="mb-2">选择回测策略</Title>
      <Paragraph type="secondary" className="mb-6">
        选择一个策略开始回测，每个策略都支持灵活的参数配置
      </Paragraph>

      <Row gutter={[16, 16]}>
        {strategies.map((strategy) => (
          <Col xs={24} sm={12} lg={8} key={strategy.id}>
            <Card
              className="strategy-card transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
              hoverable
              actions={[
                <Button 
                  type="primary" 
                  onClick={() => handleSelectStrategy(strategy.id)}
                  className="w-full"
                >
                  选择策略
                </Button>
              ]}
            >
              <Card.Meta
                title={
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">{strategy.name}</span>
                    <Tag color={getRiskColor(strategy.risk_level)} className="ml-2">
                      {RISK_LEVELS[strategy.risk_level as keyof typeof RISK_LEVELS]?.text || strategy.risk_level}
                    </Tag>
                  </div>
                }
                description={
                  <div>
                    <Paragraph ellipsis={{ rows: 2 }} className="text-gray-600 mb-3">
                      {strategy.description}
                    </Paragraph>
                    <div className="mb-2">
                      <strong className="text-gray-800">支持市场：</strong>
                      {strategy.supported_markets.map(market => (
                        <Tag key={market} className="ml-1">
                          {MARKETS[market as keyof typeof MARKETS]?.icon} {market}
                        </Tag>
                      ))}
                    </div>
                    <div>
                      <Tag className="bg-blue-50 text-blue-700 border-blue-200">{strategy.category}</Tag>
                    </div>
                  </div>
                }
              />
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  )
}

export default StrategySelection