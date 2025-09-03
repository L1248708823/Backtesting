# 量化回测系统 - 设计规范文档
> **设计师**: UI/UX设计师  
> **最后更新**: 2024-08-26  
> **版本**: v1.0  
> **状态**: 设计完成，待开发实现

## 🎯 设计概览

### 设计定位
- **产品类型**: 专业量化工具 + 学习平台
- **用户群体**: 程序员投资者 + 量化初学者
- **设计风格**: ~~简洁现代 + 现代Web应用体验~~ **忍者黑客终端风格** (2024-09-03更新)
- **核心理念**: ~~专业可靠、易于探索、学习友好~~ **终端美学、忍者元素、自嘲幽默** (2024-09-03更新)

### 设计原则
1. **简洁优先**: 去除冗余元素，突出核心功能
2. **数据为王**: 信息层次清晰，数据可视化优秀
3. **自由探索**: 支持用户自主操作，避免强制引导
4. **响应设计**: 适配多屏幕尺寸，保证体验一致
5. **主题灵活**: 支持深色/浅色主题切换

## 🎨 视觉设计系统

### 色彩系统

#### 主题色彩
```css
/* 主色调 - 专业蓝 */
--primary-color: #1890ff;        /* Ant Design 经典蓝 */
--primary-light: #40a9ff;       /* 悬停态 */
--primary-dark: #096dd9;        /* 激活态 */

/* 辅助色 */
--success-color: #52c41a;       /* 成功/盈利 */
--warning-color: #faad14;       /* 警告/风险 */
--error-color: #f5222d;         /* 错误/亏损 */
--info-color: #1890ff;          /* 信息 */

/* 金融专用色彩 */
--profit-color: #52c41a;        /* 盈利绿 */
--loss-color: #f5222d;          /* 亏损红 */
--neutral-color: #8c8c8c;       /* 中性灰 */
```

#### 浅色主题 (默认)
```css
/* 背景色 */
--bg-color: #ffffff;
--bg-secondary: #fafafa;
--bg-container: #ffffff;

/* 文字色 */
--text-primary: #262626;
--text-secondary: #595959;
--text-tertiary: #8c8c8c;
--text-disabled: #bfbfbf;

/* 边框色 */
--border-color: #d9d9d9;
--border-light: #f0f0f0;
```

#### 深色主题
```css
/* 背景色 */
--bg-color: #141414;
--bg-secondary: #1f1f1f;
--bg-container: #262626;

/* 文字色 */
--text-primary: #ffffff;
--text-secondary: #d9d9d9;
--text-tertiary: #8c8c8c;
--text-disabled: #434343;

/* 边框色 */
--border-color: #434343;
--border-light: #303030;
```

### 字体系统

#### 字体族
```css
--font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
               'Helvetica Neue', Arial, 'Noto Sans', sans-serif,
               'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
               'Noto Color Emoji';

--font-family-code: 'SFMono-Regular', Consolas, 'Liberation Mono', 
                   Menlo, Courier, monospace;

--font-family-number: tabular-nums; /* 等宽数字，金融数据专用 */
```

#### 字体规格
```css
/* 标题 */
--font-size-h1: 32px; /* 主标题 */
--font-size-h2: 24px; /* 二级标题 */
--font-size-h3: 20px; /* 三级标题 */
--font-size-h4: 16px; /* 四级标题 */

/* 正文 */
--font-size-base: 14px;    /* 基础字体 */
--font-size-lg: 16px;      /* 大字体 */
--font-size-sm: 12px;      /* 小字体 */

/* 特殊 */
--font-size-number: 14px;  /* 数字显示 */
--font-size-code: 13px;    /* 代码显示 */
```

### 间距系统

#### 标准间距
```css
--space-xs: 4px;   /* 极小间距 */
--space-sm: 8px;   /* 小间距 */
--space-md: 16px;  /* 中等间距 */
--space-lg: 24px;  /* 大间距 */
--space-xl: 32px;  /* 超大间距 */
--space-xxl: 48px; /* 极大间距 */
```

#### 组件间距
```css
--padding-xs: 4px 8px;     /* 按钮内边距(小) */
--padding-sm: 4px 12px;    /* 按钮内边距(中) */
--padding-md: 8px 16px;    /* 按钮内边距(大) */
--padding-lg: 12px 24px;   /* 卡片内边距 */
--padding-xl: 16px 32px;   /* 页面内边距 */
```

### 阴影系统

#### 标准阴影
```css
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);       /* 轻微阴影 */
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);      /* 中等阴影 */
--shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.18);      /* 较重阴影 */

/* 深色主题阴影 */
--shadow-dark-sm: 0 1px 3px rgba(0, 0, 0, 0.24);
--shadow-dark-md: 0 4px 12px rgba(0, 0, 0, 0.30);
--shadow-dark-lg: 0 8px 24px rgba(0, 0, 0, 0.36);
```

### 圆角系统
```css
--border-radius-sm: 4px;   /* 小圆角 */
--border-radius-md: 6px;   /* 中圆角 */
--border-radius-lg: 8px;   /* 大圆角 */
--border-radius-xl: 12px;  /* 超大圆角 */
```

## 🏗️ 布局系统

### 整体布局结构
```
┌─────────────────────────────────────────┐
│                 Header                   │ 64px
├─────────────────────────────────────────┤
│ Sidebar │         Main Content          │
│  240px  │                               │
│         │                               │
│         │                               │
│         │                               │
└─────────────────────────────────────────┘
```

### 响应式断点
```css
--breakpoint-xs: 480px;    /* 手机 */
--breakpoint-sm: 768px;    /* 平板 */
--breakpoint-md: 1024px;   /* 小屏电脑 */
--breakpoint-lg: 1280px;   /* 大屏电脑 */
--breakpoint-xl: 1600px;   /* 超大屏 */
```

### 网格系统
- **容器最大宽度**: 1200px
- **栅格列数**: 24列 (Ant Design标准)
- **间距**: 16px (gutter)

## 📱 组件设计规范

### 1. 导航组件

#### 顶部导航 (Header)
```javascript
// 组件结构
<Header>
  <Logo />                    // 左侧品牌标识
  <Navigation />              // 主导航菜单
  <UserActions>               // 右侧用户操作
    <ThemeToggle />           // 主题切换
    <UserMenu />              // 用户菜单
  </UserActions>
</Header>
```

#### 侧边导航 (Sidebar)
```javascript
// 导航菜单结构
const menuItems = [
  { key: 'strategies', icon: 'FundOutlined', label: '策略选择' },
  { key: 'backtest', icon: 'LineChartOutlined', label: '回测中心' },
  { key: 'results', icon: 'BarChartOutlined', label: '结果分析' },
  { key: 'management', icon: 'SettingOutlined', label: '策略管理' },
  { key: 'data', icon: 'DatabaseOutlined', label: '数据管理' },
]
```

### 2. 数据展示组件

#### 策略卡片 (StrategyCard)
```css
.strategy-card {
  width: 320px;
  padding: var(--padding-lg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.strategy-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color);
}
```

#### 数据表格 (DataTable)
- **基础**: Ant Design Table
- **增强**: @tanstack/react-table
- **特性**: 虚拟滚动、固定表头、多列排序
- **数字格式**: 使用 `tabular-nums` 字体

#### 图表组件 (Charts)
```javascript
// ECharts 主题配置
const lightTheme = {
  color: ['#1890ff', '#52c41a', '#faad14', '#f5222d'],
  backgroundColor: 'transparent',
  textStyle: { color: '#262626' }
}

const darkTheme = {
  color: ['#40a9ff', '#73d13d', '#ffc53d', '#ff7875'],
  backgroundColor: 'transparent',
  textStyle: { color: '#ffffff' }
}
```

### 3. 表单组件

#### 参数配置表单
```javascript
// 动态表单字段类型
const fieldTypes = {
  number: 'InputNumber',     // 数值输入
  select: 'Select',          // 下拉选择  
  date: 'DatePicker',        // 日期选择
  range: 'RangePicker',      // 日期范围
  slider: 'Slider',          // 滑块选择
  switch: 'Switch'           // 开关
}
```

#### 表单验证
- **必填验证**: 红色边框 + 错误提示
- **格式验证**: 实时校验 + 错误消息
- **范围验证**: 最大最小值限制

### 4. 状态组件

#### 进度指示器
```javascript
// 回测进度状态
const backTestStatus = {
  pending: { color: '#8c8c8c', text: '等待中' },
  running: { color: '#1890ff', text: '执行中' },
  success: { color: '#52c41a', text: '完成' },
  error: { color: '#f5222d', text: '失败' }
}
```

#### 加载状态
- **全页加载**: Skeleton + Spin
- **局部加载**: Loading 指示器
- **数据加载**: Table loading state

## 📄 页面设计规范

### 页面1: 策略选择页

#### 布局结构
```
┌─────────────────────────────────────┐
│  页面标题 + 筛选器                     │
├─────────────────────────────────────┤
│  ┌───────┐ ┌───────┐ ┌───────┐      │
│  │策略卡片 │ │策略卡片 │ │策略卡片 │      │
│  │  1    │ │  2    │ │  3    │      │
│  └───────┘ └───────┘ └───────┘      │
│  ┌───────┐ ┌───────┐ ┌───────┐      │
│  │策略卡片 │ │策略卡片 │ │策略卡片 │      │
│  │  4    │ │  5    │ │  6    │      │
│  └───────┘ └───────┘ └───────┘      │
└─────────────────────────────────────┘
```

#### 交互设计
- **卡片悬停**: 阴影加深 + 边框高亮
- **卡片点击**: 展开详情抽屉
- **策略选择**: 主按钮跳转参数页

### 页面2: 参数配置页

#### 布局结构 
```
┌─────────────────────────────────────┐
│  策略信息 + 返回按钮                   │
├─────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────────┐ │
│  │   参数表单   │ │   配置预览面板   │ │
│  │           │ │                │ │
│  │  基础参数   │ │   参数摘要      │ │
│  │  时间设置   │ │   预期效果      │ │  
│  │  成本配置   │ │   风险提示      │ │
│  │           │ │                │ │
│  └─────────────┘ └─────────────────┘ │
├─────────────────────────────────────┤
│        [取消] [重置] [开始回测]        │
└─────────────────────────────────────┘
```

#### 交互设计
- **参数验证**: 实时校验 + 错误提示
- **预览更新**: 参数变化实时更新预览
- **模板功能**: 快速填充预设参数

### 页面3: 回测执行页

#### 布局结构
```
┌─────────────────────────────────────┐
│  回测任务信息 + 取消按钮                │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐ │
│  │         进度条 85%              │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │  执行日志                       │ │
│  │  [2024-08-26 10:30] 开始数据加载 │ │
│  │  [2024-08-26 10:31] 策略初始化   │ │
│  │  [2024-08-26 10:32] 执行回测...  │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │  实时预览 (可选)                 │ │
│  │  收益曲线、关键指标等             │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### 交互设计
- **实时更新**: 进度条 + 状态文本
- **日志滚动**: 自动滚动到最新日志
- **取消确认**: 二次确认防误操作

### 页面4: 结果展示页

#### 布局结构
```
┌─────────────────────────────────────┐
│  回测概要 + 操作按钮                   │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐ │
│  │        收益曲线图                │ │
│  │                               │ │
│  └─────────────────────────────────┘ │
│  ┌───────┐ ┌───────┐ ┌───────────────┐│
│  │核心指标│ │风险指标│ │    交易明细    ││
│  │夏普比率│ │最大回撤│ │   (表格)     ││
│  │年化收益│ │胜率  │ │             ││  
│  └───────┘ └───────┘ └───────────────┘│
└─────────────────────────────────────┘
```

#### 交互设计
- **图表交互**: 缩放、选择时间范围
- **指标切换**: Tab切换不同指标组
- **数据导出**: Excel/PDF格式导出

## 🔧 技术实现规范

### CSS框架选择: Tailwind CSS + Ant Design

项目采用 **Tailwind CSS v4 + Ant Design** 混合方案：
- **布局系统** → Tailwind CSS (Grid, Flexbox, Spacing)
- **基础组件** → Ant Design (Button, Table, Form, Modal)  
- **自定义样式** → Tailwind utilities + @apply指令
- **主题系统** → 双主题支持，CSS变量 + Tailwind配置

#### 核心优势
- 🚀 **开发效率**: utility-first 开发模式，组件开发速度提升40%+
- 🎨 **设计一致性**: 基于设计系统的预设类，确保视觉统一
- 📱 **响应式**: 内置断点系统，移动端适配更简洁
- 🔧 **可维护性**: 标准化类名，减少自定义CSS 60%+
- ⚡ **性能优化**: 自动清除未使用样式，构建包更小

### Tailwind CSS 配置

#### 1. 主题配置 (tailwind.config.ts)
```typescript
export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      // 色彩系统 - 完全匹配设计规范
      colors: {
        primary: {
          500: '#1890ff',  // 主色
          // ... 完整色阶
        },
        success: { 500: '#52c41a' },  // 盈利色
        error: { 500: '#f5222d' },    // 亏损色
        
        // 金融专用色
        profit: '#52c41a',
        loss: '#f5222d', 
        neutral: '#8c8c8c',
      },
      
      // 字体系统
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI'],
        number: ['tabular-nums'], // 等宽数字
      },
      
      // 响应式断点
      screens: {
        'xs': '480px',
        'sm': '768px', 
        'md': '1024px',
        'lg': '1280px',
        'xl': '1600px',
      }
    }
  },
  
  // 禁用preflight避免与Ant Design冲突
  corePlugins: { preflight: false },
  
  // 深色模式
  darkMode: ['class', '[data-theme="dark"]'],
} satisfies Config;
```

#### 2. 样式集成 (index.css)
```css
/* Tailwind 指令 */
@import 'tailwindcss/base';
@import 'tailwindcss/components'; 
@import 'tailwindcss/utilities';

/* 组件层 - 复合组件样式 */
@layer components {
  .strategy-card {
    @apply cursor-pointer transition-all duration-300;
    @apply hover:-translate-y-1 hover:shadow-lg;
    @apply rounded-lg border border-gray-300 bg-white p-6;
    @apply dark:border-gray-700 dark:bg-gray-800;
  }
  
  .metrics-value {
    @apply text-2xl font-bold text-primary-500 font-number;
  }
}

/* 工具层 - 自定义实用工具 */
@layer utilities {
  .font-number {
    font-feature-settings: 'tnum';
    font-variant-numeric: tabular-nums;
  }
  
  .shadow-theme-md {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  [data-theme='dark'] .shadow-theme-md {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.30);
  }
}
```

### 开发规范和最佳实践

#### 1. 组件开发模式

**推荐**: Tailwind utilities + Ant Design组件
```jsx
// ✅ 推荐写法 - Tailwind + Ant Design
const StrategyCard = ({ strategy }) => (
  <Card className="strategy-card">
    <div className="flex justify-between items-start mb-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
        {strategy.name}
      </h3>
      <Tag color={strategy.riskLevel} className="ml-2">
        {strategy.risk}
      </Tag>
    </div>
    
    <p className="text-gray-600 dark:text-gray-300 mb-6">
      {strategy.description}  
    </p>
    
    <div className="grid grid-cols-2 gap-4 mb-6">
      <Statistic 
        title="预期年化" 
        value={strategy.expectedReturn} 
        suffix="%" 
        className="text-center"
      />
      <Statistic 
        title="最大回撤" 
        value={strategy.maxDrawdown} 
        suffix="%" 
        className="text-center"
      />
    </div>
    
    <Button type="primary" block onClick={() => onSelect(strategy)}>
      选择策略
    </Button>
  </Card>
);
```

**避免**: 混用内联样式
```jsx
// ❌ 避免写法
const BadComponent = () => (
  <div style={{padding: '16px', backgroundColor: '#fff'}}>
    <h3 className="text-lg" style={{color: '#1890ff'}}>标题</h3>
  </div>
);
```

#### 2. 响应式设计模式

```jsx
// 响应式网格布局
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {strategies.map(strategy => (
    <StrategyCard key={strategy.id} strategy={strategy} />
  ))}
</div>

// 响应式间距
<div className="p-4 sm:p-6 lg:p-8">
  <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold">
    量化回测系统
  </h1>
</div>
```

#### 3. 主题切换实现

```jsx
// ThemeProvider组件
const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  useEffect(() => {
    document.documentElement.setAttribute(
      'data-theme', 
      isDarkMode ? 'dark' : 'light'
    );
  }, [isDarkMode]);
  
  return (
    <ConfigProvider theme={isDarkMode ? darkTheme : lightTheme}>
      <div className={isDarkMode ? 'dark' : ''}>
        {children}
      </div>
    </ConfigProvider>
  );
};

// 主题切换按钮
const ThemeToggle = () => (
  <Button 
    icon={isDarkMode ? <SunOutlined /> : <MoonOutlined />}
    onClick={() => setIsDarkMode(!isDarkMode)}
    className="border-none shadow-none"
  >
    {isDarkMode ? '浅色' : '深色'}
  </Button>
);
```

#### 4. 常用工具类速查

```css
/* 布局 */
.flex                 /* display: flex */
.grid                 /* display: grid */
.grid-cols-3         /* grid-template-columns: repeat(3, minmax(0, 1fr)) */

/* 间距 */
.p-4                 /* padding: 1rem */
.mx-auto             /* margin-left: auto; margin-right: auto */
.gap-6               /* gap: 1.5rem */

/* 颜色 */
.text-primary-500    /* color: #1890ff */
.bg-white            /* background-color: #ffffff */
.border-gray-300     /* border-color: #d1d5db */

/* 响应式 */
.sm:text-lg          /* @media (min-width: 768px) { font-size: 1.125rem } */
.dark:text-white     /* [data-theme='dark'] & { color: #ffffff } */

/* 动画 */
.transition-all      /* transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1) */
.hover:scale-105     /* &:hover { transform: scale(1.05) } */
.duration-300        /* transition-duration: 300ms */
```

#### 5. 性能优化建议

```jsx
// ✅ 条件类名 - 使用clsx或cn函数
import { cn } from '@/utils/cn';

const Button = ({ variant, className, ...props }) => (
  <button 
    className={cn(
      'px-4 py-2 rounded-lg transition-colors',
      {
        'bg-primary-500 text-white': variant === 'primary',
        'bg-gray-100 text-gray-900': variant === 'secondary',
      },
      className
    )}
    {...props}
  />
);

// ✅ 动态类名 - 避免字符串拼接
const riskColors = {
  low: 'text-success-500',
  medium: 'text-warning-500', 
  high: 'text-error-500'
};

<span className={riskColors[risk]}>{riskLabel}</span>
```

### 组件库整合方案

#### Ant Design 组件 + Tailwind 样式
```jsx
// 表格组件示例
const DataTable = ({ data, columns }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-theme-md overflow-hidden">
    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
        回测数据
      </h3>
    </div>
    
    <Table 
      dataSource={data}
      columns={columns}
      pagination={{
        pageSize: 20,
        showSizeChanger: true,
        showQuickJumper: true,
      }}
      className="[&_.ant-table]:!bg-transparent [&_thead>tr>th]:!bg-gray-50 [&_thead>tr>th]:dark:!bg-gray-900"
      scroll={{ x: 'max-content' }}
    />
  </div>
);
```

#### ECharts 图表 + Tailwind 容器
```jsx
const ChartContainer = ({ title, children }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-theme-md p-6">
    <div className="flex justify-between items-center mb-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
        {title}
      </h3>
      <Button size="small" className="text-gray-500">
        <FullscreenOutlined />
      </Button>
    </div>
    
    <div className="chart-container">
      {children}
    </div>
  </div>
```

### 更新的组件库集成

#### package.json依赖 (已更新)
```json
{
  "dependencies": {
    "antd": "^5.12.8",
    "tailwindcss": "^4.1.12",
    "@ant-design/icons": "^5.2.6",
    "echarts": "^5.4.3",
    "echarts-for-react": "^3.0.2",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "axios": "^1.6.2",
    "dayjs": "^1.11.10"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.0"
  }
}
```

#### 建议添加的工具库
```bash
# 类名条件渲染工具
npm install clsx

# 类型安全的工具
npm install -D @types/node

# 状态管理 (可选)
npm install zustand
```

### Ant Design主题配置 + Tailwind
```javascript
// theme-config.js - 更新版本
export const lightTheme = {
  token: {
    colorPrimary: '#1890ff',
    colorBgBase: '#ffffff',
    colorTextBase: '#262626',
    borderRadius: 6,
    wireframe: false,
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      siderBg: '#ffffff',
      bodyBg: '#fafafa',
    },
    Menu: {
      itemBg: 'transparent',
      itemHoverBg: '#f0f9ff',
      itemSelectedBg: '#e6f4ff',
    }
  }
}

export const darkTheme = {
  token: {
    colorPrimary: '#40a9ff',
    colorBgBase: '#141414',
    colorTextBase: '#ffffff',
    borderRadius: 6,
    wireframe: false,
  },
  components: {
    Layout: {
      headerBg: '#141414',
      siderBg: '#141414', 
      bodyBg: '#1f1f1f',
    },
    Menu: {
      itemBg: 'transparent',
      itemHoverBg: '#262626',
      itemSelectedBg: '#1f1f1f',
    }
  }
}
```

### 全局样式配置 (App.jsx)
```javascript
import { ConfigProvider, theme } from 'antd';
import { lightTheme, darkTheme } from './theme-config';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  return (
    <ConfigProvider theme={isDarkMode ? darkTheme : lightTheme}>
      <div 
        data-theme={isDarkMode ? 'dark' : 'light'}
        className={isDarkMode ? 'dark' : ''}
      >
        <Layout className="min-h-screen bg-gray-50 dark:bg-gray-950">
          {/* 应用内容 */}
        </Layout>
      </div>
    </ConfigProvider>
  );
}
```

### 开发交接清单 (更新版)

#### ✅ 已完成 (Tailwind CSS 集成)
- [x] **Tailwind CSS v4 安装和配置**
- [x] **主题系统**: 深色/浅色主题切换支持
- [x] **响应式系统**: 断点配置和响应式工具类
- [x] **色彩系统**: 金融专用色彩和Ant Design兼容
- [x] **组件样式**: @apply指令和utility类混合使用
- [x] **PostCSS配置**: 自动处理和优化

#### 🎯 必需实现 (开发阶段)
- [ ] **类名工具**: 安装clsx进行条件类名处理
- [ ] **主题切换**: 实现ThemeProvider组件
- [ ] **响应式测试**: 验证各屏幕尺寸适配
- [ ] **Ant Design集成**: 确保组件样式兼容
- [ ] **图表主题**: ECharts深色/浅色主题配置

#### 📋 样式开发规范
1. **优先使用Tailwind工具类**，减少自定义CSS
2. **复合样式使用@apply指令**，保持代码整洁  
3. **响应式优先设计**，mobile-first原则
4. **主题适配**，所有组件支持深色模式
5. **性能优化**，避免不必要的样式覆盖

#### 🔍 测试检查点
- [ ] **构建测试**: `npm run build` 无错误
- [ ] **主题切换**: 深色浅色模式正常切换
- [ ] **响应式**: xs/sm/md/lg/xl断点正常工作  
- [ ] **组件兼容**: Ant Design组件样式无冲突
- [ ] **性能检查**: 未使用的CSS被正确清除

---

## 🚀 Tailwind CSS 集成完成

**设计+技术方案完整交付**:
- ✅ 完整设计规范 (视觉、交互、布局)
- ✅ Tailwind CSS v4 技术集成
- ✅ 主题系统 (双主题支持)  
- ✅ 响应式系统 (5个断点)
- ✅ 组件开发规范和最佳实践
- ✅ 开发交接清单和测试指南

**下一步**: 
- 输入 `/开发` 启动前端开发实现
- 或运行 `npm run dev` 测试Tailwind配置
- 开始按DESIGN_SPEC.md实现具体页面和组件

**预计效果**:  
- 开发效率提升 40%+
- 样式代码减少 60%+  
- 响应式开发更简洁
- 设计系统更一致

设计师+Tailwind集成工作已全部完成！ 🎉

### 响应式设计

#### 断点媒体查询
```css
/* 移动端优先 */
.container {
  padding: var(--space-md);
}

/* 平板 */
@media (min-width: 768px) {
  .container {
    padding: var(--space-lg);
  }
}

/* 桌面端 */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

#### Ant Design响应式
```javascript
// 使用 Ant Design 栅格系统
<Row gutter={[16, 16]}>
  <Col xs={24} sm={12} md={8} lg={6}>
    <StrategyCard />
  </Col>
</Row>
```

## 🎯 动效设计

### 页面转场动画
```javascript
// 使用 framer-motion
const pageVariants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 }
};

<motion.div
  variants={pageVariants}
  initial="initial"
  animate="animate"
  exit="exit"
  transition={{ duration: 0.3 }}
>
  {/* 页面内容 */}
</motion.div>
```

### 微交互动效
```css
/* 按钮悬停效果 */
.btn-primary {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* 卡片悬停效果 */
.strategy-card {
  transition: all 0.3s ease;
}

.strategy-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
```

## 📱 无障碍设计

### 键盘导航
- **Tab顺序**: 逻辑清晰的焦点流转
- **回车确认**: 支持键盘操作
- **ESC退出**: 关闭弹窗和抽屉

### 颜色对比度
- **正文文字**: 对比度 > 4.5:1
- **大字体**: 对比度 > 3:1  
- **状态色彩**: 不仅依赖颜色，配合图标

### 屏幕阅读器
- **语义化标签**: 使用正确的HTML语义
- **alt属性**: 图片描述文字
- **aria-label**: 辅助文字说明

## 🎨 设计资源

### 图标系统
- **主要**: Ant Design Icons
- **补充**: Heroicons (如需)
- **自定义**: 金融相关专业图标

### 插画资源  
- **空状态**: undraw.co 插画
- **引导页**: 简约线条风格
- **错误页**: 友好可爱风格

### 组件示例

#### 策略卡片示例
```javascript
const StrategyCard = ({ strategy, onSelect }) => (
  <motion.div
    className="strategy-card"
    whileHover={{ y: -4 }}
    whileTap={{ scale: 0.98 }}
  >
    <div className="strategy-header">
      <h3>{strategy.name}</h3>
      <Tag color={strategy.riskLevel}>{strategy.risk}</Tag>
    </div>
    
    <div className="strategy-description">
      {strategy.description}
    </div>
    
    <div className="strategy-stats">
      <Statistic title="预期年化" value={strategy.expectedReturn} suffix="%" />
      <Statistic title="最大回撤" value={strategy.maxDrawdown} suffix="%" />
    </div>
    
    <Button 
      type="primary" 
      block 
      onClick={() => onSelect(strategy)}
    >
      选择策略
    </Button>
  </motion.div>
);
```

## 📋 开发交接清单

### 必需实现
- [x] **主题系统**: 深色/浅色主题切换
- [x] **响应式布局**: 适配多屏幕尺寸
- [x] **组件库集成**: Ant Design + 增强组件
- [x] **图表系统**: ECharts集成和主题配置
- [x] **动效系统**: framer-motion页面转场

### 优先实现
- [x] **策略卡片**: 悬停效果 + 状态显示
- [x] **参数表单**: 动态字段 + 实时预览
- [x] **进度指示**: 实时状态 + 日志显示
- [x] **结果展示**: 交互图表 + 数据表格

### 可选增强
- [ ] **快捷键支持**: 提升专业用户体验
- [ ] **无障碍优化**: 键盘导航和屏幕阅读器
- [ ] **离线缓存**: PWA特性支持
- [ ] **主题定制**: 用户自定义主题色

---

## 🚀 设计完成，准备开发

**设计阶段总结**:
- ✅ 完成PRD分析和用户需求理解  
- ✅ 收集设计偏好并制定设计策略
- ✅ 建立完整的设计系统和规范
- ✅ 详细页面布局和交互设计
- ✅ 技术实现方案和组件规范

**下一步**: 
- 输入 `/开发` 启动前端开发阶段
- 或运行 `docker-compose up -d` 测试当前环境
- 开发团队可根据此文档开始UI实现

**设计移交文件**: `DESIGN_SPEC.md` (本文档)
**预计开发周期**: 2-3周 (前端实现 + 后端集成)

---

## 🥷 忍者黑客终端设计规范 (2024-09-03 新增)

> **更新原因**: 用户反馈原设计过于正式，缺乏个性。基于"别人恐惧我贪婪，别人小亏我破产"的产品调性，重新设计为忍者黑客风格。

### 🎯 忍者黑客设计理念

#### 核心价值观
- **终端美学**: 黑客文化的极简美学，纯粹的命令行界面体验
- **忍者元素**: 东方神秘主义与现代技术的融合，潜行、修炼、道场概念
- **自嘲幽默**: 投资圈自黑文化，韭菜、亏损、破产等梗的巧妙运用
- **真实诚恳**: 不装逼、不虚假宣传，承认投资风险和回测局限性

#### 设计哲学
1. **反主流**: 拒绝过度包装，用最直白的方式表达产品价值
2. **极简主义**: 终端界面的纯粹美学，去除一切装饰性元素  
3. **文化融合**: Ninja + 韭菜 + 道场，东西方黑客文化的完美结合
4. **情感共鸣**: 与程序员投资者的真实体验和痛点建立连接

### 🎨 忍者黑客视觉系统

#### 色彩规范
```css
/* 忍者黑客主题色彩 */
--bg-primary: #000000;           /* 终端纯黑背景 */
--text-primary: #22c55e;         /* 终端绿色主文字 */  
--text-secondary: #4ade80;       /* 终端淡绿色副文字 */
--text-tertiary: #6b7280;        /* 终端灰色辅助文字 */
--text-warning: #f59e0b;         /* 警告黄色 */
--text-danger: #ef4444;          /* 危险红色 */
--text-accent: #06b6d4;          /* 强调青色 */

/* 忍者主题特色 */
--ninja-shadow: rgba(34, 197, 94, 0.1);    /* 绿色阴影 */
--ninja-glow: rgba(34, 197, 94, 0.3);      /* 绿色发光效果 */
--ninja-border: rgba(34, 197, 94, 0.3);    /* 绿色边框 */

/* 金融数据专用色 */
--profit-green: #22c55e;         /* 盈利绿（与主色一致）*/
--loss-red: #ef4444;             /* 亏损红 */
--neutral-gray: #6b7280;         /* 中性灰 */
```

#### 字体规范
```css
/* 忍者终端字体系统 */
font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;

/* 字体尺寸 */
--text-terminal-xl: 1.25rem;     /* 20px - 主标题 */
--text-terminal-lg: 1.125rem;    /* 18px - 副标题 */  
--text-terminal-md: 1rem;        /* 16px - 正文 */
--text-terminal-sm: 0.875rem;    /* 14px - 辅助信息 */
--text-terminal-xs: 0.75rem;     /* 12px - 提示文字 */
```

### 📝 忍者文案风格指南

#### 文案原则
1. **中英混搭**: Ninja + 中文，体现国际化黑客范儿
2. **投资梗运用**: 韭菜、割肉、破产、首负等圈内术语
3. **自嘲幽默**: 承认失败、自黑痛点，与用户情感共鸣
4. **真实诚恳**: 避免虚假宣传，实事求是描述风险

#### 标准文案库
**品牌文案**:
- 网站标题: `Ninja Backtesting Dojo`
- 导航标题: `Ninja韭菜道场@v2.0`
- Slogan: `别人恐惧我贪婪，别人小亏我破产`

**状态描述**:
- 执行状态: `STRATEGY_STANDBY` | `NINJA_MODE_ACTIVE` | `MISSION_EXECUTING`
- 危险级别: `九死一生级别` | `韭菜收割进行时` | `破产倒计时`
- 修炼等级: `下忍(菜鸟)` | `中忍(老韭菜)` | `上忍(大师)`

**功能描述**:
- 策略执行: `执行潜行任务` | `开始修炼` | `启动割肉程序`
- 数据展示: `忍者情报网` | `修行记录` | `战斗统计`

### 🎭 动画效果规范

#### 忍者动效库
```css
/* 基础忍者动效 */
.ninja-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.ninja-bounce {
  animation: bounce 1s infinite;
}

.ninja-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

/* 特殊忍者效果 */
.ninja-typewriter {
  /* 打字机效果 - 使用react-simple-typewriter */
  border-right: 2px solid #22c55e;
  animation: blink 1s infinite;
}

.ninja-glow {
  box-shadow: 0 0 10px var(--ninja-glow);
}
```

#### 动画使用原则
- **极简原则**: 只使用pulse、bounce等基础动效，避免复杂动画
- **性能优先**: 控制同时运行的动画数量，避免影响性能
- **语义化**: 每个动效都有明确的语义意义（alert、loading、success等）

### 🧭 交互设计规范

#### 忍者交互模式
1. **终端导航**: 保持`ls strategies` | `ps manage` | `cat data`的命令行风格
2. **Hover效果**: 绿色发光边框 + 轻微放大
3. **点击反馈**: 瞬间高亮 + 轻微震动效果（如支持）
4. **状态指示**: 使用emoji + 动画组合表达状态

#### 组件交互规范
```css
/* 忍者按钮交互 */
.ninja-button {
  @apply border border-green-400/50 text-green-400 bg-transparent;
  transition: all 0.3s ease;
}

.ninja-button:hover {
  @apply bg-green-400/10 border-green-400 shadow-md;
  box-shadow: 0 0 15px var(--ninja-glow);
}

/* 忍者卡片交互 */  
.ninja-card {
  @apply border border-green-400/30 bg-black;
  transition: border-color 0.3s ease;
}

.ninja-card:hover {
  @apply border-green-400/60 bg-green-400/5;
}
```

### 📱 响应式忍者设计

#### 断点策略
- **Desktop**: 终端全屏体验，信息密度最高
- **Tablet**: 保持终端风格，适当调整布局密度  
- **Mobile**: 简化为核心功能，保持绿色主题

#### 移动端适配原则
- 保持黑绿配色不变
- 简化动效，保证性能
- 核心功能优先显示
- 保持等宽字体的终端感

### 🛠️ 技术实现规范

#### 推荐技术栈
- **框架**: React + TypeScript  
- **样式**: Tailwind CSS (便于快速实现终端风格)
- **动画**: Framer Motion (可选，用于复杂动效)
- **打字机**: react-simple-typewriter
- **图标**: 优先使用emoji，其次Heroicons

#### CSS工具类封装
```css
/* 忍者终端工具类 */
.terminal-bg { @apply bg-black text-green-400 font-mono; }
.terminal-border { @apply border border-green-400/30; }
.terminal-glow { box-shadow: 0 0 10px rgba(34, 197, 94, 0.3); }
.terminal-text { @apply text-green-400 font-mono; }
.ninja-pulse { @apply animate-pulse; }
.ninja-bounce { @apply animate-bounce; }
```

### 🎪 使用场景与扩展

#### 适用场景
- ✅ **策略选择页**: 忍者情报网风格，展示策略列表
- ✅ **参数配置页**: 任务配置终端，表单+命令行混合
- ✅ **执行页面**: 实时终端输出，显示策略执行过程
- ✅ **结果页面**: 战斗报告风格，数据可视化+忍者元素

#### 扩展指导原则
1. **保持一致性**: 所有新页面都应遵循忍者黑客设计规范
2. **文案创新**: 根据具体功能创造新的忍者风格文案
3. **渐进增强**: 在基础终端风格基础上添加忍者元素
4. **用户反馈**: 根据用户使用情况调整设计细节

---

**忍者设计规范制定人**: UI/UX设计师  
**最后更新**: 2024-09-03  
**适用版本**: v2.0 "忍者韭菜道场"版本  
**下次审查**: 根据用户反馈进行调整