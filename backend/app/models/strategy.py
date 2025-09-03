# -*- coding: utf-8 -*-
"""
策略相关数据模型

定义策略参数、元数据和配置相关的数据模型。

📚 学习点：
- 策略参数化设计：通过数据模型定义参数，支持动态配置
- 元数据模式：策略信息与策略实现分离，便于管理和展示
- 依赖关系：参数之间的依赖关系建模
"""

from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
from .common import (
    StrategyType, MarketType, ParameterType, 
    ParameterOption, ValidationRule
)


# =============================================================================
# 策略参数相关模型
# =============================================================================

class ParameterDependency(BaseModel):
    """
    参数依赖关系模型
    
    📚 学习点：用于定义参数间的依赖关系
    例如：只有当frequency="monthly"时，investment_day参数才显示
    """
    parameter: str = Field(..., description="依赖的参数名")
    values: List[Union[str, int, float, bool]] = Field(..., description="依赖的参数值列表")
    operator: str = Field("in", description="比较操作符：in, not_in, eq, ne, gt, lt等")


class ParameterDefinition(BaseModel):
    """
    策略参数定义模型
    
    📚 学习点：
    - 这是参数化配置的核心模型
    - 前端根据这个模型动态生成配置界面
    - 后端根据这个模型进行参数验证
    """
    name: str = Field(..., description="参数名称（代码中使用的变量名）")
    display_name: str = Field(..., description="参数显示名称（界面显示）")
    description: str = Field(..., description="参数详细说明")
    parameter_type: ParameterType = Field(..., description="参数类型")
    
    # 默认值和验证
    default_value: Optional[Any] = Field(None, description="默认值")
    validation_rules: Optional[ValidationRule] = Field(None, description="验证规则")
    
    # 选择类型参数的选项
    options: Optional[List[ParameterOption]] = Field(None, description="可选项（仅select类型）")
    
    # 依赖关系
    dependencies: Optional[List[ParameterDependency]] = Field(None, description="参数依赖关系")
    
    # 界面相关
    group: Optional[str] = Field(None, description="参数分组（用于界面组织）")
    order: int = Field(0, description="显示顺序")
    advanced: bool = Field(False, description="是否为高级参数")


class StrategyMetadata(BaseModel):
    """
    策略元数据模型
    
    📚 学习点：
    - 策略的"身份证"，描述策略的基本信息
    - 与策略实现代码分离，便于管理和展示
    """
    id: str = Field(..., description="策略唯一标识符")
    name: str = Field(..., description="策略名称")
    description: str = Field(..., description="策略详细描述")
    
    # 分类信息
    category: str = Field(..., description="策略分类")
    strategy_type: StrategyType = Field(..., description="策略类型")
    risk_level: str = Field(..., description="风险等级：低/中/高")
    
    # 市场支持
    supported_markets: List[MarketType] = Field(..., description="支持的市场类型")
    
    # 作者信息
    author: str = Field(..., description="策略作者")
    version: str = Field(..., description="策略版本")
    created_date: Optional[str] = Field(None, description="创建日期")
    
    # 标签和特性
    tags: List[str] = Field(default_factory=list, description="策略标签")
    features: List[str] = Field(default_factory=list, description="策略特性")
    
    # 参数定义
    parameters: List[ParameterDefinition] = Field(default_factory=list, description="策略参数定义")


# =============================================================================
# 策略配置和执行相关模型
# =============================================================================

class StrategyParameters(BaseModel):
    """
    策略参数值模型
    
    📚 学习点：
    - 这里存储的是参数的具体值
    - 与ParameterDefinition配合使用：Definition定义规则，Parameters存储值
    """
    strategy_id: str = Field(..., description="策略ID")
    parameters: Dict[str, Any] = Field(..., description="参数值字典")
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """获取参数值"""
        return self.parameters.get(name, default)
    
    def set_parameter(self, name: str, value: Any) -> None:
        """设置参数值"""
        self.parameters[name] = value


class StrategyConfig(BaseModel):
    """
    策略完整配置模型
    
    📚 学习点：结合元数据和参数值的完整配置
    """
    metadata: StrategyMetadata = Field(..., description="策略元数据")
    parameters: StrategyParameters = Field(..., description="策略参数")


# =============================================================================
# 策略验证和信息模型
# =============================================================================

class ParameterValidationError(BaseModel):
    """参数验证错误模型"""
    parameter_name: str = Field(..., description="参数名称")
    error_message: str = Field(..., description="错误消息")
    error_code: str = Field(..., description="错误代码")


class StrategyValidationResult(BaseModel):
    """策略参数验证结果模型"""
    is_valid: bool = Field(..., description="验证是否通过")
    errors: List[ParameterValidationError] = Field(default_factory=list, description="验证错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告信息列表")


class StrategyInfo(BaseModel):
    """
    策略详细信息模型（用于API响应）
    """
    metadata: StrategyMetadata = Field(..., description="策略元数据")
    status: str = Field("available", description="策略状态")
    usage_count: int = Field(0, description="使用次数")
    last_updated: Optional[str] = Field(None, description="最后更新时间")


# =============================================================================
# 预定义的常用参数
# =============================================================================

def create_symbol_parameter() -> ParameterDefinition:
    """创建标的代码参数定义（通用）"""
    return ParameterDefinition(
        name="symbol",
        display_name="投资标的",
        description="要投资的标的代码，如：510300（沪深300ETF）、SPY（标普500ETF）",
        parameter_type=ParameterType.STRING,
        default_value="510300",
        validation_rules=ValidationRule(
            min_length=3,
            max_length=20,
            pattern=r"^[A-Za-z0-9]+$",
            required=True
        ),
        group="基础配置",
        order=1
    )


def create_amount_parameter() -> ParameterDefinition:
    """创建投资金额参数定义（通用）"""
    return ParameterDefinition(
        name="investment_amount", 
        display_name="投资金额",
        description="每期投资金额（元），建议不少于500元以降低手续费影响",
        parameter_type=ParameterType.NUMBER,
        default_value=1000.0,
        validation_rules=ValidationRule(
            min_value=100.0,
            max_value=1000000.0,
            required=True
        ),
        group="基础配置",
        order=2
    )


def create_date_range_parameters() -> List[ParameterDefinition]:
    """创建日期范围参数定义（通用）"""
    return [
        ParameterDefinition(
            name="start_date",
            display_name="开始日期", 
            description="回测开始日期",
            parameter_type=ParameterType.DATE,
            validation_rules=ValidationRule(required=True),
            group="时间配置",
            order=10
        ),
        ParameterDefinition(
            name="end_date",
            display_name="结束日期",
            description="回测结束日期",  
            parameter_type=ParameterType.DATE,
            validation_rules=ValidationRule(required=True),
            group="时间配置",
            order=11
        )
    ]


# 导出所有策略相关类型
__all__ = [
    # 参数相关
    "ParameterDependency", "ParameterDefinition", "StrategyParameters",
    
    # 策略元数据
    "StrategyMetadata", "StrategyConfig", 
    
    # 验证相关
    "ParameterValidationError", "StrategyValidationResult",
    
    # 信息展示
    "StrategyInfo",
    
    # 工具函数
    "create_symbol_parameter", "create_amount_parameter", "create_date_range_parameters"
]