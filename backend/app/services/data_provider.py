# -*- coding: utf-8 -*-
"""
简化数据提供者 (Simplified Data Provider)

为定投策略专门优化的数据提供服务，具有以下特点：
1. 轻量级：去除复杂的数据处理，专注核心数据获取
2. 高效率：针对定投场景优化，支持长期数据缓存
3. 易维护：清晰的代码结构，便于扩展和维护
4. 容错性：优雅处理数据异常和网络问题

核心功能：
- ETF价格数据获取和缓存
- 多数据源支持（AKShare + yfinance）
- 数据质量检查和修复
- 智能缓存管理

设计原则：
- 数据源抽象：支持多数据源切换
- 缓存优先：减少重复网络请求
- 异常处理：优雅处理各种异常情况
- 性能优化：针对定投场景的数据获取模式
"""

import logging
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import asyncio
from pathlib import Path

# 尝试导入数据源依赖
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    logging.warning("AKShare 未安装，A股数据获取将不可用")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logging.warning("yfinance 未安装，美股数据获取将不可用")

# 配置日志
logger = logging.getLogger(__name__)


class DataProviderError(Exception):
    """数据提供者异常"""
    pass


class DataSource:
    """数据源接口抽象"""
    
    def fetch_price_data(self, symbol: str, start_date: date, end_date: date) -> Dict[date, Decimal]:
        """获取价格数据"""
        raise NotImplementedError


class AKShareDataSource(DataSource):
    """AKShare数据源 - 用于A股/港股数据"""
    
    def fetch_price_data(self, symbol: str, start_date: date, end_date: date) -> Dict[date, Decimal]:
        """
        获取A股ETF价格数据
        
        Args:
            symbol: 股票代码（如：510300）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict[date, Decimal]: 日期到收盘价的映射
        """
        if not AKSHARE_AVAILABLE:
            raise DataProviderError("AKShare 未安装，无法获取A股数据")
        
        try:
            logger.debug(f"通过AKShare获取{symbol}数据: {start_date} 到 {end_date}")
            
            # 使用akshare获取ETF数据
            # 注意：akshare的日期格式通常是字符串 'YYYYMMDD'
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            
            # 获取ETF历史数据
            df = ak.fund_etf_hist_em(symbol=symbol, period="daily", 
                                   start_date=start_str, end_date=end_str, adjust="qfq")
            
            if df is None or df.empty:
                logger.warning(f"未获取到{symbol}的数据")
                return {}
            
            # 转换数据格式
            price_data = {}
            for _, row in df.iterrows():
                try:
                    # AKShare返回的日期可能是多种格式，需要统一处理
                    date_str = str(row['日期'])
                    if len(date_str) == 8:  # YYYYMMDD格式
                        trade_date = datetime.strptime(date_str, '%Y%m%d').date()
                    else:  # YYYY-MM-DD格式
                        trade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    # 使用收盘价
                    close_price = Decimal(str(row['收盘']))
                    price_data[trade_date] = close_price
                    
                except Exception as e:
                    logger.warning(f"解析数据行时发生错误: {e}, 跳过该行")
                    continue
            
            logger.info(f"成功获取{symbol}数据 {len(price_data)}条记录")
            return price_data
            
        except Exception as e:
            error_msg = f"AKShare获取数据失败 {symbol}: {str(e)}"
            logger.error(error_msg)
            raise DataProviderError(error_msg)


class YFinanceDataSource(DataSource):
    """YFinance数据源 - 用于美股数据"""
    
    def fetch_price_data(self, symbol: str, start_date: date, end_date: date) -> Dict[date, Decimal]:
        """
        获取美股ETF价格数据
        
        Args:
            symbol: 股票代码（如：SPY）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict[date, Decimal]: 日期到收盘价的映射
        """
        if not YFINANCE_AVAILABLE:
            raise DataProviderError("yfinance 未安装，无法获取美股数据")
        
        try:
            logger.debug(f"通过yfinance获取{symbol}数据: {start_date} 到 {end_date}")
            
            # 创建ticker对象
            ticker = yf.Ticker(symbol)
            
            # 获取历史数据
            hist = ticker.history(start=start_date, end=end_date + timedelta(days=1))
            
            if hist is None or hist.empty:
                logger.warning(f"未获取到{symbol}的数据")
                return {}
            
            # 转换数据格式
            price_data = {}
            for date_index, row in hist.iterrows():
                try:
                    # yfinance返回的日期是pandas的Timestamp
                    trade_date = date_index.date()
                    
                    # 使用收盘价（调整后价格）
                    close_price = Decimal(str(row['Close']))
                    price_data[trade_date] = close_price
                    
                except Exception as e:
                    logger.warning(f"解析数据行时发生错误: {e}, 跳过该行")
                    continue
            
            logger.info(f"成功获取{symbol}数据 {len(price_data)}条记录")
            return price_data
            
        except Exception as e:
            error_msg = f"yfinance获取数据失败 {symbol}: {str(e)}"
            logger.error(error_msg)
            raise DataProviderError(error_msg)


class SimpleDataProvider:
    """
    简化数据提供者
    
    为定投策略专门设计的数据提供服务，支持多数据源和智能缓存。
    """
    
    def __init__(self, cache_db_path: str = "data_cache.db"):
        """
        初始化数据提供者
        
        Args:
            cache_db_path: 缓存数据库路径
        """
        self.cache_db_path = cache_db_path
        self.data_sources = self._initialize_data_sources()
        
        # 初始化缓存数据库
        self._initialize_cache_db()
        
        logger.info(f"SimpleDataProvider初始化完成，可用数据源: {list(self.data_sources.keys())}")
    
    def _initialize_data_sources(self) -> Dict[str, DataSource]:
        """初始化数据源"""
        sources = {}
        
        # A股数据源（AKShare）
        if AKSHARE_AVAILABLE:
            sources['akshare'] = AKShareDataSource()
            logger.info("AKShare数据源已启用")
        
        # 美股数据源（yfinance）
        if YFINANCE_AVAILABLE:
            sources['yfinance'] = YFinanceDataSource()
            logger.info("yfinance数据源已启用")
        
        if not sources:
            logger.warning("没有可用的数据源，请安装akshare或yfinance")
        
        return sources
    
    def _initialize_cache_db(self):
        """初始化缓存数据库"""
        try:
            # 确保目录存在
            cache_path = Path(self.cache_db_path)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建数据库表
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # 价格数据缓存表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_cache (
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    close_price TEXT NOT NULL,
                    data_source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (symbol, date)
                )
            ''')
            
            # 创建索引提高查询性能
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_symbol_date 
                ON price_cache (symbol, date)
            ''')
            
            conn.commit()
            conn.close()
            
            logger.debug("缓存数据库初始化完成")
            
        except Exception as e:
            error_msg = f"初始化缓存数据库失败: {str(e)}"
            logger.error(error_msg)
            raise DataProviderError(error_msg)
    
    def get_price_data(self, 
                      symbol: str, 
                      start_date: date, 
                      end_date: date,
                      force_refresh: bool = False) -> Dict[date, Decimal]:
        """
        获取价格数据（优先从缓存获取）
        
        Args:
            symbol: 标的代码
            start_date: 开始日期
            end_date: 结束日期
            force_refresh: 是否强制刷新（跳过缓存）
            
        Returns:
            Dict[date, Decimal]: 日期到价格的映射
        """
        try:
            # 1. 如果不强制刷新，先尝试从缓存获取
            if not force_refresh:
                cached_data = self._get_cached_data(symbol, start_date, end_date)
                if self._is_cache_complete(cached_data, start_date, end_date):
                    logger.debug(f"从缓存获取{symbol}数据成功")
                    return cached_data
            
            # 2. 缓存不完整或强制刷新，从网络获取
            network_data = self._fetch_from_network(symbol, start_date, end_date)
            
            # 3. 更新缓存
            if network_data:
                self._update_cache(symbol, network_data)
            
            # 4. 返回网络数据，如果网络失败则返回缓存数据
            if network_data:
                return network_data
            elif not force_refresh:
                logger.warning(f"网络获取失败，尝试返回缓存数据")
                return self._get_cached_data(symbol, start_date, end_date)
            else:
                raise DataProviderError(f"无法获取{symbol}的数据")
                
        except Exception as e:
            logger.error(f"获取价格数据失败: {str(e)}")
            # 最后的容错措施：返回缓存数据（如果有）
            try:
                cached_data = self._get_cached_data(symbol, start_date, end_date)
                if cached_data:
                    logger.info(f"使用缓存数据作为容错措施")
                    return cached_data
            except:
                pass
            
            raise DataProviderError(f"获取{symbol}数据失败: {str(e)}")
    
    def _get_cached_data(self, symbol: str, start_date: date, end_date: date) -> Dict[date, Decimal]:
        """从缓存获取数据"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, close_price 
                FROM price_cache 
                WHERE symbol = ? AND date BETWEEN ? AND ?
                ORDER BY date
            ''', (symbol, start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换数据格式
            price_data = {}
            for date_str, price_str in rows:
                trade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                price = Decimal(price_str)
                price_data[trade_date] = price
            
            return price_data
            
        except Exception as e:
            logger.error(f"从缓存获取数据失败: {str(e)}")
            return {}
    
    def _is_cache_complete(self, cached_data: Dict[date, Decimal], 
                          start_date: date, end_date: date) -> bool:
        """检查缓存数据是否完整"""
        if not cached_data:
            return False
        
        # 简化的完整性检查：检查是否有足够的数据点
        # 实际应该考虑交易日历，这里使用简化逻辑
        expected_days = (end_date - start_date).days + 1
        actual_days = len(cached_data)
        
        # 如果实际数据点数量大于期望天数的50%，认为缓存基本完整
        # （考虑到周末和节假日）
        completion_ratio = actual_days / expected_days
        is_complete = completion_ratio >= 0.5
        
        logger.debug(f"缓存完整性检查: {actual_days}/{expected_days} = {completion_ratio:.2f}, "
                    f"完整: {is_complete}")
        
        return is_complete
    
    def _fetch_from_network(self, symbol: str, start_date: date, end_date: date) -> Dict[date, Decimal]:
        """从网络获取数据"""
        # 根据symbol判断使用哪个数据源
        data_source = self._select_data_source(symbol)
        if not data_source:
            raise DataProviderError(f"没有合适的数据源获取{symbol}数据")
        
        logger.info(f"从网络获取{symbol}数据，使用数据源: {data_source}")
        
        try:
            source_instance = self.data_sources[data_source]
            return source_instance.fetch_price_data(symbol, start_date, end_date)
        except Exception as e:
            logger.error(f"网络获取数据失败: {str(e)}")
            raise
    
    def _select_data_source(self, symbol: str) -> Optional[str]:
        """根据标的代码选择合适的数据源"""
        # 简化的数据源选择逻辑
        if symbol.isdigit() and len(symbol) == 6:
            # A股代码通常是6位数字
            if 'akshare' in self.data_sources:
                return 'akshare'
        else:
            # 其他情况（美股等）使用yfinance
            if 'yfinance' in self.data_sources:
                return 'yfinance'
        
        # 如果没有匹配的数据源，返回第一个可用的
        if self.data_sources:
            return next(iter(self.data_sources.keys()))
        
        return None
    
    def _update_cache(self, symbol: str, price_data: Dict[date, Decimal]):
        """更新缓存数据"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # 获取数据源信息
            data_source = self._select_data_source(symbol)
            created_at = datetime.now().isoformat()
            
            # 批量插入或更新数据（使用REPLACE避免重复）
            for trade_date, price in price_data.items():
                cursor.execute('''
                    REPLACE INTO price_cache 
                    (symbol, date, close_price, data_source, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (symbol, trade_date.isoformat(), str(price), data_source, created_at))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"缓存更新成功: {symbol}, {len(price_data)}条记录")
            
        except Exception as e:
            logger.error(f"更新缓存失败: {str(e)}")
    
    def get_latest_price(self, symbol: str) -> Optional[Tuple[date, Decimal]]:
        """获取最新价格"""
        try:
            # 从缓存获取最新价格
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, close_price 
                FROM price_cache 
                WHERE symbol = ?
                ORDER BY date DESC
                LIMIT 1
            ''', (symbol,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                trade_date = datetime.strptime(row[0], '%Y-%m-%d').date()
                price = Decimal(row[1])
                return (trade_date, price)
            
            return None
            
        except Exception as e:
            logger.error(f"获取最新价格失败: {str(e)}")
            return None
    
    def clear_cache(self, symbol: Optional[str] = None):
        """清空缓存（可指定标的）"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute('DELETE FROM price_cache WHERE symbol = ?', (symbol,))
                logger.info(f"清空{symbol}的缓存数据")
            else:
                cursor.execute('DELETE FROM price_cache')
                logger.info("清空所有缓存数据")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # 统计缓存记录数
            cursor.execute('SELECT COUNT(*) FROM price_cache')
            total_records = cursor.fetchone()[0]
            
            # 统计标的数量
            cursor.execute('SELECT COUNT(DISTINCT symbol) FROM price_cache')
            symbol_count = cursor.fetchone()[0]
            
            # 统计各数据源记录数
            cursor.execute('''
                SELECT data_source, COUNT(*) 
                FROM price_cache 
                GROUP BY data_source
            ''')
            source_stats = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_records': total_records,
                'symbol_count': symbol_count,
                'source_stats': source_stats
            }
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {str(e)}")
            return {}
    
    def validate_symbol(self, symbol: str) -> bool:
        """验证标的代码是否有效"""
        try:
            # 尝试获取最近3天的数据来验证标的
            end_date = date.today()
            start_date = end_date - timedelta(days=3)
            
            data = self.get_price_data(symbol, start_date, end_date)
            return len(data) > 0
            
        except Exception as e:
            logger.debug(f"验证标的{symbol}失败: {str(e)}")
            return False
    
    def get_available_symbols(self) -> List[str]:
        """获取缓存中可用的标的列表"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT DISTINCT symbol FROM price_cache ORDER BY symbol')
            symbols = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return symbols
            
        except Exception as e:
            logger.error(f"获取可用标的列表失败: {str(e)}")
            return []
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"SimpleDataProvider(数据源: {list(self.data_sources.keys())})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        stats = self.get_cache_stats()
        return (f"SimpleDataProvider(data_sources={list(self.data_sources.keys())}, "
                f"cached_symbols={stats.get('symbol_count', 0)}, "
                f"cached_records={stats.get('total_records', 0)})")


def create_data_provider(cache_db_path: str = "data/cache.db") -> SimpleDataProvider:
    """工厂函数：创建数据提供者实例"""
    return SimpleDataProvider(cache_db_path)


# 异步版本的数据获取（可选，为未来扩展预留）
class AsyncSimpleDataProvider(SimpleDataProvider):
    """异步版本的简化数据提供者"""
    
    async def get_price_data_async(self, 
                                  symbol: str, 
                                  start_date: date, 
                                  end_date: date,
                                  force_refresh: bool = False) -> Dict[date, Decimal]:
        """异步获取价格数据"""
        # 在单独的线程中执行同步操作
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.get_price_data, 
            symbol, 
            start_date, 
            end_date, 
            force_refresh
        )