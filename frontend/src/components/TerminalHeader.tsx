import React from 'react'

interface TerminalHeaderProps {
  /** 终端标题 - 显示在窗口按钮右侧的标题文本 */
  title: string
  /** 版本号 - 显示的版本信息，可选 */
  version?: string
  /** 命令行用户名 - 终端提示符显示的用户名，默认为ninja */
  username?: string
  /** 命令行主机名 - 终端提示符显示的主机名 */
  hostname: string
  /** 任务描述 - 显示在命令行提示符下的任务描述 */
  taskDescription: string
  /** 额外CSS类名 */
  className?: string
}

/**
 * 忍者终端头部组件
 * 统一的终端窗口风格头部，包含窗口控制按钮、标题、命令行提示符
 */
const TerminalHeader: React.FC<TerminalHeaderProps> = ({
  title,
  version = 'v1.0',
  username = 'ninja',
  hostname,
  taskDescription,
  className = ''
}) => {
  return (
    <div className={`mb-8 ${className}`}>
      {/* 终端窗口头部 */}
      <div className="flex items-center gap-4 mb-4">
        {/* macOS风格窗口控制按钮 */}
        <div className="flex gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full" title="关闭"></div>
          <div className="w-3 h-3 bg-yellow-500 rounded-full" title="最小化"></div>
          <div className="w-3 h-3 bg-green-500 rounded-full" title="全屏"></div>
        </div>
        
        {/* 终端标题和版本 */}
        <span className="text-gray-500 font-mono">
          {title} {version}
        </span>
      </div>
      
      {/* 命令行提示符区域 */}
      <div className="border-l-4 border-green-400 pl-4 py-2 bg-green-400/5 mb-6">
        {/* 命令行提示符 */}
        <div className="text-gray-400 text-sm mb-1 font-mono">
          {username}@{hostname}:~$
        </div>
        
        {/* 任务描述 */}
        <div className="text-xl font-mono text-green-400">
          {taskDescription}
        </div>
      </div>
    </div>
  )
}

export default TerminalHeader