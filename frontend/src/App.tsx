import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useLocation } from 'react-router-dom'
import StrategySelection from '@/pages/StrategySelection'
import ParameterConfig from '@/pages/ParameterConfig'
import BacktestExecution from '@/pages/BacktestExecution'
import ResultDisplay from '@/pages/ResultDisplay'
import StrategyManagement from '@/pages/StrategyManagement'
import DataManagement from '@/pages/DataManagement'
import { DCAConfig, DCAResult } from '@/pages/DCA'
import DCATerminalConfig from '@/pages/DCA/DCATerminalConfig'

function ModernNavbar() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'strategies', icon: '$', cmd: 'ls' },
    { path: '/strategies', label: 'manage', icon: '#', cmd: 'ps' },
    { path: '/data', label: 'data', icon: '*', cmd: 'cat' }
  ]

  return (
    <nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-black/90 backdrop-blur-lg border-2 border-green-500/30 rounded-md px-6 py-3 shadow-lg shadow-green-500/20">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2 text-green-400 font-mono font-bold">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="tracking-wider">韭菜道场@v1.0</span>
        </div>
        
        <div className="flex items-center gap-1">
          {navItems.map((item) => (
            <a
              key={item.path}
              href={item.path}
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-mono transition-all duration-300 ${
                location.pathname === item.path 
                  ? 'bg-green-500/20 text-green-400 border border-green-500/50' 
                  : 'text-gray-400 hover:text-green-300 hover:bg-gray-800/50 border border-transparent hover:border-green-500/20'
              }`}
            >
              <span className="font-bold">{item.icon}</span>
              <span className="font-medium tracking-wide">{item.cmd} {item.label}</span>
            </a>
          ))}
        </div>
      </div>
    </nav>
  )
}

function AppContent() {
  return (
    <div className="min-h-screen bg-gray-950 pt-22">
      <ModernNavbar />
      
      <main>
        <Routes>
          <Route path="/" element={<StrategySelection />} />
          <Route path="/config/:strategyId" element={<ParameterConfig />} />
          <Route path="/backtest/:taskId" element={<BacktestExecution />} />
          <Route path="/result/:taskId" element={<ResultDisplay />} />
          <Route path="/strategies" element={<StrategyManagement />} />
          <Route path="/data" element={<DataManagement />} />
          
          {/* DCA路由 */}
          <Route path="/dca/config" element={<DCATerminalConfig />} />
          <Route path="/dca/result/:taskId" element={<DCAResult />} />
          <Route path="/dca/result" element={<DCAResult />} />
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