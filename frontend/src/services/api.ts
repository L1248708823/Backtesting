import axios from 'axios'
import { API_BASE_URL } from '@/utils/constants'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 增强错误处理
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    
    // 统一错误处理
    let errorMessage = '网络请求失败'
    
    if (error.response) {
      // 后端响应错误 (4xx, 5xx)
      const status = error.response.status
      const data = error.response.data
      
      switch (status) {
        case 400:
          errorMessage = `参数错误: ${data?.detail || '请检查输入参数'}`
          break
        case 404:
          errorMessage = `资源不存在: ${data?.detail || '请求的资源未找到'}`
          break
        case 500:
          errorMessage = `服务器错误: ${data?.detail || '服务器内部错误，请稍后重试'}`
          break
        default:
          errorMessage = data?.detail || `HTTP ${status}: 未知错误`
      }
    } else if (error.request) {
      // 网络连接错误
      errorMessage = '无法连接到服务器，请检查网络连接或后端服务状态'
    } else {
      // 请求配置错误
      errorMessage = `请求配置错误: ${error.message}`
    }
    
    // 创建增强的错误对象
    const enhancedError = new Error(errorMessage)
    enhancedError.name = 'APIError'
    // @ts-ignore - 添加额外属性
    enhancedError.status = error.response?.status
    // @ts-ignore
    enhancedError.response = error.response
    // @ts-ignore  
    enhancedError.originalError = error
    
    return Promise.reject(enhancedError)
  }
)

export default api