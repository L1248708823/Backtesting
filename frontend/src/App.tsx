import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import AppHeader from '@/components/Layout/Header'
import AppSider from '@/components/Layout/Sider'
import StrategySelection from '@/pages/StrategySelection'
import ParameterConfig from '@/pages/ParameterConfig'
import BacktestExecution from '@/pages/BacktestExecution'
import ResultDisplay from '@/pages/ResultDisplay'
import StrategyManagement from '@/pages/StrategyManagement'
import DataManagement from '@/pages/DataManagement'

const { Content } = Layout

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <AppHeader />
        <Layout>
          <AppSider />
          <Layout style={{ padding: '24px' }}>
            <Content
              style={{
                background: '#fff',
                padding: 24,
                margin: 0,
                minHeight: 280,
                borderRadius: 8,
              }}
            >
              <Routes>
                <Route path="/" element={<StrategySelection />} />
                <Route path="/config/:strategyId" element={<ParameterConfig />} />
                <Route path="/backtest/:taskId" element={<BacktestExecution />} />
                <Route path="/result/:taskId" element={<ResultDisplay />} />
                <Route path="/strategies" element={<StrategyManagement />} />
                <Route path="/data" element={<DataManagement />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </Router>
  )
}

export default App