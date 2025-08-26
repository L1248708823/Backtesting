import React from 'react'
import { Layout, Menu } from 'antd'
import { useLocation, useNavigate } from 'react-router-dom'
import { 
  HomeOutlined, 
  SettingOutlined, 
  DatabaseOutlined,
  HistoryOutlined 
} from '@ant-design/icons'

const { Sider } = Layout

const AppSider: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '策略选择'
    },
    {
      key: '/strategies',
      icon: <SettingOutlined />,
      label: '策略管理'
    },
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: '历史记录'
    },
    {
      key: '/data',
      icon: <DatabaseOutlined />,
      label: '数据管理'
    }
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  return (
    <Sider width={200} style={{ background: '#fff' }}>
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        style={{ height: '100%', borderRight: 0 }}
        items={menuItems}
        onClick={handleMenuClick}
      />
    </Sider>
  )
}

export default AppSider