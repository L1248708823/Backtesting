# -*- coding: utf-8 -*-
"""
学习知识点记录机制

用于记录和管理项目中的学习知识点，支持渐进式学习和知识回顾。

📚 核心理念：
- 第一次遇到概念时详细记录
- 后续遇到时简化注释
- 定期回顾和清理过时的学习注释
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict

# =============================================================================
# 学习概念分类
# =============================================================================

class ConceptCategory(str, Enum):
    """学习概念分类"""
    FRAMEWORK = "framework"          # 框架相关 (FastAPI, Backtrader等)
    PATTERN = "pattern"             # 设计模式
    PYTHON = "python"               # Python语法特性
    FINANCE = "finance"             # 金融量化概念
    API = "api"                     # API设计概念
    DATABASE = "database"           # 数据库相关
    ASYNC = "async"                 # 异步编程
    TESTING = "testing"             # 测试相关


class LearningLevel(str, Enum):
    """学习程度"""
    NEW = "new"                     # 新概念，需要详细说明
    FAMILIAR = "familiar"           # 已熟悉，简化说明即可
    MASTERED = "mastered"           # 已掌握，可以去掉注释


# =============================================================================
# 学习记录数据结构
# =============================================================================

@dataclass
class ConceptRecord:
    """单个概念记录"""
    name: str                       # 概念名称
    category: ConceptCategory       # 概念分类
    description: str                # 详细描述
    example: Optional[str] = None   # 代码示例
    analogy: Optional[str] = None   # 类比说明（如：类似Spring的@Service）
    
    # 学习状态
    level: LearningLevel = LearningLevel.NEW
    first_seen: str = ""            # 首次遇到时间
    last_reviewed: str = ""         # 最后复习时间
    usage_count: int = 0            # 使用次数
    
    # 关联信息
    related_concepts: List[str] = None    # 相关概念
    files_used: List[str] = None          # 使用该概念的文件
    
    def __post_init__(self):
        if self.related_concepts is None:
            self.related_concepts = []
        if self.files_used is None:
            self.files_used = []
        if not self.first_seen:
            self.first_seen = datetime.now().isoformat()


@dataclass 
class LearningSession:
    """学习会话记录"""
    date: str                       # 学习日期
    concepts_learned: List[str]     # 学到的新概念
    concepts_reviewed: List[str]    # 复习的概念  
    notes: str = ""                 # 会话笔记


# =============================================================================
# 学习跟踪器
# =============================================================================

class LearningTracker:
    """
    学习跟踪器
    
    📚 功能：
    - 记录新概念
    - 更新学习状态
    - 生成学习报告
    - 管理注释清理
    """
    
    def __init__(self, storage_path: str = "learning_progress.json"):
        self.storage_path = Path(storage_path)
        self.concepts: Dict[str, ConceptRecord] = {}
        self.sessions: List[LearningSession] = []
        self._load_progress()
    
    def record_concept(self, 
                      name: str, 
                      category: ConceptCategory,
                      description: str,
                      example: Optional[str] = None,
                      analogy: Optional[str] = None,
                      file_path: Optional[str] = None) -> ConceptRecord:
        """
        记录新概念或更新已有概念
        
        📚 用法：
        tracker.record_concept(
            name="Pydantic BaseModel",
            category=ConceptCategory.FRAMEWORK, 
            description="数据验证和序列化的基类",
            analogy="类似Java的Bean Validation"
        )
        """
        if name in self.concepts:
            # 更新现有概念
            concept = self.concepts[name]
            concept.usage_count += 1
            concept.last_reviewed = datetime.now().isoformat()
            if file_path and file_path not in concept.files_used:
                concept.files_used.append(file_path)
        else:
            # 创建新概念
            concept = ConceptRecord(
                name=name,
                category=category,
                description=description,
                example=example,
                analogy=analogy
            )
            if file_path:
                concept.files_used.append(file_path)
            self.concepts[name] = concept
        
        self._save_progress()
        return concept
    
    def update_learning_level(self, name: str, level: LearningLevel):
        """更新概念的学习程度"""
        if name in self.concepts:
            self.concepts[name].level = level
            self._save_progress()
    
    def mark_as_familiar(self, name: str):
        """标记概念为已熟悉"""
        self.update_learning_level(name, LearningLevel.FAMILIAR)
    
    def mark_as_mastered(self, name: str):
        """标记概念为已掌握"""
        self.update_learning_level(name, LearningLevel.MASTERED)
    
    def get_concept(self, name: str) -> Optional[ConceptRecord]:
        """获取概念记录"""
        return self.concepts.get(name)
    
    def get_concepts_by_category(self, category: ConceptCategory) -> List[ConceptRecord]:
        """按分类获取概念"""
        return [c for c in self.concepts.values() if c.category == category]
    
    def get_concepts_by_level(self, level: LearningLevel) -> List[ConceptRecord]:
        """按学习程度获取概念"""
        return [c for c in self.concepts.values() if c.level == level]
    
    def should_show_detailed_comment(self, name: str) -> bool:
        """判断是否应该显示详细注释"""
        concept = self.get_concept(name)
        if not concept:
            return True  # 新概念，显示详细注释
        return concept.level == LearningLevel.NEW
    
    def should_show_simplified_comment(self, name: str) -> bool:
        """判断是否应该显示简化注释"""
        concept = self.get_concept(name)
        if not concept:
            return False
        return concept.level == LearningLevel.FAMILIAR
    
    def should_remove_comment(self, name: str) -> bool:
        """判断是否应该移除注释"""
        concept = self.get_concept(name)
        if not concept:
            return False
        return concept.level == LearningLevel.MASTERED
    
    def start_learning_session(self) -> str:
        """开始新的学习会话"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        return session_id
    
    def end_learning_session(self, 
                           session_id: str, 
                           concepts_learned: List[str],
                           concepts_reviewed: List[str],
                           notes: str = ""):
        """结束学习会话"""
        session = LearningSession(
            date=session_id,
            concepts_learned=concepts_learned,
            concepts_reviewed=concepts_reviewed,
            notes=notes
        )
        self.sessions.append(session)
        self._save_progress()
    
    def generate_learning_report(self) -> Dict[str, Any]:
        """生成学习报告"""
        total_concepts = len(self.concepts)
        new_concepts = len(self.get_concepts_by_level(LearningLevel.NEW))
        familiar_concepts = len(self.get_concepts_by_level(LearningLevel.FAMILIAR))
        mastered_concepts = len(self.get_concepts_by_level(LearningLevel.MASTERED))
        
        category_stats = {}
        for category in ConceptCategory:
            category_stats[category.value] = len(self.get_concepts_by_category(category))
        
        return {
            "total_concepts": total_concepts,
            "learning_progress": {
                "new": new_concepts,
                "familiar": familiar_concepts,
                "mastered": mastered_concepts
            },
            "category_distribution": category_stats,
            "recent_sessions": len(self.sessions),
            "most_used_concepts": self._get_most_used_concepts(5)
        }
    
    def suggest_review_concepts(self, limit: int = 5) -> List[ConceptRecord]:
        """建议复习的概念"""
        familiar_concepts = self.get_concepts_by_level(LearningLevel.FAMILIAR)
        # 按最后复习时间排序，最久未复习的优先
        familiar_concepts.sort(key=lambda x: x.last_reviewed or "")
        return familiar_concepts[:limit]
    
    def cleanup_mastered_comments(self) -> List[str]:
        """获取可以清理注释的文件列表"""
        mastered_concepts = self.get_concepts_by_level(LearningLevel.MASTERED)
        files_to_cleanup = set()
        for concept in mastered_concepts:
            files_to_cleanup.update(concept.files_used)
        return list(files_to_cleanup)
    
    def _get_most_used_concepts(self, limit: int) -> List[Dict[str, Any]]:
        """获取最常用的概念"""
        concepts = list(self.concepts.values())
        concepts.sort(key=lambda x: x.usage_count, reverse=True)
        return [
            {"name": c.name, "category": c.category.value, "usage_count": c.usage_count}
            for c in concepts[:limit]
        ]
    
    def _load_progress(self):
        """加载学习进度"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载概念记录
                for name, concept_data in data.get('concepts', {}).items():
                    concept = ConceptRecord(
                        name=concept_data['name'],
                        category=ConceptCategory(concept_data['category']),
                        description=concept_data['description'],
                        example=concept_data.get('example'),
                        analogy=concept_data.get('analogy'),
                        level=LearningLevel(concept_data.get('level', LearningLevel.NEW.value)),
                        first_seen=concept_data.get('first_seen', ''),
                        last_reviewed=concept_data.get('last_reviewed', ''),
                        usage_count=concept_data.get('usage_count', 0)
                    )
                    concept.related_concepts = concept_data.get('related_concepts', [])
                    concept.files_used = concept_data.get('files_used', [])
                    self.concepts[name] = concept
                
                # 加载会话记录
                for session_data in data.get('sessions', []):
                    session = LearningSession(
                        date=session_data['date'],
                        concepts_learned=session_data['concepts_learned'],
                        concepts_reviewed=session_data['concepts_reviewed'],
                        notes=session_data.get('notes', '')
                    )
                    self.sessions.append(session)
                    
            except Exception as e:
                print(f"加载学习进度失败: {e}")
    
    def _save_progress(self):
        """保存学习进度"""
        try:
            data = {
                'concepts': {
                    name: asdict(concept) 
                    for name, concept in self.concepts.items()
                },
                'sessions': [asdict(session) for session in self.sessions],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存学习进度失败: {e}")


# =============================================================================
# 预定义的常用概念
# =============================================================================

def setup_common_concepts(tracker: LearningTracker):
    """设置项目中的常用概念"""
    
    # FastAPI相关概念
    tracker.record_concept(
        name="FastAPI Dependency Injection",
        category=ConceptCategory.FRAMEWORK,
        description="FastAPI的依赖注入系统，通过Depends()实现",
        analogy="类似Spring Framework的@Autowired",
        example="def get_db(db: Session = Depends(get_database))"
    )
    
    tracker.record_concept(
        name="Pydantic BaseModel",
        category=ConceptCategory.FRAMEWORK,
        description="数据验证和序列化的基类，自动进行类型检查",
        analogy="类似Java的Bean Validation + Jackson序列化",
        example="class User(BaseModel): name: str; age: int"
    )
    
    # Backtrader相关概念
    tracker.record_concept(
        name="Backtrader Strategy",
        category=ConceptCategory.FRAMEWORK,
        description="Backtrader的策略基类，通过继承实现交易策略",
        example="class MyStrategy(bt.Strategy): def next(self): pass"
    )
    
    tracker.record_concept(
        name="Backtrader Cerebro",
        category=ConceptCategory.FRAMEWORK,
        description="Backtrader的回测引擎，协调数据、策略、经纪商等组件",
        analogy="类似Spring的ApplicationContext，管理所有组件"
    )
    
    # Python异步编程
    tracker.record_concept(
        name="Python asyncio",
        category=ConceptCategory.ASYNC,
        description="Python的异步编程库，用于编写并发代码",
        example="async def func(): await some_async_operation()"
    )
    
    # 设计模式
    tracker.record_concept(
        name="策略模式",
        category=ConceptCategory.PATTERN,
        description="定义算法族，并使它们可以互相替换",
        analogy="类似多态，但更侧重于算法的封装"
    )


# =============================================================================
# 全局学习跟踪器实例
# =============================================================================

# 创建全局学习跟踪器实例
learning_tracker = LearningTracker("backend/learning_progress.json")

# 设置常用概念
setup_common_concepts(learning_tracker)

# 便捷函数
def record_learning(name: str, category: ConceptCategory, description: str, 
                   example: str = None, analogy: str = None, file_path: str = None):
    """便捷的概念记录函数"""
    return learning_tracker.record_concept(name, category, description, example, analogy, file_path)

def check_comment_level(name: str) -> str:
    """检查注释级别"""
    if learning_tracker.should_show_detailed_comment(name):
        return "detailed"
    elif learning_tracker.should_show_simplified_comment(name):
        return "simplified" 
    elif learning_tracker.should_remove_comment(name):
        return "remove"
    return "detailed"

def generate_progress_report():
    """生成学习进度报告"""
    return learning_tracker.generate_learning_report()


# 导出
__all__ = [
    "ConceptCategory", "LearningLevel", "ConceptRecord", "LearningSession",
    "LearningTracker", "learning_tracker", 
    "record_learning", "check_comment_level", "generate_progress_report"
]