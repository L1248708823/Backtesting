import React, { ReactNode } from 'react'

interface TerminalShellProps {
  /** 终端标题 */
  title?: string
  /** 主机名 */
  hostname?: string
  /** 当前工作目录 */
  workingDir?: string
  /** 子内容 */
  children: ReactNode
  /** 终端窗口样式类名 */
  className?: string
}

/**
 * 终端外壳组件
 * 提供真正的CMD风格终端容器，但保持美观的视觉效果
 */
const TerminalShell: React.FC<TerminalShellProps> = ({
  title = "DCA Mission Terminal",
  hostname = "ninja",
  workingDir = "~/dca-mission",
  children,
  className = ""
}) => {
  return (
    <div className={`bg-black border-2 border-green-400/50 rounded-lg shadow-2xl shadow-green-400/20 ${className}`}>
      {/* 终端标题栏 - macOS风格但保持终端调性 */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-green-400/30 rounded-t-lg">
        {/* 左侧控制按钮 */}
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full opacity-60"></div>
          <div className="w-3 h-3 bg-yellow-500 rounded-full opacity-60"></div>
          <div className="w-3 h-3 bg-green-500 rounded-full opacity-60"></div>
        </div>
        
        {/* 终端标题 - 增加emoji */}
        <div className="text-green-400 font-mono text-sm">
          🥷 {title}
        </div>
        
        {/* 右侧占位 */}
        <div className="w-16"></div>
      </div>

      {/* 终端状态栏 - 显示当前会话信息 */}
      <div className="px-4 py-1 bg-gray-800 border-b border-green-400/20 text-xs font-mono">
        <span className="text-gray-400">📊 Session: </span>
        <span className="text-green-400">{hostname}@hackermain</span>
        <span className="text-gray-400 ml-4">📁 PWD: </span>
        <span className="text-cyan-400">{workingDir}</span>
        <span className="text-gray-400 ml-4">⚡ Status: </span>
        <span className="text-yellow-400 animate-pulse">MISSION_ACTIVE</span>
      </div>

      {/* 终端内容区域 */}
      <div className="p-6 bg-black rounded-b-lg min-h-[400px] font-mono">
        {children}
      </div>
    </div>
  )
}

export default TerminalShell