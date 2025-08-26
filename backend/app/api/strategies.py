# -*- coding: utf-8 -*-
"""
策略管理API接口

重构后的API设计：
- 使用 schemas 定义请求/响应格式
- 使用 models 定义数据结构
- 分离API层和业务逻辑层
- 完善错误处理和文档
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

# 导入策略工厂和数据模型
from app.strategies import StrategyFactory
from app.models import StrategyMetadata, ParameterDefinition

# 导入API模式定义
from app.schemas.strategy import (
    StrategyRequestSchemas,
    StrategyResponseSchemas
)

router = APIRouter()


@router.get(
    "/", 
    response_model=List[StrategyResponseSchemas.StrategyInfo],
    summary="获取策略列表",
    description="获取所有可用策略的详细信息，包括参数定义"
)
async def get_strategies(
    category: Optional[str] = Query(None, description="按分类筛选策略"),
    risk_level: Optional[str] = Query(None, description="按风险等级筛选"),
    market: Optional[str] = Query(None, description="按支持市场筛选")
):
    """
    获取策略列表接口
    
    支持按分类、风险等级、支持市场进行筛选。
    返回策略的完整信息和参数定义，供前端生成配置界面。
    """
    try:
        strategies = []
        
        for metadata in StrategyFactory.get_all_strategies():
            # 应用筛选条件
            if category and metadata.category != category:
                continue
            if risk_level and metadata.risk_level != risk_level:
                continue
            if market and market not in metadata.supported_markets:
                continue
            
            # 获取策略参数定义
            parameters = StrategyFactory.get_strategy_parameters(metadata.id)
            
            # 构建响应对象
            strategy_response = StrategyResponseSchemas.StrategyInfo(
                id=metadata.id,
                name=metadata.name,
                description=metadata.description,
                category=metadata.category,
                risk_level=metadata.risk_level,
                supported_markets=metadata.supported_markets,
                author=metadata.author,
                version=metadata.version,
                parameters=parameters
            )
            strategies.append(strategy_response)
        
        return strategies
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"获取策略列表失败: {str(e)}"
        )


@router.get(
    "/{strategy_id}", 
    response_model=StrategyResponseSchemas.StrategyInfo,
    summary="获取单个策略信息",
    description="根据策略ID获取详细的策略信息和参数定义"
)
async def get_strategy(strategy_id: str):
    """
    获取单个策略详情接口
    
    根据策略ID返回该策略的完整信息，如果策略不存在返回404错误。
    """
    try:
        # 查找策略元数据
        all_strategies = StrategyFactory.get_all_strategies()
        metadata = None
        for s in all_strategies:
            if s.id == strategy_id:
                metadata = s
                break
        
        if not metadata:
            raise HTTPException(status_code=404, detail=f"策略 {strategy_id} 未找到")
        
        # 获取参数定义
        parameters = StrategyFactory.get_strategy_parameters(strategy_id)
        
        # 返回策略信息
        return StrategyResponseSchemas.StrategyInfo(
            id=metadata.id,
            name=metadata.name,
            description=metadata.description,
            category=metadata.category,
            risk_level=metadata.risk_level,
            supported_markets=metadata.supported_markets,
            author=metadata.author,
            version=metadata.version,
            parameters=parameters
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"获取策略信息失败: {str(e)}"
        )


@router.post(
    "/{strategy_id}/validate",
    response_model=StrategyResponseSchemas.ValidationResult,
    summary="验证策略参数",
    description="验证给定的策略参数是否符合策略要求"
)
async def validate_strategy_parameters(
    strategy_id: str, 
    request: StrategyRequestSchemas.ParameterValidation
):
    """
    策略参数验证接口
    
    接收策略ID和参数字典，返回验证结果。
    如果验证通过，还会返回策略实例的详细信息。
    """
    try:
        # 验证策略ID匹配
        if request.strategy_id != strategy_id:
            raise HTTPException(
                status_code=400, 
                detail="请求路径中的策略ID与请求体中的策略ID不匹配"
            )
        
        # 尝试创建策略实例进行参数验证
        strategy = StrategyFactory.create_strategy(strategy_id, request.parameters)
        
        # 获取策略详细信息（如果策略支持）
        strategy_info = {}
        if hasattr(strategy, 'get_strategy_info'):
            strategy_info = strategy.get_strategy_info()
        
        return StrategyResponseSchemas.ValidationResult(
            success=True,
            message="参数验证通过",
            valid=True,
            errors=[],
            strategy_info=strategy_info
        )
        
    except ValueError as e:
        # 参数验证错误
        return StrategyResponseSchemas.ValidationResult(
            success=True,
            message="参数验证完成",
            valid=False,
            errors=[str(e)],
            strategy_info={}
        )
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"参数验证出错: {str(e)}"
        )