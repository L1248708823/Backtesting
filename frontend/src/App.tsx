import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useLocation } from 'react-router-dom'
import StrategySelection from '@/pages/StrategySelection'
import ParameterConfig from '@/pages/ParameterConfig'
import BacktestExecution from '@/pages/BacktestExecution'
import ResultDisplay from '@/pages/ResultDisplay'
import StrategyManagement from '@/pages/StrategyManagement'
import DataManagement from '@/pages/DataManagement'
import DCAConfig from '@/pages/DCAConfig'
import DCAResult from '@/pages/DCAResult'

function ModernNavbar() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: '策略', icon: '🚀' },
    { path: '/strategies', label: '管理', icon: '📊' },
    { path: '/data', label: '数据', icon: '💾' }
  ]

  return (
    <nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-gray-900/80 backdrop-blur-lg border border-gray-700/50 rounded-2xl px-6 py-3">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2 text-blue-400 font-semibold">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
          量化回测 v2.0
        </div>
        
        <div className="flex items-center gap-1">
          {navItems.map((item) => (
            <a
              key={item.path}
              href={item.path}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-300 ${
                location.pathname === item.path 
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
                  : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
              }`}
            >
              <span>{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </a>
          ))}
        </div>
      </div>
    </nav>
  )
}

function AppContent() {
  return (
    <div className="min-h-screen bg-gray-950">
      <ModernNavbar />
      
      <main>
        <Routes>
          <Route path="/" element={<StrategySelection />} />
          <Route path="/config/:strategyId" element={<ParameterConfig />} />
          <Route path="/backtest/:taskId" element={<BacktestExecution />} />
          <Route path="/result/:taskId" element={<ResultDisplay />} />
          <Route path="/strategies" element={<StrategyManagement />} />
          <Route path="/data" element={<DataManagement />} />
          <Route path="/dca/config" element={<DCAConfig />} />
          <Route path="/dca/result/:taskId" element={<DCAResult />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App