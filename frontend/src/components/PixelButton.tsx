import React, { ReactNode } from 'react'

interface PixelButtonProps {
  /** 按钮文本或内容 */
  children: ReactNode
  /** 点击事件 */
  onClick?: () => void
  /** 按钮变体样式 */
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
  /** 按钮尺寸 */
  size?: 'small' | 'medium' | 'large'
  /** 是否禁用 */
  disabled?: boolean
  /** 自定义样式类名 */
  className?: string
}

/**
 * 像素风按钮组件
 * 终端风格的简洁文字按钮，符合hacker美学
 */
const PixelButton: React.FC<PixelButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  className = ""
}) => {
  // 按钮变体样式映射
  const variantStyles = {
    primary: 'bg-black border-green-400 text-green-400 hover:bg-green-400/10 hover:shadow-green-400/50',
    secondary: 'bg-black border-gray-500 text-gray-400 hover:bg-gray-500/10 hover:text-gray-300 hover:shadow-gray-500/30',
    success: 'bg-black border-cyan-400 text-cyan-400 hover:bg-cyan-400/10 hover:shadow-cyan-400/50',
    warning: 'bg-black border-yellow-400 text-yellow-400 hover:bg-yellow-400/10 hover:shadow-yellow-400/50',
    danger: 'bg-black border-red-400 text-red-400 hover:bg-red-400/10 hover:shadow-red-400/50'
  }

  // 按钮尺寸样式映射
  const sizeStyles = {
    small: 'px-3 py-1 text-xs min-w-[60px]',
    medium: 'px-4 py-2 text-sm min-w-[80px]',
    large: 'px-6 py-3 text-base min-w-[120px]'
  }

  // 禁用状态样式
  const disabledStyles = 'opacity-50 cursor-not-allowed hover:bg-black hover:shadow-none'

  return (
    <button
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
      className={`
        inline-flex items-center justify-center
        font-mono font-bold
        border-2 rounded-sm
        transition-all duration-200
        hover:shadow-lg
        active:transform active:scale-95
        select-none
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${disabled ? disabledStyles : 'cursor-pointer'}
        ${className}
      `}
    >
      {/* 按钮内容前缀 - 终端风格的命令提示符 */}
      <span className="mr-1">&gt;</span>
      {children}
    </button>
  )
}

export default PixelButton