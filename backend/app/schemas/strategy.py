# -*- coding: utf-8 -*-
"""
策略相关API模式

定义策略管理相关的所有请求和响应数据结构。
将API层面的数据模型与业务逻辑层面的数据模型分离，
便于版本管理和接口演化。
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.models import ParameterDefinition, StrategyMetadata
from app.models.common import BaseResponseModel


class StrategyResponseSchemas:
    """策略相关响应模式集合"""
    
    class StrategyInfo(BaseModel):
        """
        单个策略信息响应模式
        
        用于 GET /strategies/{id} 和策略列表接口的响应。
        包含策略的完整信息和参数定义。
        """
        id: str = Field(..., description="策略唯一标识符")
        name: str = Field(..., description="策略显示名称")
        description: str = Field(..., description="策略详细说明")
        category: str = Field(..., description="策略分类")
        risk_level: str = Field(..., description="风险等级：低/中/高")
        supported_markets: List[str] = Field(..., description="支持的市场列表")
        author: str = Field(..., description="策略作者")
        version: str = Field(..., description="策略版本号")
        parameters: List[ParameterDefinition] = Field(..., description="策略参数定义列表")

        class Config:
            schema_extra = {
                "example": {
                    "id": "dca_strategy",
                    "name": "定投策略",
                    "description": "定期定额投资策略，通过分散投资时间降低市场波动风险",
                    "category": "定投类",
                    "risk_level": "低",
                    "supported_markets": ["A股", "美股"],
                    "author": "系统内置",
                    "version": "1.0.0",
                    "parameters": [
                        {
                            "name": "symbol",
                            "type": "text",
                            "default": "510300",
                            "description": "投资标的代码",
                            "required": True
                        }
                    ]
                }
            }
    
    class StrategyList(BaseResponseModel):
        """
        策略列表响应模式
        
        用于 GET /strategies 接口的响应。
        包含所有可用策略的基本信息。
        """
        data: List['StrategyResponseSchemas.StrategyInfo'] = Field(..., description="策略信息列表")
        total: int = Field(..., description="策略总数")

        class Config:
            schema_extra = {
                "example": {
                    "success": True,
                    "message": "获取策略列表成功",
                    "data": [
                        {
                            "id": "dca_strategy",
                            "name": "定投策略",
                            "category": "定投类",
                            "risk_level": "低"
                        }
                    ],
                    "total": 1
                }
            }

    class ValidationResult(BaseResponseModel):
        """
        参数验证结果响应模式
        
        用于 POST /strategies/{id}/validate 接口的响应。
        返回参数验证的结果和详细信息。
        """
        valid: bool = Field(..., description="参数是否通过验证")
        errors: List[str] = Field(default=[], description="验证错误列表")
        strategy_info: Dict[str, Any] = Field(default={}, description="策略实例信息")

        class Config:
            schema_extra = {
                "example": {
                    "success": True,
                    "message": "参数验证完成",
                    "valid": True,
                    "errors": [],
                    "strategy_info": {
                        "策略名称": "定投策略",
                        "投资标的": "510300",
                        "投资金额": "1000.00元"
                    }
                }
            }


class StrategyRequestSchemas:
    """策略相关请求模式集合"""
    
    class ParameterValidation(BaseModel):
        """
        参数验证请求模式
        
        用于 POST /strategies/{id}/validate 接口。
        客户端发送策略ID和参数值，服务端返回验证结果。
        """
        strategy_id: str = Field(..., description="要验证的策略ID")
        parameters: Dict[str, Any] = Field(..., description="策略参数键值对")

        class Config:
            schema_extra = {
                "example": {
                    "strategy_id": "dca_strategy",
                    "parameters": {
                        "symbol": "510300",
                        "investment_amount": 1000.0,
                        "frequency": "monthly"
                    }
                }
            }
    
    class StrategyQuery(BaseModel):
        """
        策略查询请求模式
        
        用于策略列表接口的查询参数。
        支持按分类、风险等级等条件筛选策略。
        """
        category: str = Field(default="", description="按分类筛选")
        risk_level: str = Field(default="", description="按风险等级筛选")
        market: str = Field(default="", description="按支持市场筛选")
        page: int = Field(default=1, ge=1, description="页码，从1开始")
        page_size: int = Field(default=20, ge=1, le=100, description="每页数量，1-100")

        class Config:
            schema_extra = {
                "example": {
                    "category": "定投类",
                    "risk_level": "低",
                    "market": "A股",
                    "page": 1,
                    "page_size": 20
                }
            }