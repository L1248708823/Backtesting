"""
数据源管理器
统一管理AKShare、yfinance等数据源的数据获取
"""
import pandas as pd
from datetime import datetime
from typing import Optional
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class DataSource(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def get_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票/ETF数据，返回标准格式的OHLCV DataFrame"""
        pass

class AKShareDataSource(DataSource):
    """AKShare数据源 - A股和A股ETF"""
    
    def __init__(self):
        self.name = "AKShare"
        self._ak = None
    
    def _ensure_akshare(self):
        """延迟导入AKShare"""
        if self._ak is None:
            try:
                import akshare as ak
                self._ak = ak
                logger.info(f"AKShare loaded, version: {ak.__version__}")
            except ImportError:
                raise ImportError("AKShare not installed")
        return self._ak
    
    def get_data(self, symbol: str, start_date: str, end_date: str, is_etf: bool = None) -> pd.DataFrame:
        """获取A股/ETF数据
        
        Args:
            symbol: 股票代码，如 "510300", "000001"
            start_date: 开始日期 "2024-01-01" 
            end_date: 结束日期 "2024-12-01"
            is_etf: 是否为ETF，None时自动判断(5开头为ETF)
        
        Returns:
            标准OHLCV DataFrame，index为Date
        """
        ak = self._ensure_akshare()
        
        # 转换日期格式 (AKShare需要 "20240101" 格式)
        start_ak = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        end_ak = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')
        
        # 自动判断是否为ETF (5开头通常是ETF)
        if is_etf is None:
            is_etf = symbol.startswith('5')
        
        try:
            if is_etf:
                # 使用ETF专用接口
                df = ak.fund_etf_hist_em(
                    symbol=symbol,
                    period="daily",
                    start_date=start_ak,
                    end_date=end_ak,
                    adjust="qfq"
                )
            else:
                # 使用股票接口
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily", 
                    start_date=start_ak,
                    end_date=end_ak,
                    adjust="qfq"
                )
            
            if df.empty:
                logger.warning(f"No data for {symbol}")
                return pd.DataFrame()
            
            # 标准化列名 (两个接口的列名略有不同)
            if is_etf:
                # ETF接口列名
                df = df.rename(columns={
                    '日期': 'Date',
                    '开盘': 'Open',
                    '最高': 'High', 
                    '最低': 'Low',
                    '收盘': 'Close',
                    '成交量': 'Volume'
                })
            else:
                # 股票接口列名
                df = df.rename(columns={
                    '日期': 'Date',
                    '开盘': 'Open',
                    '最高': 'High', 
                    '最低': 'Low',
                    '收盘': 'Close',
                    '成交量': 'Volume'
                })
            
            # 设置Date为index
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            # 只保留OHLCV
            columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df[[col for col in columns if col in df.columns]]
            
            logger.info(f"Got {len(df)} records for {symbol} ({'ETF' if is_etf else 'Stock'})")
            return df
            
        except Exception as e:
            logger.error(f"AKShare error for {symbol}: {e}")
            return pd.DataFrame()

class YFinanceDataSource(DataSource):
    """yfinance数据源 - 美股和美股ETF"""
    
    def __init__(self):
        self.name = "yfinance"
        self._yf = None
    
    def _ensure_yfinance(self):
        """延迟导入yfinance"""
        if self._yf is None:
            try:
                import yfinance as yf
                self._yf = yf
                logger.info("yfinance loaded")
            except ImportError:
                raise ImportError("yfinance not installed")
        return self._yf
    
    def get_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取美股/ETF数据
        
        Args:
            symbol: 股票代码，如 "SPY"
            start_date: 开始日期 "2024-01-01"
            end_date: 结束日期 "2024-12-01"
        
        Returns:
            标准OHLCV DataFrame，index为Date
        """
        yf = self._ensure_yfinance()
        
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                logger.warning(f"No data for {symbol}")
                return pd.DataFrame()
            
            # yfinance已经是标准列名，只保留需要的
            columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df[[col for col in columns if col in df.columns]]
            
            logger.info(f"Got {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"yfinance error for {symbol}: {e}")
            return pd.DataFrame()

class DataManager:
    """数据管理器 - 自动选择数据源"""
    
    def __init__(self):
        self.akshare = AKShareDataSource()
        self.yfinance = YFinanceDataSource()
    
    def get_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """统一获取数据接口
        
        自动根据symbol选择数据源:
        - 纯数字(510300) -> AKShare  
        - 字母(SPY) -> yfinance
        """
        if symbol.isdigit():
            # A股/ETF
            return self.akshare.get_data(symbol, start_date, end_date)
        else:
            # 美股/ETF  
            return self.yfinance.get_data(symbol, start_date, end_date)

# 全局实例
data_manager = DataManager()