import React, { useEffect, useState } from 'react'
import './MatrixNinjaAnimation.css'

interface MatrixNinjaAnimationProps {
  /** 是否激活动画 */
  isActive: boolean
  /** 动画完成回调 */
  onComplete?: () => void
  /** 预期持续时间（毫秒）*/
  duration?: number
  /** 当前进度百分比 0-100，用于外部控制进度 */
  progress?: number
}

/**
 * 忍者道场Loading动画
 * - 01数字流背景（随机起始位置）
 * - 手里剑旋转动画
 * - 智能进度条（<3s用默认3s，>3s动态调整，90%后暂停）
 */
const MatrixNinjaAnimation: React.FC<MatrixNinjaAnimationProps> = ({
  isActive,
  onComplete,
  duration = 3000,
  progress
}) => {
  /** 内部进度状态，用于自动进度 */
  const [internalProgress, setInternalProgress] = useState(0)
  
  useEffect(() => {
    console.log(`useEffect triggered: isActive=${isActive}, progress=${progress}`)
    
    if (!isActive) {
      console.log('isActive is false, resetting progress and stopping timer')
      setInternalProgress(0)
      return
    }

    // 如果有外部progress，使用外部控制
    if (progress !== undefined) {
      console.log('External progress provided, skipping internal timer')
      return
    }
    
    // 智能进度条逻辑：
    // - 前3秒快速到75%
    // - 3秒后缓慢增加等待后端
    const fastDuration = 3000 // 前3秒
    const fastProgress = 75   // 快速到75%
    const slowIncrement = 0.5 // 3秒后每次增加0.5%
    
    const timer = setInterval(() => {
      setInternalProgress(prev => {
        const elapsedTime = Date.now() - startTime
        let newProgress
        
        if (elapsedTime <= fastDuration) {
          // 前3秒：快速增长到75%
          newProgress = (elapsedTime / fastDuration) * fastProgress
        } else {
          // 3秒后：缓慢增长，但不超过95%
          newProgress = Math.min(prev + slowIncrement, 95)
        }
        
        console.log(`Timer tick: elapsedTime=${elapsedTime}ms, progress=${newProgress.toFixed(1)}%`)
        
        return newProgress
      })
    }, 100)
    
    const startTime = Date.now()
    
    return () => {
      console.log('Timer cleanup - clearing interval')
      clearInterval(timer)
    }
  }, [isActive, duration])  // 移除progress依赖，避免重复执行
  
  // 组件卸载时的清理
  useEffect(() => {
    return () => {
      console.log('Component unmounting - MatrixNinjaAnimation')
    }
  }, [])
  
  // 添加完成进度的方法，供外部调用
  useEffect(() => {
    if (progress === 100) {
      console.log('Progress reached 100%, showing completion for 0.3s')
      // 显示100%状态0.3秒后触发完成
      const timer = setTimeout(() => {
        onComplete?.()
      }, 300)
      return () => clearTimeout(timer)
    }
  }, [progress, onComplete])
  
  // 使用外部progress或内部progress
  const currentProgress = progress ?? internalProgress
  
  console.log(`progress: ${progress}, internalProgress: ${internalProgress}, currentProgress: ${currentProgress}`)

  if (!isActive) return null

  return (
    <div className="ninja-loading-container">
      {/* 01数字流背景 */}
      <div className="digital-rain-bg">
        {Array.from({ length: 20 }, (_, i) => {
          const randomDelay = Math.random() * 5 // 0-5秒随机延迟
          const randomDuration = 4 + Math.random() * 3 // 4-7秒随机时长
          return (
            <div
              key={i}
              className="rain-column"
              style={{
                left: `${(i * 5)}%`,
                animationDelay: `${randomDelay}s`,
                animationDuration: `${randomDuration}s`
              }}
            >
              {Array.from({ length: 30 }, () => Math.random() > 0.5 ? '1' : '0').join('')}
            </div>
          )
        })}
      </div>

      {/* 前景加载内容 */}
      <div className="loading-foreground">
        {/* 旋转手里剑 */}
        <div className="shuriken-spinner">
          <svg className="shuriken-icon" viewBox="0 0 1024 1024">
            <path d="M920.507276 246.269336l-85.792398-0.451539a557.831202 557.831202 0 0 0-321.676338 100.151336l-267.852898-243.831026-0.451538 85.792398a557.831202 557.831202 0 0 0 100.151336 321.947262l-243.831026 267.852897 85.792398 0.451539a557.831202 557.831202 0 0 0 321.856954-100.151336l267.852897 243.831026 0.451539-85.792398A557.831202 557.831202 0 0 0 677.308405 514.122233z m-354.458065 316.077255a74.594232 74.594232 0 1 1-4.966929-105.29888 74.594232 74.594232 0 0 1 4.966929 105.118265z" fill="currentColor" />
          </svg>
        </div>
        
        {/* 终端状态文字 */}
        <div className="terminal-status">
          [ EXECUTING STRATEGY ]
        </div>
        
        {/* 进度条 */}
        <div className="progress-track">
          <div 
            className="progress-fill"
            style={{ 
              width: `${currentProgress}%`
            }}
          />
        </div>
      </div>
    </div>
  )
}

export default MatrixNinjaAnimation