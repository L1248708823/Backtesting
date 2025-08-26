# -*- coding: utf-8 -*-
"""
通用数据模型

定义系统中通用的数据类型、枚举和基础模型。
"""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ParameterType(str, Enum):
    """
    参数类型枚举
    
    定义策略参数支持的所有数据类型，用于：
    - 参数验证：确保参数值符合预期类型
    - UI生成：前端根据类型自动生成对应输入组件
    - 文档生成：API文档中显示参数类型信息
    """
    NUMBER = "number"           # 数字输入（整数或浮点数）
    TEXT = "text"              # 文本输入（字符串）
    SELECT = "select"          # 单选下拉框
    BOOLEAN = "boolean"        # 布尔值选择（开关）
    DATE = "date"             # 日期选择器
    MULTI_SELECT = "multi_select"  # 多选框


class BaseResponseModel(BaseModel):
    """
    基础响应模型
    
    所有API响应都可以继承此模型，提供统一的响应结构。
    """
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    
    class Config:
        """Pydantic配置"""
        # 允许字段使用别名
        allow_population_by_field_name = True
        # 生成示例数据用于API文档
        schema_extra = {
            "example": {
                "success": True,
                "message": "操作成功"
            }
        }