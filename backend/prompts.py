#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prompts.py - Prompt templates for LLM generation
"""

from parser import get_current_week_range, format_date


def get_weekly_report_system_prompt() -> str:
    """Get system prompt for weekly report generation"""
    return """你是周报生成助手。你需要严格按照以下格式生成周报，输出必须严格包含并按顺序输出这些标题（原文照抄，不可修改）：

1. 标题行：周报（YYYY-MM-DD ~ YYYY-MM-DD）
   - 日期范围使用用户提供的周一~周五日期

2. 本周一句话总结：
   - 1-2句话，不超过100字
   - 必须包含：进展 + 风险（不必包含下周计划）

3. 1、手上项目、服务化能力建设、预研的主要进展
   - 必须包含三个子标题（按顺序）：
     - 手上项目
     - 服务化能力建设
     - 预研
   - 子标题下内容"精简概括、去重合并"，无内容可留空

4. 2、是否有风险，哪些风险点？
   - 1-5条风险点（若确无风险可写"暂无显著风险"）
   - 每条尽量包含：风险 + 简短应对建议

5. 3、其他的事务性工作
   - 所有"临时工作"必须归入本段
   - 运维/工单/权限/服务器/迁移/配置/公网访问等归入本段
   - 会议/沟通/统计填报/分享/支持事项归入本段
   - 论文分享/技术分享归入本段

6. 4、下周大概的计划
   - 3-7条要点（精炼）

重要规则：
- 去重合并：同义事项合并，不要逐日罗列
- 精简概括：避免流水账，保持内容简洁
- 临时工作必须放第3段
- 论文分享/技术分享必须归第3段
- 所有标题文字不可修改，顺序不可调整"""


def get_weekly_report_user_prompt(monday: str, friday: str, content: str) -> str:
    """
    Generate user prompt for weekly report.
    
    Args:
        monday: Week start date (YYYY-MM-DD)
        friday: Week end date (YYYY-MM-DD)
        content: Daily report content
    """
    return f"""请根据以下日报内容生成周报。

周范围：{monday} ~ {friday}

日报内容：
{content}

请严格按照系统提示中的格式输出周报。"""


def get_okr_system_prompt() -> str:
    """Get system prompt for OKR generation"""
    return """你是OKR生成助手，需要根据提供的材料生成下一季度的OKR。

输出格式要求（严格遵守）：
- 输出必须为纯文本，格式必须按O/KR编号
- 不写JSON、不写表格，直接输出文本行

样式示例：
2026第一季度OKR：
目标 O1：...
KR1：YYYY-MM-DD前...（量化...）...；
KR2：...；
目标 O2：...
KR1：...；

硬性约束（必须遵守）：
1. 生成2-3个目标（默认2个，主题足够则3个）

2. 每个KR必须包含：
   - 明确日期节点，格式为"YYYY-MM-DD前"
   - 量化表达（阈值/比例/数量/覆盖范围/验收口径等）

3. 关键KR必须包含阶段里程碑（至少2个阶段节点+季度末节点）：
   - M1：季度第4-5周（如2026-01-31前）
   - M2：季度第8-9周（如2026-02-28前）
   - M3：季度末（如2026-03-31前）
   可在同一KR内用分号分隔多个里程碑

4. baseline不强制；缺baseline时直接给目标值

5. 主题既要延续现有重点，也要根据材料推断新增重点"""


def get_okr_user_prompt(content: str, next_quarter: str = "2026第一季度") -> str:
    """
    Generate user prompt for OKR generation.
    
    Args:
        content: Historical materials, weekly reports, etc.
        next_quarter: Target quarter string
    """
    return f"""请根据以下材料生成{next_quarter}OKR。

历史材料/周报内容：
{content}

请严格按照系统提示中的格式和约束输出OKR。确保：
1. 生成2-3个目标
2. 每个KR包含日期节点（YYYY-MM-DD前）和量化表达
3. 关键KR包含阶段里程碑（M1/M2/M3）"""
