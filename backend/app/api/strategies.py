# -*- coding: utf-8 -*-
"""
策略相关API接口
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from ..core.strategy_registry import registry
from ..models.strategy import StrategyInfo

router = APIRouter(prefix="/api/v1/strategies", tags=["strategies"])


@router.get("/", response_model=List[StrategyInfo])
async def list_strategies():
    """
    获取所有可用策略列表
    
    Returns:
        策略信息列表
    """
    try:
        strategies = registry.list_strategies()
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取策略列表失败: {str(e)}")


@router.get("/{strategy_id}", response_model=StrategyInfo)
async def get_strategy_info(strategy_id: str):
    """
    获取特定策略的详细信息
    
    Args:
        strategy_id: 策略ID
        
    Returns:
        策略详细信息
    """
    strategy_info = registry.get_strategy_info(strategy_id)
    
    if not strategy_info:
        raise HTTPException(
            status_code=404, 
            detail=f"策略不存在: {strategy_id}"
        )
        
    return strategy_info


@router.get("/{strategy_id}/parameters")
async def get_strategy_parameters(strategy_id: str):
    """
    获取策略的默认参数
    
    Args:
        strategy_id: 策略ID
        
    Returns:
        策略默认参数
    """
    parameters = registry.get_strategy_parameters(strategy_id)
    
    if parameters is None:
        raise HTTPException(
            status_code=404,
            detail=f"策略不存在: {strategy_id}"
        )
        
    return {
        "strategy_id": strategy_id,
        "parameters": parameters
    }