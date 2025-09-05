# -*- coding: utf-8 -*-
"""
市场数据API接口
基于新浪财经API提供实时市场指数、热门ETF等数据
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import asyncio

from ..core.sina_api import sina_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/market", tags=["market"])


class MarketDataService:
    """市场数据服务 - 基于新浪财经API"""
    
    def __init__(self):
        self._cache = {}
        self._cache_expiry = {}
        self._cache_duration = 30  # 缓存30秒
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._cache_expiry:
            return False
        return datetime.now() < self._cache_expiry[key]
    
    def _set_cache(self, key: str, data: Any) -> None:
        """设置缓存"""
        self._cache[key] = data
        self._cache_expiry[key] = datetime.now() + timedelta(seconds=self._cache_duration)
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if self._is_cache_valid(key):
            return self._cache[key]
        return None

    async def get_shanghai_index(self) -> Dict[str, Any]:
        """获取上证指数实时数据"""
        cache_key = "shanghai_index"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
            
        try:
            # 使用新浪API获取上证指数数据
            stock_data = sina_api.get_index_data('上证指数')
            
            if stock_data is None:
                raise ValueError("上证指数数据为空")
            
            result = {
                "value": stock_data.current_price,
                "change_pct": stock_data.change_percent,
                "change_amount": stock_data.change_amount,
                "timestamp": datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, result)
            logger.info(f"获取上证指数成功: {result['value']} ({result['change_pct']:+.2f}%)")
            return result
            
        except Exception as e:
            logger.error(f"获取上证指数失败: {e}")
            return {
                "value": None,
                "change_pct": None,
                "change_amount": None,
                "error": "数据获取中...",
                "timestamp": datetime.now().isoformat()
            }

    async def get_nasdaq_index(self) -> Dict[str, Any]:
        """获取纳指实时数据"""
        cache_key = "nasdaq_index"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
            
        try:
            # 使用新浪API获取纳指数据
            stock_data = sina_api.get_index_data('纳斯达克')
            
            if stock_data is None:
                raise ValueError("纳指数据为空")
            
            result = {
                "value": stock_data.current_price,
                "change_pct": stock_data.change_percent,
                "change_amount": stock_data.change_amount,
                "timestamp": datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, result)
            logger.info(f"获取纳指成功: {result['value']:.2f} ({result['change_pct']:+.2f}%)")
            return result
            
        except Exception as e:
            logger.error(f"获取纳指失败: {e}")
            return {
                "value": None,
                "change_pct": None,
                "change_amount": None,
                "error": "数据获取中...",
                "timestamp": datetime.now().isoformat()
            }

    async def get_vix_level(self) -> Dict[str, Any]:
        """获取VIX恐慌指数并判断危险等级"""
        cache_key = "vix_level"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
            
        try:
            # 基于上证指数涨跌幅计算市场恐慌程度
            shanghai_data = await self.get_shanghai_index()
            
            if shanghai_data.get('change_pct') is None:
                raise ValueError("无法获取上证指数数据")
            
            # 基于上证指数波动计算恐慌指数
            change_pct = abs(shanghai_data['change_pct'])
            
            # 简化的恐慌指数计算
            if change_pct <= 0.5:
                vix_value = 18.5  # 低波动
                level = "稳如老狗级别"
                color = "green"
            elif change_pct <= 1.5:
                vix_value = 22.0  # 中等波动
                level = "刀口舔血级别"
                color = "yellow"
            elif change_pct <= 3.0:
                vix_value = 28.5  # 高波动
                level = "九死一生级别"
                color = "red"
            else:
                vix_value = 35.0  # 极高波动
                level = "血流成河级别"
                color = "red"
            
            result = {
                "value": vix_value,
                "level": level,
                "color": color,
                "timestamp": datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, result)
            logger.info(f"计算恐慌指数成功: {vix_value:.1f} - {level} (基于上证涨跌{change_pct:.1f}%)")
            return result
            
        except Exception as e:
            logger.error(f"获取VIX失败: {e}")
            return {
                "value": None,
                "level": "数据获取中...",
                "color": "gray",
                "error": "数据获取中...",
                "timestamp": datetime.now().isoformat()
            }

    async def get_hot_etfs(self) -> List[str]:
        """获取热门ETF数据"""
        cache_key = "hot_etfs"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
            
        try:
            # 使用新浪API获取热门ETF数据
            hot_etfs = sina_api.get_hot_etfs(count=5)
            
            if not hot_etfs:
                raise ValueError("未找到ETF数据")
            
            result = []
            for etf in hot_etfs:
                # 格式化显示
                if etf.change_percent > 0:
                    result.append(f"{etf.name} +{etf.change_percent:.1f}%")
                elif etf.change_percent < 0:
                    result.append(f"{etf.name} {etf.change_percent:.1f}%")
                else:
                    result.append(f"{etf.name} 0.0%")
            
            # 只取前3个避免显示过多
            result = result[:3]
            
            self._set_cache(cache_key, result)
            logger.info(f"获取热门ETF成功: {result}")
            return result
            
        except Exception as e:
            logger.error(f"获取热门ETF失败: {e}")
            return ["数据获取中...", "数据获取中...", "数据获取中..."]


# 全局服务实例
market_service = MarketDataService()


@router.get("/dashboard")
async def get_market_dashboard():
    """
    获取市场仪表盘数据
    
    返回上证指数、纳指、VIX恐慌指数、热门ETF等实时数据
    """
    try:
        # 并行获取所有数据以提高性能
        shanghai_task = market_service.get_shanghai_index()
        nasdaq_task = market_service.get_nasdaq_index()
        vix_task = market_service.get_vix_level()
        etf_task = market_service.get_hot_etfs()
        
        # 等待所有任务完成
        shanghai_data, nasdaq_data, vix_data, etf_data = await asyncio.gather(
            shanghai_task, nasdaq_task, vix_task, etf_task,
            return_exceptions=True  # 即使某个失败也继续
        )
        
        # 处理可能的异常
        if isinstance(shanghai_data, Exception):
            logger.error(f"上证指数获取异常: {shanghai_data}")
            shanghai_data = {"value": None, "change_pct": None, "error": "数据获取中..."}
            
        if isinstance(nasdaq_data, Exception):
            logger.error(f"纳指获取异常: {nasdaq_data}")
            nasdaq_data = {"value": None, "change_pct": None, "error": "数据获取中..."}
            
        if isinstance(vix_data, Exception):
            logger.error(f"VIX获取异常: {vix_data}")
            vix_data = {"value": None, "level": "数据获取中...", "color": "gray"}
            
        if isinstance(etf_data, Exception):
            logger.error(f"ETF获取异常: {etf_data}")
            etf_data = ["数据获取中...", "数据获取中...", "数据获取中..."]
        
        response = {
            "shanghai_index": shanghai_data,
            "nasdaq_index": nasdaq_data,
            "vix_level": vix_data,
            "hot_etfs": etf_data,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"市场仪表盘获取失败: {e}")
        raise HTTPException(status_code=500, detail="市场数据获取失败")


@router.get("/test")
async def test_market_data():
    """测试市场数据获取"""
    return {
        "message": "市场数据API测试",
        "shanghai": await market_service.get_shanghai_index(),
        "nasdaq": await market_service.get_nasdaq_index(),
        "vix": await market_service.get_vix_level(),
        "etfs": await market_service.get_hot_etfs()
    }