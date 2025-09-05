# -*- coding: utf-8 -*-
"""
新浪财经API客户端
基于LeekHub/leek-fund项目的数据获取方案
提供稳定的股票、指数实时数据
"""

import requests
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StockData:
    """股票数据结构"""
    code: str           # 股票代码
    name: str           # 股票名称
    current_price: float    # 当前价格
    open_price: float       # 开盘价
    close_price: float      # 昨收价
    high_price: float       # 最高价
    low_price: float        # 最低价
    volume: int             # 成交量
    amount: float           # 成交额
    change_amount: float    # 涨跌额
    change_percent: float   # 涨跌幅(%)
    date: str              # 日期
    time: str              # 时间
    raw_data: str          # 原始数据


class SinaFinanceAPI:
    """新浪财经API客户端"""
    
    BASE_URL = "https://hq.sinajs.cn/list="
    HEADERS = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 常用股票代码映射
    STOCK_CODES = {
        # A股指数
        '上证指数': 'sh000001',
        '深证成指': 'sz399001', 
        '沪深300': 'sh000300',
        '创业板指': 'sz399006',
        
        # 美股指数
        '道琼斯': 'usr_dji',
        '纳斯达克': 'usr_ixic',
        '标普500': 'usr_inx',
        
        # 港股指数
        '恒生指数': 'hsi_hsi',
        
        # 热门港股
        '腾讯控股': 'hk00700',
        '阿里巴巴': 'hk09988',
        '美团': 'hk03690',
        
        # 热门ETF (示例)
        '沪深300ETF': 'sh510300',
        '中证500ETF': 'sh510500',
        '创业板ETF': 'sz159915',
        '科技ETF': 'sh515000',
        '券商ETF': 'sh512000'
    }
    
    def __init__(self, timeout: int = 5):
        """
        初始化新浪财经API客户端
        
        Args:
            timeout: 请求超时时间(秒)
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def _parse_stock_data(self, code: str, raw_text: str) -> Optional[StockData]:
        """
        解析新浪财经返回的股票数据
        
        Args:
            code: 股票代码
            raw_text: 原始返回文本
            
        Returns:
            解析后的股票数据对象，失败返回None
        """
        try:
            # 提取数据部分: var hq_str_sh000001="数据";
            match = re.search(r'var hq_str_[^=]+="([^"]+)"', raw_text)
            if not match:
                logger.warning(f"无法从响应中提取数据: {raw_text[:100]}")
                return None
            
            data_str = match.group(1)
            if not data_str:
                logger.warning(f"股票 {code} 数据为空")
                return None
            
            # 按逗号分割数据
            fields = data_str.split(',')
            
            # 基本字段数量检查 - 美股和A股字段数量不同
            min_fields = 12 if code.startswith('usr_') else 32
            if len(fields) < min_fields:
                logger.warning(f"股票 {code} 数据字段不完整，只有 {len(fields)} 个字段，最少需要 {min_fields} 个")
                return None
            
            # 解析字段 (按新浪财经API字段顺序)
            name = fields[0]              # 股票名称
            
            # 检查是否是美股指数 (字段格式不同)
            if code.startswith('usr_'):
                # 美股指数数据格式: 名称,当前价,涨跌幅,时间,涨跌额,昨收,今开,最高,最低,...
                current_price = float(fields[1]) if fields[1] else 0.0  # 当前价格
                change_percent = float(fields[2]) if fields[2] else 0.0 # 涨跌幅(已经是百分比)
                # fields[3] 是时间戳字符串，跳过
                change_amount = float(fields[4]) if fields[4] else 0.0  # 涨跌额
                close_price = float(fields[5]) if fields[5] else 0.0   # 昨日收盘价
                open_price = float(fields[6]) if fields[6] else 0.0    # 今日开盘价
                high_price = float(fields[7]) if fields[7] else 0.0    # 今日最高价
                low_price = float(fields[8]) if fields[8] else 0.0     # 今日最低价
                
                # 美股成交量和成交额字段位置不同
                volume = int(float(fields[10])) if len(fields) > 10 and fields[10] else 0
                amount = float(fields[11]) if len(fields) > 11 and fields[11] else 0.0
                
                # 美股时间信息
                date = fields[3].split(' ')[0] if fields[3] else ""     # 从时间戳中提取日期
                time = fields[3].split(' ')[1] if fields[3] and ' ' in fields[3] else ""
                
                # 使用已有的涨跌幅，不需要重新计算
                change_percent_calc = change_percent
                change_amount_calc = change_amount
            else:
                # A股数据格式: 名称,今开,昨收,当前价,最高,最低,...
                open_price = float(fields[1]) if fields[1] else 0.0    # 今日开盘价
                close_price = float(fields[2]) if fields[2] else 0.0   # 昨日收盘价
                current_price = float(fields[3]) if fields[3] else 0.0  # 当前价格
                high_price = float(fields[4]) if fields[4] else 0.0    # 今日最高价
                low_price = float(fields[5]) if fields[5] else 0.0     # 今日最低价
                
                # 成交数据
                volume = int(float(fields[8])) if fields[8] else 0      # 成交量(股)
                amount = float(fields[9]) if fields[9] else 0.0        # 成交额(元)
                
                # 时间信息
                date = fields[30] if len(fields) > 30 else ""          # 日期
                time = fields[31] if len(fields) > 31 else ""          # 时间
                
                # 计算涨跌额和涨跌幅
                change_amount_calc = current_price - close_price if close_price > 0 else 0.0
                change_percent_calc = (change_amount_calc / close_price * 100) if close_price > 0 else 0.0
            
            stock_data = StockData(
                code=code,
                name=name,
                current_price=current_price,
                open_price=open_price,
                close_price=close_price,
                high_price=high_price,
                low_price=low_price,
                volume=volume,
                amount=amount,
                change_amount=change_amount_calc,
                change_percent=change_percent_calc,
                date=date,
                time=time,
                raw_data=data_str
            )
            
            logger.info(f"成功解析股票数据: {name}({code}) 价格:{current_price} 涨跌:{change_percent_calc:+.2f}%")
            return stock_data
            
        except (ValueError, IndexError) as e:
            logger.error(f"解析股票数据失败 {code}: {e}, 原始数据: {raw_text[:200]}")
            return None
    
    def get_stock_data(self, codes: Union[str, List[str]]) -> Dict[str, Optional[StockData]]:
        """
        获取股票实时数据
        
        Args:
            codes: 股票代码或代码列表 (支持批量查询)
            
        Returns:
            字典，key为股票代码，value为StockData对象
        """
        if isinstance(codes, str):
            codes = [codes]
        
        # 构建请求URL
        codes_str = ','.join(codes)
        url = f"{self.BASE_URL}{codes_str}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = 'gb2312'  # 新浪返回的是GBK编码
            
            result = {}
            
            # 如果只查询一只股票
            if len(codes) == 1:
                stock_data = self._parse_stock_data(codes[0], response.text)
                result[codes[0]] = stock_data
            else:
                # 批量查询，按行分割结果
                lines = response.text.strip().split('\n')
                for i, code in enumerate(codes):
                    if i < len(lines):
                        stock_data = self._parse_stock_data(code, lines[i])
                        result[code] = stock_data
                    else:
                        result[code] = None
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"请求新浪财经API失败: {e}")
            return {code: None for code in codes}
        except Exception as e:
            logger.error(f"处理新浪财经API数据失败: {e}")
            return {code: None for code in codes}
    
    def get_index_data(self, index_name: str) -> Optional[StockData]:
        """
        获取指数数据
        
        Args:
            index_name: 指数名称，支持中文名称或股票代码
            
        Returns:
            指数数据对象
        """
        # 转换中文名称为代码
        if index_name in self.STOCK_CODES:
            code = self.STOCK_CODES[index_name]
        else:
            code = index_name
        
        result = self.get_stock_data([code])
        return result.get(code)
    
    def get_multiple_indices(self, index_names: List[str]) -> Dict[str, Optional[StockData]]:
        """
        批量获取指数数据
        
        Args:
            index_names: 指数名称列表
            
        Returns:
            指数数据字典
        """
        # 转换名称为代码
        codes = []
        name_to_code = {}
        for name in index_names:
            if name in self.STOCK_CODES:
                code = self.STOCK_CODES[name]
            else:
                code = name
            codes.append(code)
            name_to_code[name] = code
        
        # 获取数据
        raw_result = self.get_stock_data(codes)
        
        # 转换回以名称为key的结果
        result = {}
        for name in index_names:
            code = name_to_code[name]
            result[name] = raw_result.get(code)
        
        return result
    
    def get_hot_etfs(self, count: int = 5) -> List[StockData]:
        """
        获取热门ETF数据
        
        Args:
            count: 返回数量
            
        Returns:
            热门ETF数据列表，按成交额排序
        """
        # 预定义的热门ETF代码列表
        etf_codes = [
            'sh510300',  # 沪深300ETF
            'sh510500',  # 中证500ETF
            'sz159915',  # 创业板ETF
            'sh515000',  # 科技ETF
            'sh512000',  # 券商ETF
            'sh513100',  # 纳指ETF
            'sh512980',  # 广发中证传媒ETF
            'sh512170',  # 医药ETF
            'sz159949',  # 创业板50ETF
            'sh510050'   # 上证50ETF
        ]
        
        # 获取所有ETF数据
        etf_data_dict = self.get_stock_data(etf_codes)
        
        # 过滤有效数据并按成交额排序
        valid_etfs = [data for data in etf_data_dict.values() if data is not None and data.amount > 0]
        valid_etfs.sort(key=lambda x: x.amount, reverse=True)
        
        return valid_etfs[:count]
    
    def is_market_open(self) -> bool:
        """
        检查市场是否开盘
        简单实现：检查上证指数数据的时间戳
        
        Returns:
            是否开盘
        """
        shanghai_data = self.get_index_data('上证指数')
        if not shanghai_data or not shanghai_data.date:
            return False
        
        # 检查数据是否为今天
        today = datetime.now().strftime('%Y-%m-%d')
        return shanghai_data.date == today


# 全局实例
sina_api = SinaFinanceAPI()