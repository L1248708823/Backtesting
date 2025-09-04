import React, { useState, useEffect } from 'react'

interface StreamLine {
  /** 行ID */
  id: string
  /** 行内容 */
  content: string
  /** 行类型 - 影响颜色 */
  type?: 'info' | 'success' | 'warning' | 'error' | 'command'
  /** 延迟显示时间（毫秒） */
  delay?: number
}

interface StreamOutputProps {
  /** 要流式输出的行数据 */
  lines: StreamLine[]
  /** 每行输出间隔（毫秒） */
  lineInterval?: number
  /** 每个字符打字间隔（毫秒，0表示整行显示） */
  typeInterval?: number
  /** 是否立即显示所有内容 */
  immediate?: boolean
  /** 输出完成回调 */
  onComplete?: () => void
  /** 自定义样式类名 */
  className?: string
}

/**
 * 终端流式输出组件
 * 模拟终端逐行输出文本的效果，支持不同类型的着色
 */
const StreamOutput: React.FC<StreamOutputProps> = ({
  lines,
  lineInterval = 200, // 加速到200ms，去掉便秘体验
  typeInterval = 0, // 默认整行显示，不逐字打字
  immediate = false,
  onComplete,
  className = ""
}) => {
  const [visibleLines, setVisibleLines] = useState<StreamLine[]>([])
  const [isCompleted, setIsCompleted] = useState(false)

  useEffect(() => {
    // 重置状态
    setVisibleLines([])
    setIsCompleted(false)
    
    if (immediate) {
      setVisibleLines(lines)
      setIsCompleted(true)
      onComplete?.()
      return
    }

    let currentIndex = 0
    const timers: NodeJS.Timeout[] = []

    const showNextLine = () => {
      if (currentIndex < lines.length) {
        const currentLine = lines[currentIndex]
        const delay = currentLine.delay || lineInterval
        
        const timer = setTimeout(() => {
          setVisibleLines(prev => [...prev, currentLine])
          currentIndex++
          
          if (currentIndex >= lines.length) {
            setIsCompleted(true)
            onComplete?.()
          } else {
            showNextLine()
          }
        }, delay)
        
        timers.push(timer)
      }
    }

    showNextLine()

    return () => {
      timers.forEach(timer => clearTimeout(timer))
    }
  }, [lines, lineInterval, immediate]) // 移除onComplete避免无限循环

  // 获取行的样式类名
  const getLineStyle = (type: StreamLine['type'] = 'info') => {
    const baseStyle = 'font-mono text-sm leading-relaxed'
    
    switch (type) {
      case 'command':
        return `${baseStyle} text-green-400`
      case 'success':
        return `${baseStyle} text-cyan-400`
      case 'warning':
        return `${baseStyle} text-yellow-400`
      case 'error':
        return `${baseStyle} text-red-400`
      case 'info':
      default:
        return `${baseStyle} text-gray-300`
    }
  }

  return (
    <div className={`space-y-1 ${className}`}>
      {visibleLines.map((line, index) => (
        <div
          key={line.id}
          className={`${getLineStyle(line.type)} ${
            index === visibleLines.length - 1 && !isCompleted ? 'animate-pulse' : ''
          }`}
        >
          {/* 根据行类型添加前缀 */}
          {line.type === 'command' && <span className="text-green-400 mr-2">&gt;</span>}
          {line.type === 'success' && <span className="text-cyan-400 mr-2">✓</span>}
          {line.type === 'warning' && <span className="text-yellow-400 mr-2">!</span>}
          {line.type === 'error' && <span className="text-red-400 mr-2">✗</span>}
          
          {line.content}
        </div>
      ))}
      
      {/* 光标效果 - 只在未完成时显示 */}
      {!isCompleted && visibleLines.length > 0 && (
        <div className="inline-block w-2 h-4 bg-green-400 animate-pulse ml-1"></div>
      )}
    </div>
  )
}

export default StreamOutput