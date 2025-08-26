# -*- coding: utf-8 -*-
"""
通用计算工具组件

提供回测系统中常用的计算功能，包括：
1. 性能指标计算 (收益率、夏普比率、最大回撤等)
2. 数据处理工具 (数据清洗、格式转换等)
3. 图表数据生成 (为前端图表准备数据)

设计特点：
- 高度可复用：所有函数都是纯函数，无副作用
- 类型安全：使用类型注解，支持IDE智能提示
- 精确计算：使用Decimal避免浮点数精度问题
- 详细注释：每个函数都有详细说明和使用示例
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    total_return: Decimal               # 总收益率
    annualized_return: Decimal          # 年化收益率
    volatility: Decimal                 # 波动率（年化）
    sharpe_ratio: Decimal              # 夏普比率
    max_drawdown: Decimal              # 最大回撤
    max_drawdown_duration: int         # 最大回撤持续天数
    calmar_ratio: Decimal              # 卡尔玛比率
    win_rate: Decimal                  # 胜率
    profit_loss_ratio: Decimal         # 盈亏比
    total_trades: int                  # 总交易次数


class MetricsCalculator:
    """性能指标计算器"""
    
    @staticmethod
    def calculate_returns(price_series: List[Tuple[date, Decimal]]) -> List[Decimal]:
        """
        计算收益率序列
        
        Args:
            price_series: 价格时间序列 [(date, price), ...]
            
        Returns:
            List[Decimal]: 收益率序列
        """
        if len(price_series) < 2:
            return []
        
        returns = []
        for i in range(1, len(price_series)):
            prev_price = price_series[i-1][1]
            curr_price = price_series[i][1]
            
            if prev_price > 0:
                return_rate = (curr_price - prev_price) / prev_price
                returns.append(return_rate)
            else:
                returns.append(Decimal('0'))
        
        return returns
    
    @staticmethod
    def calculate_total_return(initial_value: Decimal, final_value: Decimal) -> Decimal:
        """
        计算总收益率
        
        Args:
            initial_value: 初始价值
            final_value: 最终价值
            
        Returns:
            Decimal: 总收益率
        """
        if initial_value <= 0:
            return Decimal('0')
        
        return (final_value - initial_value) / initial_value
    
    @staticmethod
    def calculate_annualized_return(total_return: Decimal, days: int) -> Decimal:
        """
        计算年化收益率
        
        Args:
            total_return: 总收益率
            days: 投资天数
            
        Returns:
            Decimal: 年化收益率
        """
        if days <= 0:
            return Decimal('0')
        
        years = Decimal(str(days)) / Decimal('365.25')
        if years <= 0:
            return Decimal('0')
        
        # 使用复利公式: (1 + total_return)^(1/years) - 1
        try:
            annualized = ((Decimal('1') + total_return) ** (Decimal('1') / years)) - Decimal('1')
            return annualized.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        except:
            return Decimal('0')
    
    @staticmethod
    def calculate_volatility(returns: List[Decimal], annualized: bool = True) -> Decimal:
        """
        计算波动率
        
        Args:
            returns: 收益率序列
            annualized: 是否年化
            
        Returns:
            Decimal: 波动率
        """
        if len(returns) < 2:
            return Decimal('0')
        
        try:
            # 转换为float进行计算（Decimal不支持标准差计算）
            returns_float = [float(r) for r in returns]
            std_dev = Decimal(str(statistics.stdev(returns_float)))
            
            if annualized:
                # 年化：日收益率波动率 * sqrt(252)
                std_dev = std_dev * (Decimal('252') ** Decimal('0.5'))
            
            return std_dev.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        except:
            return Decimal('0')
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[Decimal], risk_free_rate: Decimal = Decimal('0')) -> Decimal:
        """
        计算夏普比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率（年化）
            
        Returns:
            Decimal: 夏普比率
        """
        if len(returns) < 2:
            return Decimal('0')
        
        # 计算平均收益率（年化）
        avg_return = sum(returns) / len(returns) * Decimal('252')
        
        # 计算波动率（年化）
        volatility = MetricsCalculator.calculate_volatility(returns, annualized=True)
        
        if volatility <= 0:
            return Decimal('0')
        
        # 夏普比率 = (年化收益率 - 无风险利率) / 年化波动率
        sharpe = (avg_return - risk_free_rate) / volatility
        return sharpe.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_max_drawdown(value_series: List[Tuple[date, Decimal]]) -> Tuple[Decimal, int]:
        """
        计算最大回撤和持续时间
        
        Args:
            value_series: 价值时间序列 [(date, value), ...]
            
        Returns:
            Tuple[Decimal, int]: (最大回撤, 最大回撤持续天数)
        """
        if len(value_series) < 2:
            return Decimal('0'), 0
        
        max_drawdown = Decimal('0')
        max_duration = 0
        current_duration = 0
        peak = value_series[0][1]
        
        for date_val, value in value_series:
            if value > peak:
                peak = value
                current_duration = 0
            else:
                current_duration += 1
                if peak > 0:
                    drawdown = (peak - value) / peak
                    max_drawdown = max(max_drawdown, drawdown)
                    max_duration = max(max_duration, current_duration)
        
        return max_drawdown, max_duration
    
    @staticmethod
    def calculate_calmar_ratio(annualized_return: Decimal, max_drawdown: Decimal) -> Decimal:
        """
        计算卡尔玛比率
        
        Args:
            annualized_return: 年化收益率
            max_drawdown: 最大回撤
            
        Returns:
            Decimal: 卡尔玛比率
        """
        if max_drawdown <= 0:
            return Decimal('0')
        
        calmar = annualized_return / max_drawdown
        return calmar.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @classmethod
    def calculate_comprehensive_metrics(cls, 
                                      value_series: List[Tuple[date, Decimal]],
                                      transactions: Optional[List] = None) -> PerformanceMetrics:
        """
        计算综合性能指标
        
        Args:
            value_series: 价值时间序列
            transactions: 交易记录（可选）
            
        Returns:
            PerformanceMetrics: 综合性能指标
        """
        if len(value_series) < 2:
            return PerformanceMetrics(
                total_return=Decimal('0'),
                annualized_return=Decimal('0'),
                volatility=Decimal('0'),
                sharpe_ratio=Decimal('0'),
                max_drawdown=Decimal('0'),
                max_drawdown_duration=0,
                calmar_ratio=Decimal('0'),
                win_rate=Decimal('0'),
                profit_loss_ratio=Decimal('0'),
                total_trades=0
            )
        
        # 基础数据
        initial_value = value_series[0][1]
        final_value = value_series[-1][1]
        days = (value_series[-1][0] - value_series[0][0]).days
        
        # 计算收益率序列
        returns = cls.calculate_returns(value_series)
        
        # 计算各项指标
        total_return = cls.calculate_total_return(initial_value, final_value)
        annualized_return = cls.calculate_annualized_return(total_return, days)
        volatility = cls.calculate_volatility(returns)
        sharpe_ratio = cls.calculate_sharpe_ratio(returns)
        max_drawdown, max_dd_duration = cls.calculate_max_drawdown(value_series)
        calmar_ratio = cls.calculate_calmar_ratio(annualized_return, max_drawdown)
        
        # 交易相关指标
        win_rate = Decimal('0')
        profit_loss_ratio = Decimal('0')
        total_trades = 0
        
        if transactions:
            total_trades = len(transactions)
            # 这里可以添加更详细的交易分析逻辑
        
        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            calmar_ratio=calmar_ratio,
            win_rate=win_rate,
            profit_loss_ratio=profit_loss_ratio,
            total_trades=total_trades
        )


class DataProcessor:
    """数据处理工具"""
    
    @staticmethod
    def clean_price_data(price_data: Dict[date, Union[float, Decimal]]) -> Dict[date, Decimal]:
        """
        清洗价格数据
        
        Args:
            price_data: 原始价格数据
            
        Returns:
            Dict[date, Decimal]: 清洗后的价格数据
        """
        cleaned_data = {}
        
        for trade_date, price in price_data.items():
            try:
                # 转换为Decimal
                if isinstance(price, Decimal):
                    decimal_price = price
                else:
                    decimal_price = Decimal(str(price))
                
                # 验证价格有效性
                if decimal_price > 0:
                    cleaned_data[trade_date] = decimal_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                else:
                    logger.warning(f"发现无效价格数据: {trade_date}, {price}")
            except Exception as e:
                logger.warning(f"清洗价格数据时发生错误: {trade_date}, {price}, {e}")
                continue
        
        return cleaned_data
    
    @staticmethod
    def fill_missing_dates(price_data: Dict[date, Decimal], 
                          start_date: date, 
                          end_date: date,
                          method: str = 'forward_fill') -> Dict[date, Decimal]:
        """
        填充缺失日期的价格数据
        
        Args:
            price_data: 价格数据
            start_date: 开始日期
            end_date: 结束日期
            method: 填充方法 ('forward_fill', 'backward_fill', 'interpolate')
            
        Returns:
            Dict[date, Decimal]: 填充后的价格数据
        """
        filled_data = {}
        current_date = start_date
        last_price = None
        
        while current_date <= end_date:
            if current_date in price_data:
                filled_data[current_date] = price_data[current_date]
                last_price = price_data[current_date]
            elif method == 'forward_fill' and last_price is not None:
                filled_data[current_date] = last_price
            
            current_date += timedelta(days=1)
        
        return filled_data
    
    @staticmethod
    def resample_to_frequency(price_data: Dict[date, Decimal], 
                             frequency: str = 'weekly') -> Dict[date, Decimal]:
        """
        将价格数据重采样到指定频率
        
        Args:
            price_data: 日频价格数据
            frequency: 目标频率 ('weekly', 'monthly', 'quarterly')
            
        Returns:
            Dict[date, Decimal]: 重采样后的价格数据
        """
        if not price_data:
            return {}
        
        resampled_data = {}
        sorted_dates = sorted(price_data.keys())
        
        if frequency == 'weekly':
            # 每周取最后一个交易日
            current_week = None
            for trade_date in sorted_dates:
                week_key = trade_date.isocalendar()[:2]  # (year, week)
                if current_week != week_key:
                    current_week = week_key
                resampled_data[trade_date] = price_data[trade_date]
        
        elif frequency == 'monthly':
            # 每月取最后一个交易日
            current_month = None
            for trade_date in sorted_dates:
                month_key = (trade_date.year, trade_date.month)
                if current_month != month_key:
                    current_month = month_key
                resampled_data[trade_date] = price_data[trade_date]
        
        return resampled_data


class ChartDataGenerator:
    """图表数据生成器"""
    
    @staticmethod
    def generate_equity_curve_data(value_series: List[Tuple[date, Decimal]]) -> List[Dict[str, Any]]:
        """
        生成权益曲线图表数据
        
        Args:
            value_series: 价值时间序列
            
        Returns:
            List[Dict]: 图表数据
        """
        chart_data = []
        
        for trade_date, value in value_series:
            chart_data.append({
                "date": trade_date.isoformat(),
                "value": float(value),
                "timestamp": int(trade_date.strftime('%Y%m%d'))
            })
        
        return chart_data
    
    @staticmethod
    def generate_drawdown_chart_data(value_series: List[Tuple[date, Decimal]]) -> List[Dict[str, Any]]:
        """
        生成回撤图表数据
        
        Args:
            value_series: 价值时间序列
            
        Returns:
            List[Dict]: 回撤图表数据
        """
        if len(value_series) < 2:
            return []
        
        chart_data = []
        peak = value_series[0][1]
        
        for trade_date, value in value_series:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak if peak > 0 else Decimal('0')
            
            chart_data.append({
                "date": trade_date.isoformat(),
                "drawdown": float(drawdown),
                "drawdown_percent": float(drawdown * 100)
            })
        
        return chart_data
    
    @staticmethod
    def generate_returns_distribution_data(returns: List[Decimal], bins: int = 50) -> Dict[str, Any]:
        """
        生成收益率分布图表数据
        
        Args:
            returns: 收益率序列
            bins: 分箱数量
            
        Returns:
            Dict: 分布图表数据
        """
        if not returns:
            return {"bins": [], "counts": [], "statistics": {}}
        
        # 转换为float进行分箱
        returns_float = [float(r) for r in returns]
        
        try:
            import numpy as np
            
            # 计算直方图
            counts, bin_edges = np.histogram(returns_float, bins=bins)
            
            # 生成图表数据
            chart_data = {
                "bins": [
                    {
                        "start": float(bin_edges[i]),
                        "end": float(bin_edges[i+1]),
                        "count": int(counts[i]),
                        "frequency": float(counts[i] / len(returns_float))
                    }
                    for i in range(len(counts))
                ],
                "statistics": {
                    "mean": float(np.mean(returns_float)),
                    "std": float(np.std(returns_float)),
                    "min": float(np.min(returns_float)),
                    "max": float(np.max(returns_float)),
                    "percentiles": {
                        "5%": float(np.percentile(returns_float, 5)),
                        "25%": float(np.percentile(returns_float, 25)),
                        "50%": float(np.percentile(returns_float, 50)),
                        "75%": float(np.percentile(returns_float, 75)),
                        "95%": float(np.percentile(returns_float, 95))
                    }
                }
            }
            
            return chart_data
            
        except ImportError:
            # 如果没有numpy，使用简单的统计
            return {
                "bins": [],
                "statistics": {
                    "mean": float(sum(returns) / len(returns)),
                    "count": len(returns)
                }
            }
    
    @staticmethod
    def generate_monthly_returns_heatmap(value_series: List[Tuple[date, Decimal]]) -> Dict[str, Any]:
        """
        生成月度收益率热力图数据
        
        Args:
            value_series: 价值时间序列
            
        Returns:
            Dict: 热力图数据
        """
        if len(value_series) < 2:
            return {"data": [], "years": [], "months": []}
        
        # 按月统计收益率
        monthly_returns = {}
        monthly_values = {}
        
        for trade_date, value in value_series:
            month_key = (trade_date.year, trade_date.month)
            if month_key not in monthly_values:
                monthly_values[month_key] = []
            monthly_values[month_key].append((trade_date, value))
        
        # 计算月度收益率
        for month_key, values in monthly_values.items():
            if len(values) >= 2:
                values.sort(key=lambda x: x[0])
                start_value = values[0][1]
                end_value = values[-1][1]
                if start_value > 0:
                    monthly_return = (end_value - start_value) / start_value
                    monthly_returns[month_key] = float(monthly_return)
        
        # 生成热力图数据结构
        years = sorted(set(year for year, month in monthly_returns.keys()))
        months = list(range(1, 13))
        
        heatmap_data = []
        for year in years:
            for month in months:
                return_value = monthly_returns.get((year, month))
                heatmap_data.append({
                    "year": year,
                    "month": month,
                    "return": return_value,
                    "return_percent": return_value * 100 if return_value is not None else None
                })
        
        return {
            "data": heatmap_data,
            "years": years,
            "months": [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]
        }


class RiskMetrics:
    """风险指标计算"""
    
    @staticmethod
    def calculate_var(returns: List[Decimal], confidence_level: float = 0.95) -> Decimal:
        """
        计算风险价值(VaR)
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平
            
        Returns:
            Decimal: VaR值
        """
        if not returns:
            return Decimal('0')
        
        try:
            import numpy as np
            returns_array = np.array([float(r) for r in returns])
            var_value = np.percentile(returns_array, (1 - confidence_level) * 100)
            return Decimal(str(var_value))
        except ImportError:
            # 简单排序方法
            sorted_returns = sorted([float(r) for r in returns])
            index = int(len(sorted_returns) * (1 - confidence_level))
            return Decimal(str(sorted_returns[index])) if index < len(sorted_returns) else Decimal('0')
    
    @staticmethod
    def calculate_cvar(returns: List[Decimal], confidence_level: float = 0.95) -> Decimal:
        """
        计算条件风险价值(CVaR)
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平
            
        Returns:
            Decimal: CVaR值
        """
        if not returns:
            return Decimal('0')
        
        var_value = RiskMetrics.calculate_var(returns, confidence_level)
        
        # 计算小于VaR的收益率的平均值
        extreme_returns = [r for r in returns if r <= var_value]
        if not extreme_returns:
            return var_value
        
        cvar_value = sum(extreme_returns) / len(extreme_returns)
        return cvar_value.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)


# 工厂函数
def create_metrics_calculator() -> MetricsCalculator:
    """创建性能指标计算器实例"""
    return MetricsCalculator()


def create_data_processor() -> DataProcessor:
    """创建数据处理器实例"""
    return DataProcessor()


def create_chart_data_generator() -> ChartDataGenerator:
    """创建图表数据生成器实例"""
    return ChartDataGenerator()