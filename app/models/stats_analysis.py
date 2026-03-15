from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

# 导入 TYPE_CHECKING 避免循环导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User

# 通用模型
class StatsAnalysisBase(SQLModel):
    # 词云和柱状图数据 (存储为 JSON 字符串)
    materials_freq: str = Field(default="{}", description="高频材料词频字典")
    risks_freq: str = Field(default="{}", description="高频风险词频字典")
    
    # 饼图数据
    complexity_distribution: str = Field(default="{}", description="通知复杂度分布 (高/中/低)")
    notice_type_distribution: str = Field(default="{}", description="通知类型分布")
    
    # 时间节省估算数据
    total_time_saved_minutes: int = Field(default=0, description="累计节省的时间(分钟)")
    avg_time_saved_minutes: int = Field(default=0, description="平均每篇节省的时间(分钟)")
    time_saved_distribution: str = Field(default="{}", description="每月/每周节省时间柱状图数据")
    
    # 其他基础统计
    total_parsed_count: int = Field(default=0, description="总共解析的通知数量")
    
    # 统计所属的用户
    user_id: Optional[int] = Field(default=None, foreign_key="user.uid", description="所属用户，如果为空则代表全局统计")

# 数据库模型
class StatsAnalysis(StatsAnalysisBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    updated_time: datetime = Field(default_factory=datetime.now)

    # 建立与 User 的多对一关系
    user: Optional["User"] = Relationship(back_populates="stats_analyses")
