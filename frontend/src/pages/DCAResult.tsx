// -*- coding: utf-8 -*-
/**
 * 定投策略结果展示页面
 * 
 * 提供comprehensive的定投回测结果展示，包括：
 * 1. 核心性能指标概览
 * 2. 交互式权益曲线图表
 * 3. 详细的收益分析
 * 4. 交易记录和统计
 * 5. 风险指标分析
 * 6. 结果导出和分享功能
 * 
 * 设计特点：
 * - 数据驱动：实时获取和展示回测结果
 * - 可视化丰富：多种图表类型展示不同维度数据
 * - 交互性强：支持图表缩放、筛选、对比
 * - 专业分析：提供专业的投资分析报告
 */

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Alert,
  Button,
  Table,
  Tabs,
  Tag,
  Space,
  Typography,
  Spin,
  Empty,
  Tooltip,
  Modal,
  message,
  Descriptions,
  Timeline
} from 'antd';
import {
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  DollarOutlined,
  LineChartOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  ReloadOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

// 类型定义
interface BacktestResult {
  task_id: string;
  config: any;
  status: string;
  
  // 基础结果
  initial_capital: number;
  final_capital: number;
  final_cash: number;
  final_market_value: number;
  
  // 收益指标
  total_return: number;
  annualized_return: number;
  max_drawdown: number;
  sharpe_ratio: number;
  
  // 交易统计
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  
  // 定投特定指标
  investment_count: number;
  skipped_count: number;
  average_cost: number;
  total_invested: number;
  
  // 时间信息
  created_at: string;
  completed_at?: string;
  
  // 详细数据
  equity_curve?: Array<{date: string, value: number}>;
  transactions?: Array<any>;
}

interface BacktestStatus {
  task_id: string;
  status: string;
  progress: number;
  message: string;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

const DCAResultPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [status, setStatus] = useState<BacktestStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detailsVisible, setDetailsVisible] = useState(false);

  // 轮询获取状态
  useEffect(() => {
    if (!taskId) return;

    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/v1/dca/backtest/status/${taskId}`);
        if (response.ok) {
          const statusData = await response.json();
          setStatus(statusData);
          
          if (statusData.status === 'completed') {
            // 获取完整结果
            fetchResult(true);
          } else if (statusData.status === 'failed') {
            setError(statusData.error_message || '回测执行失败');
            setLoading(false);
          }
        } else {
          setError('获取回测状态失败');
          setLoading(false);
        }
      } catch (err) {
        setError('网络请求失败');
        setLoading(false);
      }
    };

    // 立即执行一次
    pollStatus();

    // 如果任务未完成，继续轮询
    const interval = setInterval(() => {
      if (status?.status === 'completed' || status?.status === 'failed') {
        clearInterval(interval);
        return;
      }
      pollStatus();
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId, status?.status]);

  // 获取详细结果
  const fetchResult = async (includeDetails: boolean = false) => {
    try {
      const response = await fetch(
        `/api/v1/dca/backtest/result/${taskId}?include_details=${includeDetails}`
      );
      
      if (response.ok) {
        const resultData = await response.json();
        setResult(resultData);
      } else {
        setError('获取回测结果失败');
      }
    } catch (err) {
      setError('网络请求失败');
    }
    setLoading(false);
  };

  // 加载详细数据
  const loadDetailedData = async () => {
    if (result?.equity_curve && result?.transactions) return; // 已加载
    
    setDetailsVisible(true);
    await fetchResult(true);
  };

  // 刷新结果
  const handleRefresh = () => {
    setLoading(true);
    setError(null);
    fetchResult(true);
  };

  // 下载报告
  const handleDownloadReport = () => {
    // 实现报告下载逻辑
    message.info('报告下载功能开发中...');
  };

  // 分享结果
  const handleShare = () => {
    // 实现分享功能
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      message.success('链接已复制到剪贴板');
    });
  };

  // 渲染加载状态
  if (loading || (status && status.status !== 'completed' && status.status !== 'failed')) {
    return (
      <div style={{ padding: 24 }}>
        <Card>
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" />
            <Title level={4} style={{ marginTop: 16 }}>
              {status?.message || '正在执行回测...'}
            </Title>
            {status && (
              <Progress
                percent={Math.round(status.progress * 100)}
                status={status.status === 'failed' ? 'exception' : 'active'}
                style={{ marginTop: 16, maxWidth: 400, margin: '16px auto' }}
              />
            )}
            <Paragraph type="secondary" style={{ marginTop: 16 }}>
              任务ID: {taskId}
            </Paragraph>
          </div>
        </Card>
      </div>
    );
  }

  // 渲染错误状态
  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <Alert
          type="error"
          message="回测执行失败"
          description={error}
          action={
            <Button size="small" onClick={handleRefresh}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  if (!result) {
    return (
      <div style={{ padding: 24 }}>
        <Empty description="未找到回测结果" />
      </div>
    );
  }

  // 生成权益曲线图表配置
  const getEquityCurveOption = () => {
    if (!result.equity_curve) return {};

    return {
      title: {
        text: '资产增长曲线',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const point = params[0];
          return `
            <div>
              <div>${point.axisValue}</div>
              <div>
                <span style="color: ${point.color};">●</span>
                资产总值: ¥${point.value.toLocaleString()}
              </div>
            </div>
          `;
        }
      },
      xAxis: {
        type: 'category',
        data: result.equity_curve.map(point => point.date),
        axisLabel: {
          formatter: (value: string) => dayjs(value).format('YYYY-MM')
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: (value: number) => `¥${(value / 10000).toFixed(1)}万`
        }
      },
      series: [
        {
          name: '资产总值',
          type: 'line',
          data: result.equity_curve.map(point => point.value),
          smooth: true,
          lineStyle: {
            width: 3
          },
          itemStyle: {
            color: '#1890ff'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: '#1890ff'
              }, {
                offset: 1, color: 'rgba(24, 144, 255, 0.1)'
              }],
              global: false
            }
          }
        }
      ],
      grid: {
        left: 60,
        right: 30,
        top: 60,
        bottom: 60
      }
    };
  };

  // 渲染核心指标卡片
  const renderMetricsCards = () => (
    <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
      <Col xs={24} sm={12} md={6}>
        <Card>
          <Statistic
            title="总收益率"
            value={result.total_return * 100}
            precision={2}
            suffix="%"
            valueStyle={{ 
              color: result.total_return >= 0 ? '#3f8600' : '#cf1322' 
            }}
            prefix={
              result.total_return >= 0 ? <RiseOutlined /> : <FallOutlined />
            }
          />
        </Card>
      </Col>
      
      <Col xs={24} sm={12} md={6}>
        <Card>
          <Statistic
            title="年化收益率"
            value={result.annualized_return * 100}
            precision={2}
            suffix="%"
            valueStyle={{ 
              color: result.annualized_return >= 0 ? '#3f8600' : '#cf1322' 
            }}
          />
        </Card>
      </Col>
      
      <Col xs={24} sm={12} md={6}>
        <Card>
          <Statistic
            title="最大回撤"
            value={result.max_drawdown * 100}
            precision={2}
            suffix="%"
            valueStyle={{ color: '#cf1322' }}
            prefix={<FallOutlined />}
          />
        </Card>
      </Col>
      
      <Col xs={24} sm={12} md={6}>
        <Card>
          <Statistic
            title="夏普比率"
            value={result.sharpe_ratio}
            precision={2}
            valueStyle={{ 
              color: result.sharpe_ratio >= 1 ? '#3f8600' : '#fa8c16' 
            }}
            prefix={<TrophyOutlined />}
          />
        </Card>
      </Col>
    </Row>
  );

  // 渲染资金概览
  const renderCapitalOverview = () => (
    <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
      <Col xs={24} md={12}>
        <Card title="资金概览">
          <Descriptions column={1} size="small">
            <Descriptions.Item label="初始资金">
              ¥{result.initial_capital.toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="最终资金">
              ¥{result.final_capital.toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="现金余额">
              ¥{result.final_cash.toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="持仓市值">
              ¥{result.final_market_value.toLocaleString()}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Col>
      
      <Col xs={24} md={12}>
        <Card title="定投统计">
          <Descriptions column={1} size="small">
            <Descriptions.Item label="投资次数">
              {result.investment_count} 次
            </Descriptions.Item>
            <Descriptions.Item label="跳过次数">
              {result.skipped_count} 次
            </Descriptions.Item>
            <Descriptions.Item label="累计投资">
              ¥{result.total_invested.toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="平均投资额">
              ¥{result.average_cost.toLocaleString()}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Col>
    </Row>
  );

  // 渲染交易记录表格
  const renderTransactionTable = () => {
    if (!result.transactions || result.transactions.length === 0) {
      return <Empty description="暂无交易记录" />;
    }

    const columns = [
      {
        title: '日期',
        dataIndex: 'date',
        key: 'date',
        render: (date: string) => dayjs(date).format('YYYY-MM-DD')
      },
      {
        title: '操作',
        dataIndex: 'action',
        key: 'action',
        render: (action: string) => (
          <Tag color={action === 'buy' ? 'green' : 'red'}>
            {action === 'buy' ? '买入' : '卖出'}
          </Tag>
        )
      },
      {
        title: '数量',
        dataIndex: 'quantity',
        key: 'quantity',
        render: (value: number) => value.toLocaleString()
      },
      {
        title: '价格',
        dataIndex: 'price',
        key: 'price',
        render: (value: number) => `¥${value.toFixed(2)}`
      },
      {
        title: '金额',
        dataIndex: 'amount',
        key: 'amount',
        render: (value: number) => `¥${value.toLocaleString()}`
      },
      {
        title: '手续费',
        dataIndex: 'commission',
        key: 'commission',
        render: (value: number) => `¥${value.toFixed(2)}`
      },
      {
        title: '原因',
        dataIndex: 'reason',
        key: 'reason',
        ellipsis: true
      }
    ];

    return (
      <Table
        columns={columns}
        dataSource={result.transactions}
        rowKey={(record, index) => `${record.date}-${index}`}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条交易记录`
        }}
        size="small"
      />
    );
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 页面头部 */}
      <div style={{ marginBottom: 24 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2}>
              定投回测结果
              <Tag color="green" style={{ marginLeft: 8 }}>
                {result.status === 'completed' ? '已完成' : result.status}
              </Tag>
            </Title>
            <Text type="secondary">
              回测完成时间: {result.completed_at ? dayjs(result.completed_at).format('YYYY-MM-DD HH:mm:ss') : '-'}
            </Text>
          </Col>
          <Col>
            <Space>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={handleRefresh}
              >
                刷新
              </Button>
              <Button 
                icon={<DownloadOutlined />}
                onClick={handleDownloadReport}
              >
                下载报告
              </Button>
              <Button 
                type="primary"
                icon={<ShareAltOutlined />}
                onClick={handleShare}
              >
                分享结果
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 核心指标 */}
      {renderMetricsCards()}

      {/* 资金概览 */}
      {renderCapitalOverview()}

      {/* 权益曲线图表 */}
      <Card 
        title="资产增长曲线" 
        style={{ marginBottom: 24 }}
        extra={
          !result.equity_curve && (
            <Button size="small" onClick={loadDetailedData}>
              加载详细数据
            </Button>
          )
        }
      >
        {result.equity_curve ? (
          <ReactECharts
            option={getEquityCurveOption()}
            style={{ height: 400 }}
          />
        ) : (
          <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Empty 
              description="点击右上角按钮加载详细数据"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          </div>
        )}
      </Card>

      {/* 详细分析标签页 */}
      <Card>
        <Tabs defaultActiveKey="transactions">
          <TabPane tab="交易记录" key="transactions">
            {renderTransactionTable()}
          </TabPane>
          
          <TabPane tab="配置信息" key="config">
            <Descriptions title="回测配置" bordered column={2}>
              <Descriptions.Item label="投资标的">{result.config?.symbol}</Descriptions.Item>
              <Descriptions.Item label="投资金额">¥{result.config?.investment_amount?.toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="投资频率">{result.config?.frequency}</Descriptions.Item>
              <Descriptions.Item label="初始资金">¥{result.config?.initial_capital?.toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="开始日期">{result.config?.start_date}</Descriptions.Item>
              <Descriptions.Item label="结束日期">{result.config?.end_date}</Descriptions.Item>
              <Descriptions.Item label="成本控制">{result.config?.enable_cost_control ? '开启' : '关闭'}</Descriptions.Item>
              <Descriptions.Item label="节假日处理">{result.config?.skip_holidays ? '自动顺延' : '严格执行'}</Descriptions.Item>
            </Descriptions>
          </TabPane>
          
          <TabPane tab="性能分析" key="performance">
            <Alert
              type="info"
              message="投资建议"
              description={
                <div>
                  <Paragraph>
                    基于本次回测结果，我们为您提供以下投资建议：
                  </Paragraph>
                  <ul>
                    <li>
                      <Text strong>收益评价：</Text>
                      {result.annualized_return > 0.08 ? 
                        '年化收益率超过8%，表现优秀' : 
                        result.annualized_return > 0.05 ? 
                        '年化收益率超过5%，表现良好' : 
                        '收益率偏低，建议考虑调整策略参数'
                      }
                    </li>
                    <li>
                      <Text strong>风险评价：</Text>
                      {result.max_drawdown < 0.1 ? 
                        '最大回撤控制在10%以内，风险较低' : 
                        result.max_drawdown < 0.2 ? 
                        '最大回撤在10%-20%之间，风险适中' : 
                        '最大回撤超过20%，风险较高，需要注意'
                      }
                    </li>
                    <li>
                      <Text strong>夏普比率：</Text>
                      {result.sharpe_ratio > 1.5 ? 
                        '夏普比率优秀，风险调整后收益表现良好' : 
                        result.sharpe_ratio > 1 ? 
                        '夏普比率良好' : 
                        '夏普比率偏低，收益与风险的平衡有待改善'
                      }
                    </li>
                  </ul>
                </div>
              }
              style={{ marginBottom: 16 }}
            />
            
            <Row gutter={16}>
              <Col span={12}>
                <Card type="inner" title="风险指标">
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="最大回撤">
                      {(result.max_drawdown * 100).toFixed(2)}%
                    </Descriptions.Item>
                    <Descriptions.Item label="夏普比率">
                      {result.sharpe_ratio.toFixed(2)}
                    </Descriptions.Item>
                    <Descriptions.Item label="胜率">
                      {(result.win_rate * 100).toFixed(1)}%
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
              
              <Col span={12}>
                <Card type="inner" title="交易统计">
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="总交易次数">
                      {result.total_trades} 次
                    </Descriptions.Item>
                    <Descriptions.Item label="盈利交易">
                      {result.winning_trades} 次
                    </Descriptions.Item>
                    <Descriptions.Item label="亏损交易">
                      {result.losing_trades} 次
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default DCAResultPage;