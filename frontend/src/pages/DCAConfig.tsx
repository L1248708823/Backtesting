// -*- coding: utf-8 -*-
/**
 * 定投策略配置页面
 * 
 * 提供用户友好的定投策略参数配置界面，包括：
 * 1. 基础参数配置（标的、金额、频率等）
 * 2. 高级参数配置（成本控制、风险管理等）
 * 3. 回测时间设置
 * 4. 实时参数验证和提示
 * 5. 配置预览和保存功能
 * 
 * 设计特点：
 * - 渐进式配置：从基础到高级，降低学习门槛
 * - 智能提示：实时验证和建议
 * - 可视化预览：参数效果直观展示
 * - 响应式设计：适配不同屏幕尺寸
 */

import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Select,
  InputNumber,
  DatePicker,
  Switch,
  Button,
  Card,
  Steps,
  Alert,
  Tooltip,
  Space,
  Divider,
  Row,
  Col,
  Typography,
  Tag,
  Spin,
  message
} from 'antd';
import {
  QuestionCircleOutlined,
  RocketOutlined,
  SettingOutlined,
  CalendarOutlined,
  DollarOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

// 类型定义
/** 定投策略配置接口 - 包含所有定投回测所需的参数设置 */
interface DCAConfig {
  // 基础配置
  /** 投资标的代码，如510300（沪深300ETF）、SPY（标普500ETF） */
  symbol: string;
  
  /** 每期投资金额（元），建议为月收入的10-30%，最小建议500元 */
  investment_amount: number;
  
  /** 投资频率 - daily:每日, weekly:每周, monthly:每月（推荐）, quarterly:每季度 */
  frequency: string;
  
  // 时间配置
  /** 回测开始日期，格式：YYYY-MM-DD */
  start_date: string;
  
  /** 回测结束日期，格式：YYYY-MM-DD */
  end_date: string;
  
  /** 初始资金（元），用于回测的起始资金量，建议大于单次投资金额的10倍 */
  initial_capital: number;
  
  // 可选配置
  /** 每月投资日期（1-28号），仅月度和季度投资时有效。建议设为发薪日后的1-5号，避免月末日期差异 */
  investment_day?: number;
  
  /** 节假日处理方式 - true: 遇节假日自动顺延到下一交易日, false: 严格按日期执行 */
  skip_holidays: boolean;
  
  /** 单次投资最大占组合比例限制（0.01-0.5），防止单次投资过于集中。推荐值：0.1（10%） */
  max_single_weight: number;
  
  /** 是否启用成本控制优化 - true: 当交易成本占比过高时暂停投资, false: 严格执行投资计划 */
  enable_cost_control: boolean;
  
  /** 最小成本效益比（0.001-0.05），仅在成本控制开启时有效。当交易成本占投资金额比例超过此值时跳过本次投资 */
  min_cost_ratio: number;
  
  // 交易成本配置
  /** 佣金费率（0-0.01），一般券商为万分之2.5-3，即0.0003左右 */
  commission_rate: number;
  
  /** 最小佣金金额（元），一般券商设定为5元，不足5元按5元收取 */
  min_commission: number;
  
  /** 印花税费率（0-0.01），A股卖出时收取千分之1，买入免收 */
  stamp_duty_rate: number;
  
  /** 过户费费率（0-0.001），A股交易时收取成交金额的万分之0.2 */
  transfer_fee_rate: number;
}

/** 标的验证结果接口 - 用于验证投资标的是否有效 */
interface SymbolValidation {
  /** 标的代码 */
  symbol: string;
  
  /** 是否有效 - true: 标的存在且可交易, false: 标的不存在或无法获取数据 */
  is_valid: boolean;
  
  /** 验证结果消息，失败时显示错误原因 */
  message: string;
  
  /** 最新交易日期，格式：YYYY-MM-DD，仅验证成功时有效 */
  latest_date?: string;
  
  /** 最新价格（元），仅验证成功时有效 */
  latest_price?: number;
}

/** 参数定义接口 - 描述策略参数的配置和验证规则 */
interface ParameterDefinition {
  /** 参数名称，用作唯一标识 */
  name: string;
  
  /** 参数类型 - text:文本, number:数值, select:单选, boolean:布尔值等 */
  type: string;
  
  /** 参数默认值 */
  default: any;
  
  /** 参数说明，向用户解释此参数的作用和建议值 */
  description: string;
  
  /** 是否为必填参数 */
  required: boolean;
  
  /** 数值参数的最小值限制，仅type为number时有效 */
  min_value?: number;
  
  /** 数值参数的最大值限制，仅type为number时有效 */
  max_value?: number;
  
  /** 选择类型参数的可选项，格式：[{value: 'key', label: 'display_name'}] */
  options?: Array<{value: string, label: string}>;
  
  /** 自定义验证规则，用于复杂参数验证 */
  validation_rules?: any;
  
  /** 参数依赖关系，当其他参数满足特定条件时此参数才生效 */
  depends_on?: Array<{parameter: string, values: any[]}>;
}

const DCAConfigPage: React.FC = () => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [symbolValidating, setSymbolValidating] = useState(false);
  const [symbolValidation, setSymbolValidation] = useState<SymbolValidation | null>(null);
  const [parameters, setParameters] = useState<ParameterDefinition[]>([]);
  const [config, setConfig] = useState<Partial<DCAConfig>>({
    // 默认值
    investment_amount: 1000,
    frequency: 'monthly',
    initial_capital: 100000,
    investment_day: 1,
    skip_holidays: true,
    max_single_weight: 0.1,
    enable_cost_control: true,
    min_cost_ratio: 0.01,
    commission_rate: 0.0003,
    min_commission: 5.0,
    stamp_duty_rate: 0.001,
    transfer_fee_rate: 0.00002
  });

  // 步骤配置
  const steps = [
    {
      title: '基础配置',
      icon: <DollarOutlined />,
      description: '选择投资标的和基本参数'
    },
    {
      title: '时间设置',
      icon: <CalendarOutlined />,
      description: '设置回测时间范围'
    },
    {
      title: '高级选项',
      icon: <SettingOutlined />,
      description: '风险控制和成本管理'
    },
    {
      title: '确认启动',
      icon: <RocketOutlined />,
      description: '预览配置并启动回测'
    }
  ];

  // 频率选项
  const frequencyOptions = [
    { value: 'daily', label: '每日投资', description: '适合金额较小，手续费极低的情况' },
    { value: 'weekly', label: '每周投资', description: '平衡了成本和风险分散效果' },
    { value: 'monthly', label: '每月投资（推荐）', description: '最常见选择，平衡收益和成本' },
    { value: 'quarterly', label: '每季度投资', description: '适合大额投资，降低交易频率' }
  ];

  // 常用ETF标的
  const popularETFs = [
    { code: '510300', name: '沪深300ETF', market: 'A股', description: '跟踪沪深300指数' },
    { code: '159919', name: '沪深300ETF', market: 'A股', description: '跟踪沪深300指数' },
    { code: '512100', name: '中证1000ETF', market: 'A股', description: '跟踪中证1000指数' },
    { code: 'SPY', name: 'SPDR S&P 500', market: '美股', description: '跟踪标普500指数' },
    { code: 'QQQ', name: 'Invesco QQQ', market: '美股', description: '跟踪纳斯达克100指数' },
    { code: 'VTI', name: 'Vanguard Total Stock', market: '美股', description: '跟踪美国全市场' }
  ];

  // 组件挂载时获取参数定义
  useEffect(() => {
    fetchParameterDefinitions();
  }, []);

  // 获取参数定义
  const fetchParameterDefinitions = async () => {
    try {
      const response = await fetch('/api/v1/dca/parameters');
      if (response.ok) {
        const data = await response.json();
        setParameters(data);
      }
    } catch (error) {
      console.error('获取参数定义失败:', error);
    }
  };

  // 验证标的代码
  const validateSymbol = async (symbol: string) => {
    if (!symbol || symbol.length < 3) return;
    
    setSymbolValidating(true);
    try {
      const response = await fetch(`/api/v1/dca/validate-symbol/${symbol}`);
      if (response.ok) {
        const validation = await response.json();
        setSymbolValidation(validation);
        
        if (!validation.is_valid) {
          message.warning(validation.message);
        }
      }
    } catch (error) {
      console.error('验证标的失败:', error);
      setSymbolValidation({
        symbol,
        is_valid: false,
        message: '验证失败，请检查网络连接'
      });
    }
    setSymbolValidating(false);
  };

  // 处理标的输入变化
  const handleSymbolChange = (value: string) => {
    setConfig({ ...config, symbol: value });
    setSymbolValidation(null);
    
    // 防抖验证
    const timeoutId = setTimeout(() => {
      validateSymbol(value);
    }, 500);
    
    return () => clearTimeout(timeoutId);
  };

  // 处理快速选择标的
  const handleQuickSelectSymbol = (etf: typeof popularETFs[0]) => {
    form.setFieldValue('symbol', etf.code);
    handleSymbolChange(etf.code);
    message.success(`已选择 ${etf.name} (${etf.code})`);
  };

  // 处理表单值变化
  const handleFormChange = (changedFields: any, allFields: any) => {
    const newConfig = { ...config };
    
    changedFields.forEach((field: any) => {
      newConfig[field.name[0] as keyof DCAConfig] = field.value;
    });
    
    setConfig(newConfig);
  };

  // 验证当前步骤
  const validateCurrentStep = async (): Promise<boolean> => {
    try {
      switch (currentStep) {
        case 0: // 基础配置
          await form.validateFields(['symbol', 'investment_amount', 'frequency']);
          if (!symbolValidation?.is_valid) {
            message.error('请选择有效的投资标的');
            return false;
          }
          return true;
          
        case 1: // 时间设置
          await form.validateFields(['dateRange', 'initial_capital']);
          return true;
          
        case 2: // 高级选项
          await form.validateFields(['max_single_weight', 'commission_rate']);
          return true;
          
        default:
          return true;
      }
    } catch (error) {
      return false;
    }
  };

  // 下一步
  const handleNext = async () => {
    const isValid = await validateCurrentStep();
    if (isValid && currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  // 上一步
  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // 启动回测
  const handleStartBacktest = async () => {
    try {
      setLoading(true);
      
      // 构建回测配置
      const backtestConfig = {
        ...config,
        start_date: config.start_date,
        end_date: config.end_date
      };
      
      // 发送回测请求
      const response = await fetch('/api/v1/dca/backtest/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(backtestConfig)
      });
      
      if (response.ok) {
        const result = await response.json();
        message.success('定投回测已启动！');
        
        // 跳转到结果页面
        window.location.href = `/backtest/result/${result.task_id}`;
      } else {
        const error = await response.json();
        message.error(`启动回测失败: ${error.detail}`);
      }
    } catch (error) {
      console.error('启动回测失败:', error);
      message.error('启动回测失败，请检查网络连接');
    }
    setLoading(false);
  };

  // 渲染基础配置步骤
  const renderBasicConfig = () => (
    <Card>
      <Title level={4}>
        <DollarOutlined /> 基础投资参数
      </Title>
      
      {/* 快速选择标的 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Text strong>快速选择热门ETF：</Text>
        <div style={{ marginTop: 8 }}>
          <Space wrap>
            {popularETFs.map(etf => (
              <Tag
                key={etf.code}
                style={{ cursor: 'pointer', padding: '4px 8px' }}
                onClick={() => handleQuickSelectSymbol(etf)}
              >
                <Space>
                  <span>{etf.code}</span>
                  <span style={{ color: '#666' }}>({etf.name})</span>
                  <Tag size="small">{etf.market}</Tag>
                </Space>
              </Tag>
            ))}
          </Space>
        </div>
      </Card>
      
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="symbol"
            label={
              <Space>
                投资标的
                <Tooltip title="输入ETF代码，如510300（沪深300）或SPY（标普500）">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
            rules={[{ required: true, message: '请输入投资标的代码' }]}
          >
            <Input
              placeholder="请输入标的代码，如510300"
              onChange={(e) => handleSymbolChange(e.target.value)}
              suffix={symbolValidating ? <Spin size="small" /> : null}
            />
          </Form.Item>
          
          {/* 标的验证结果 */}
          {symbolValidation && (
            <Alert
              type={symbolValidation.is_valid ? 'success' : 'error'}
              message={symbolValidation.message}
              style={{ marginBottom: 16 }}
              showIcon
              {...(symbolValidation.is_valid && symbolValidation.latest_price && {
                description: `最新价格: ¥${symbolValidation.latest_price} (${symbolValidation.latest_date})`
              })}
            />
          )}
        </Col>
        
        <Col span={12}>
          <Form.Item
            name="investment_amount"
            label={
              <Space>
                每期投资金额
                <Tooltip title="建议设置为月收入的10-30%，最小建议500元降低成本影响">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
            rules={[
              { required: true, message: '请输入投资金额' },
              { type: 'number', min: 100, max: 1000000, message: '投资金额需在100-1000000之间' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="1000"
              min={100}
              max={1000000}
              step={100}
              addonAfter="元"
              formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
            />
          </Form.Item>
        </Col>
      </Row>
      
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="frequency"
            label="投资频率"
            rules={[{ required: true, message: '请选择投资频率' }]}
          >
            <Select placeholder="选择投资频率">
              {frequencyOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  <Space direction="vertical" size={0}>
                    <span>{option.label}</span>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {option.description}
                    </Text>
                  </Space>
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        
        <Col span={12}>
          {(config.frequency === 'monthly' || config.frequency === 'quarterly') && (
            <Form.Item
              name="investment_day"
              label={
                <Space>
                  每月投资日期
                  <Tooltip title="建议选择发薪日后的1-5号，避免月末日期差异">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              }
              rules={[
                { required: true, message: '请选择投资日期' },
                { type: 'number', min: 1, max: 28, message: '投资日期需在1-28号之间' }
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                min={1}
                max={28}
                addonAfter="号"
              />
            </Form.Item>
          )}
        </Col>
      </Row>
      
      {/* 投资建议 */}
      <Alert
        type="info"
        icon={<InfoCircleOutlined />}
        message="投资建议"
        description={
          <ul style={{ marginBottom: 0, paddingLeft: 16 }}>
            <li>建议选择流动性好的宽基指数ETF，如沪深300、中证500等</li>
            <li>投资金额应根据个人收入水平合理设置，避免影响日常生活</li>
            <li>定投最适合长期投资（建议≥3年），短期效果不明显</li>
            <li>选择月度投资可以很好平衡成本和风险分散效果</li>
          </ul>
        }
      />
    </Card>
  );

  // 渲染时间设置步骤
  const renderTimeConfig = () => (
    <Card>
      <Title level={4}>
        <CalendarOutlined /> 回测时间设置
      </Title>
      
      <Row gutter={16}>
        <Col span={16}>
          <Form.Item
            name="dateRange"
            label="回测时间范围"
            rules={[{ required: true, message: '请选择回测时间范围' }]}
          >
            <RangePicker
              style={{ width: '100%' }}
              disabledDate={(current) => current && current > dayjs().endOf('day')}
              onChange={(dates) => {
                if (dates && dates[0] && dates[1]) {
                  setConfig({
                    ...config,
                    start_date: dates[0].format('YYYY-MM-DD'),
                    end_date: dates[1].format('YYYY-MM-DD')
                  });
                }
              }}
            />
          </Form.Item>
        </Col>
        
        <Col span={8}>
          <Form.Item
            name="initial_capital"
            label={
              <Space>
                初始资金
                <Tooltip title="用于回测的初始资金量，应大于单次投资金额的10倍以上">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
            rules={[
              { required: true, message: '请输入初始资金' },
              { type: 'number', min: 1000, message: '初始资金不能少于1000元' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={1000}
              step={10000}
              addonAfter="元"
              formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
            />
          </Form.Item>
        </Col>
      </Row>
      
      {/* 时间范围建议 */}
      <Alert
        type="info"
        message="时间范围建议"
        description={
          <div>
            <Paragraph style={{ marginBottom: 8 }}>
              <Text strong>推荐回测时间：</Text>
            </Paragraph>
            <ul style={{ marginBottom: 0, paddingLeft: 16 }}>
              <li><Text strong>短期测试：</Text> 6个月 - 1年，快速了解策略表现</li>
              <li><Text strong>中期验证：</Text> 2-3年，包含一轮市场周期</li>
              <li><Text strong>长期验证：</Text> 5年以上，充分验证定投效果</li>
              <li><Text strong>历史回测：</Text> 2015年至今，包含牛熊市场</li>
            </ul>
          </div>
        }
      />
      
      {/* 快速时间选择 */}
      <Card size="small" style={{ marginTop: 16 }}>
        <Text strong>快速选择：</Text>
        <div style={{ marginTop: 8 }}>
          <Space wrap>
            {[
              { label: '最近1年', months: 12 },
              { label: '最近2年', months: 24 },
              { label: '最近3年', months: 36 },
              { label: '最近5年', months: 60 }
            ].map(period => (
              <Button
                key={period.label}
                size="small"
                onClick={() => {
                  const endDate = dayjs();
                  const startDate = endDate.subtract(period.months, 'month');
                  form.setFieldValue('dateRange', [startDate, endDate]);
                  setConfig({
                    ...config,
                    start_date: startDate.format('YYYY-MM-DD'),
                    end_date: endDate.format('YYYY-MM-DD')
                  });
                }}
              >
                {period.label}
              </Button>
            ))}
          </Space>
        </div>
      </Card>
    </Card>
  );

  // 渲染高级配置步骤
  const renderAdvancedConfig = () => (
    <Card>
      <Title level={4}>
        <SettingOutlined /> 高级配置选项
      </Title>
      
      {/* 风险控制 */}
      <Card type="inner" title="风险控制" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="max_single_weight"
              label={
                <Space>
                  单次投资最大比例
                  <Tooltip title="单次投资不能超过组合总值的此比例，防止投资过于集中">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              }
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0.01}
                max={0.5}
                step={0.01}
                addonAfter="%"
                formatter={(value) => `${(Number(value) * 100).toFixed(0)}`}
                parser={(value) => Number(value!.replace('%', '')) / 100}
              />
            </Form.Item>
          </Col>
          
          <Col span={12}>
            <Form.Item
              name="skip_holidays"
              label="节假日处理"
              valuePropName="checked"
            >
              <Switch
                checkedChildren="自动顺延"
                unCheckedChildren="严格执行"
              />
            </Form.Item>
          </Col>
        </Row>
      </Card>
      
      {/* 成本控制 */}
      <Card type="inner" title="成本控制" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="enable_cost_control"
              label="成本控制"
              valuePropName="checked"
            >
              <Switch
                checkedChildren="开启"
                unCheckedChildren="关闭"
                onChange={(checked) => setConfig({ ...config, enable_cost_control: checked })}
              />
            </Form.Item>
          </Col>
          
          {config.enable_cost_control && (
            <Col span={12}>
              <Form.Item
                name="min_cost_ratio"
                label={
                  <Space>
                    最小成本效益比
                    <Tooltip title="当交易成本占投资金额比例超过此值时跳过本次投资">
                      <QuestionCircleOutlined />
                    </Tooltip>
                  </Space>
                }
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0.001}
                  max={0.05}
                  step={0.001}
                  addonAfter="%"
                  formatter={(value) => `${(Number(value) * 100).toFixed(1)}`}
                  parser={(value) => Number(value!.replace('%', '')) / 100}
                />
              </Form.Item>
            </Col>
          )}
        </Row>
      </Card>
      
      {/* 交易成本 */}
      <Card type="inner" title="交易成本设置">
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="commission_rate"
              label="佣金费率"
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                max={0.01}
                step={0.0001}
                addonAfter="‰"
                formatter={(value) => `${(Number(value) * 10000).toFixed(1)}`}
                parser={(value) => Number(value!.replace('‰', '')) / 10000}
              />
            </Form.Item>
          </Col>
          
          <Col span={12}>
            <Form.Item
              name="min_commission"
              label="最小佣金"
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                step={1}
                addonAfter="元"
              />
            </Form.Item>
          </Col>
        </Row>
        
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="stamp_duty_rate"
              label="印花税费率"
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                max={0.01}
                step={0.0001}
                addonAfter="‰"
                formatter={(value) => `${(Number(value) * 1000).toFixed(1)}`}
                parser={(value) => Number(value!.replace('‰', '')) / 1000}
              />
            </Form.Item>
          </Col>
          
          <Col span={12}>
            <Form.Item
              name="transfer_fee_rate"
              label="过户费费率"
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                max={0.001}
                step={0.00001}
                addonAfter="‰"
                formatter={(value) => `${(Number(value) * 10000).toFixed(2)}`}
                parser={(value) => Number(value!.replace('‰', '')) / 10000}
              />
            </Form.Item>
          </Col>
        </Row>
      </Card>
      
      <Alert
        type="info"
        message="成本设置建议"
        description="以上成本参数基于A股市场的一般标准设置，实际费率请根据您的券商标准调整。美股市场的费率结构可能有所不同。"
      />
    </Card>
  );

  // 渲染确认启动步骤
  const renderConfirmConfig = () => (
    <Card>
      <Title level={4}>
        <RocketOutlined /> 配置确认
      </Title>
      
      <Alert
        type="success"
        message="配置完成！"
        description="请确认以下配置信息无误后启动回测。"
        style={{ marginBottom: 24 }}
      />
      
      {/* 配置预览 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card type="inner" title="基础配置" size="small">
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <div><Text strong>投资标的：</Text>{config.symbol}</div>
              <div><Text strong>投资金额：</Text>¥{config.investment_amount?.toLocaleString()}</div>
              <div><Text strong>投资频率：</Text>{frequencyOptions.find(f => f.value === config.frequency)?.label}</div>
              {config.investment_day && (
                <div><Text strong>投资日期：</Text>每月{config.investment_day}号</div>
              )}
            </Space>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card type="inner" title="时间设置" size="small">
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <div><Text strong>开始日期：</Text>{config.start_date}</div>
              <div><Text strong>结束日期：</Text>{config.end_date}</div>
              <div><Text strong>初始资金：</Text>¥{config.initial_capital?.toLocaleString()}</div>
              <div><Text strong>回测天数：</Text>
                {config.start_date && config.end_date && 
                  dayjs(config.end_date).diff(dayjs(config.start_date), 'day')
                }天
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
      
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card type="inner" title="风险控制" size="small">
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <div><Text strong>最大投资比例：</Text>{(config.max_single_weight! * 100).toFixed(1)}%</div>
              <div><Text strong>节假日处理：</Text>{config.skip_holidays ? '自动顺延' : '严格执行'}</div>
              <div><Text strong>成本控制：</Text>{config.enable_cost_control ? '开启' : '关闭'}</div>
              {config.enable_cost_control && (
                <div><Text strong>成本效益比：</Text>{(config.min_cost_ratio! * 100).toFixed(2)}%</div>
              )}
            </Space>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card type="inner" title="交易成本" size="small">
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <div><Text strong>佣金费率：</Text>{(config.commission_rate! * 10000).toFixed(1)}‰</div>
              <div><Text strong>最小佣金：</Text>¥{config.min_commission}</div>
              <div><Text strong>印花税：</Text>{(config.stamp_duty_rate! * 1000).toFixed(1)}‰</div>
              <div><Text strong>过户费：</Text>{(config.transfer_fee_rate! * 10000).toFixed(2)}‰</div>
            </Space>
          </Card>
        </Col>
      </Row>
      
      {/* 预期效果提示 */}
      <Alert
        type="info"
        style={{ marginTop: 16 }}
        message="预期回测时间"
        description={
          `根据您的配置，预计回测将在30秒内完成。回测完成后您可以查看详细的收益分析、交易记录和风险指标。`
        }
      />
    </Card>
  );

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>定投策略配置</Title>
      <Paragraph type="secondary">
        配置您的定投策略参数，系统将模拟历史数据进行回测分析。
      </Paragraph>
      
      {/* 步骤导航 */}
      <Steps
        current={currentStep}
        items={steps}
        style={{ marginBottom: 32 }}
      />
      
      <Form
        form={form}
        layout="vertical"
        initialValues={config}
        onValuesChange={handleFormChange}
      >
        {/* 步骤内容 */}
        {currentStep === 0 && renderBasicConfig()}
        {currentStep === 1 && renderTimeConfig()}
        {currentStep === 2 && renderAdvancedConfig()}
        {currentStep === 3 && renderConfirmConfig()}
        
        {/* 操作按钮 */}
        <Card style={{ marginTop: 24, textAlign: 'center' }}>
          <Space size="large">
            {currentStep > 0 && (
              <Button size="large" onClick={handlePrev}>
                上一步
              </Button>
            )}
            
            {currentStep < steps.length - 1 ? (
              <Button type="primary" size="large" onClick={handleNext}>
                下一步
              </Button>
            ) : (
              <Button
                type="primary"
                size="large"
                loading={loading}
                onClick={handleStartBacktest}
                icon={<RocketOutlined />}
              >
                启动回测
              </Button>
            )}
          </Space>
        </Card>
      </Form>
    </div>
  );
};

export default DCAConfigPage;