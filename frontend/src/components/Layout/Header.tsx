import React from 'react'
import { Layout, Typography, Space, Button } from 'antd'
import { GithubOutlined, ApiOutlined } from '@ant-design/icons'
import { APP_CONFIG } from '@/utils/constants'

const { Header } = Layout
const { Title } = Typography

const AppHeader: React.FC = () => {
  return (
    <Header 
      style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        background: '#001529',
        padding: '0 24px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <ApiOutlined style={{ fontSize: '24px', color: '#1890ff', marginRight: '12px' }} />
        <Title level={3} style={{ color: '#fff', margin: 0 }}>
          {APP_CONFIG.title}
        </Title>
      </div>
      
      <Space>
        <Button 
          type="text" 
          icon={<GithubOutlined />}
          style={{ color: '#fff' }}
          href="https://github.com"
          target="_blank"
        >
          GitHub
        </Button>
      </Space>
    </Header>
  )
}

export default AppHeader