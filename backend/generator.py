#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generator.py - Weekly report and OKR generation logic
"""

import logging
import re
import json
from typing import Dict, Optional, List
from parser import parse_and_categorize, get_current_week_range, format_date
from llm_client import get_llm_client, LLMClient
from prompts import (
    get_weekly_report_system_prompt,
    get_weekly_report_user_prompt,
    get_okr_system_prompt,
    get_okr_user_prompt
)
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_weekly_report(
    daily_content: str, 
    use_mock: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict:
    """
    Generate weekly report from daily report content.
    
    Args:
        daily_content: Raw daily report text
        use_mock: Whether to use mock LLM client
        start_date: Optional start date (YYYY-MM-DD format)
        end_date: Optional end date (YYYY-MM-DD format)
        
    Returns:
        Dict with:
        - success: bool
        - report: generated report string (if successful)
        - parsed_data: parsed content info
        - error: error message (if failed)
    """
    # Validate input length
    if len(daily_content) > Config.MAX_INPUT_CHARS:
        return {
            'success': False,
            'error': f'输入超过最大长度限制 ({Config.MAX_INPUT_CHARS} 字符)',
            'parsed_data': None
        }
    
    try:
        # Parse and categorize content
        parsed_data = parse_and_categorize(daily_content)
        
        # Use provided date range if available, otherwise use parsed range
        if start_date and end_date:
            monday = start_date
            friday = end_date
        else:
            monday = parsed_data['week_range']['monday']
            friday = parsed_data['week_range']['friday']
        
        # Get LLM client
        llm_client = get_llm_client(use_mock=use_mock)
        
        # Generate prompts
        system_prompt = get_weekly_report_system_prompt()
        user_prompt = get_weekly_report_user_prompt(monday, friday, daily_content)
        
        # Call LLM
        report = llm_client.call(user_prompt, system_prompt)
        
        return {
            'success': True,
            'report': report,
            'parsed_data': parsed_data
        }
        
    except Exception as e:
        logger.error(f"Weekly report generation failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'parsed_data': None
        }


def generate_okr(content: str, next_quarter: str = "2026第一季度", use_mock: bool = False) -> Dict:
    """
    Generate OKR from historical materials.
    
    Args:
        content: Historical materials, weekly reports, etc.
        next_quarter: Target quarter string
        use_mock: Whether to use mock LLM client
        
    Returns:
        Dict with:
        - success: bool
        - okr: generated OKR string (if successful)
        - error: error message (if failed)
    """
    # Validate input length
    if len(content) > Config.MAX_INPUT_CHARS:
        return {
            'success': False,
            'error': f'输入超过最大长度限制 ({Config.MAX_INPUT_CHARS} 字符)'
        }
    
    try:
        # Get LLM client
        llm_client = get_llm_client(use_mock=use_mock)
        
        # Generate prompts
        system_prompt = get_okr_system_prompt()
        user_prompt = get_okr_user_prompt(content, next_quarter)
        
        # Call LLM
        okr = llm_client.call(user_prompt, system_prompt)
        
        return {
            'success': True,
            'okr': okr
        }
        
    except Exception as e:
        logger.error(f"OKR generation failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def validate_weekly_report(report: str) -> Dict:
    """
    Validate weekly report structure against requirements.
    
    Args:
        report: Generated weekly report text
        
    Returns:
        Dict with validation results
    """
    required_sections = [
        '周报（',
        '本周一句话总结：',
        '1、手上项目、服务化能力建设、预研的主要进展',
        '手上项目',
        '服务化能力建设',
        '预研',
        '2、是否有风险，哪些风险点？',
        '3、其他的事务性工作',
        '4、下周大概的计划'
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in report:
            missing_sections.append(section)
    
    # Check section order
    order_valid = True
    prev_pos = -1
    for section in required_sections:
        pos = report.find(section)
        if pos != -1 and pos < prev_pos:
            order_valid = False
            break
        if pos != -1:
            prev_pos = pos
    
    return {
        'valid': len(missing_sections) == 0 and order_valid,
        'missing_sections': missing_sections,
        'order_valid': order_valid
    }


def validate_okr(okr: str) -> Dict:
    """
    Validate OKR structure against requirements.
    
    Args:
        okr: Generated OKR text
        
    Returns:
        Dict with validation results
    """
    import re
    
    # Check for objectives (O1, O2, etc.)
    objective_pattern = r'目标\s*O\d+'
    objectives = re.findall(objective_pattern, okr)
    
    # Check for KRs with date nodes
    kr_date_pattern = r'\d{4}-\d{2}-\d{2}前'
    date_nodes = re.findall(kr_date_pattern, okr)
    
    # Check for quantitative expressions
    quant_patterns = [
        r'≥|>=|≤|<=',
        r'\d+%',
        r'准确率',
        r'覆盖率',
        r'覆盖',
        r'数量',
        r'上线',
        r'验收',
        r'性能',
        r'可用性'
    ]
    
    quant_found = []
    for pattern in quant_patterns:
        if re.search(pattern, okr):
            quant_found.append(pattern)
    
    # Check for milestones (multiple date nodes in same KR suggest milestones)
    kr_pattern = r'KR\d+[：:].+?(?=KR\d+|目标\s*O\d+|$)'
    krs = re.findall(kr_pattern, okr, re.DOTALL)
    
    has_milestones = False
    for kr in krs:
        dates_in_kr = re.findall(kr_date_pattern, kr)
        if len(dates_in_kr) >= 2:
            has_milestones = True
            break
    
    return {
        'valid': len(objectives) >= 2 and len(date_nodes) > 0 and len(quant_found) > 0,
        'objective_count': len(objectives),
        'objectives_valid': 2 <= len(objectives) <= 3,
        'date_nodes_count': len(date_nodes),
        'has_date_nodes': len(date_nodes) > 0,
        'quantitative_expressions': quant_found,
        'has_quantitative': len(quant_found) > 0,
        'has_milestones': has_milestones
    }


# ========================================
# Career Asset Management: Entity Extraction
# ========================================

def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity between two strings using simple containment and edit-distance-like heuristics.
    Returns a score between 0 and 1.
    """
    if not str1 or not str2:
        return 0.0
    
    s1 = str1.strip().lower()
    s2 = str2.strip().lower()
    
    # Exact match
    if s1 == s2:
        return 1.0
    
    # One contains the other
    if s1 in s2 or s2 in s1:
        # Similarity based on length ratio
        shorter = min(len(s1), len(s2))
        longer = max(len(s1), len(s2))
        return shorter / longer
    
    # Find common substrings
    common_len = 0
    min_len = min(len(s1), len(s2))
    
    # Find longest common prefix
    for i in range(min_len):
        if s1[i] == s2[i]:
            common_len += 1
        else:
            break
    
    # If significant common prefix, consider similar
    if common_len > min_len * 0.5:
        return common_len / max(len(s1), len(s2))
    
    return 0.0


def find_best_matching_project(project_name: str, existing_projects: List[Dict], threshold: float = 0.6) -> Optional[Dict]:
    """
    Find the best matching project from existing projects based on name similarity.
    
    Args:
        project_name: The project name to match
        existing_projects: List of existing project dicts with 'id' and 'name' keys
        threshold: Minimum similarity threshold (default 0.6)
    
    Returns:
        Best matching project dict or None if no match above threshold
    """
    if not project_name or not existing_projects:
        return None
    
    best_match = None
    best_score = 0.0
    
    for project in existing_projects:
        existing_name = project.get('name', '')
        score = calculate_similarity(project_name, existing_name)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = project
    
    return best_match


def extract_work_items(log_content: str, log_date: str, use_mock: bool = False) -> Dict:
    """
    Extract structured work items from daily log content.
    
    Args:
        log_content: Raw daily log text
        log_date: Date of the log (YYYY-MM-DD)
        use_mock: Whether to use mock LLM client
        
    Returns:
        Dict with:
        - success: bool
        - work_items: list of extracted work items
        - extraction_quality: good | partial | insufficient
        - notes: extraction notes
        - error: error message (if failed)
    """
    if not log_content or not log_content.strip():
        return {
            'success': False,
            'error': '日志内容为空',
            'work_items': [],
            'extraction_quality': 'insufficient'
        }
    
    try:
        from prompts import (
            get_work_item_extraction_system_prompt,
            get_work_item_extraction_user_prompt
        )
        
        llm_client = get_llm_client(use_mock=use_mock)
        
        system_prompt = get_work_item_extraction_system_prompt()
        user_prompt = get_work_item_extraction_user_prompt(log_content, log_date)
        
        response = llm_client.call(user_prompt, system_prompt)
        
        # Parse JSON response
        # Try to extract JSON from response (may have markdown code blocks)
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response
        
        parsed = json.loads(json_str)
        
        # 后处理工作项：修复 null 值和过滤无效技能
        work_items = parsed.get('work_items', [])
        processed_items = []
        for item in work_items:
            # 处理 project 为 null 或 "null" 的情况
            if item.get('project') is None or str(item.get('project', '')).lower() in ['null', 'none', '']:
                item['project'] = '日常工作'
            
            # 过滤 skills 中的 null 和 "待补充"
            if 'skills' in item and item['skills']:
                item['skills'] = [
                    s for s in item['skills'] 
                    if s and str(s).lower() not in ['null', 'none', '待补充', '']
                ]
            
            processed_items.append(item)
        
        return {
            'success': True,
            'work_items': processed_items,
            'extraction_quality': parsed.get('extraction_quality', 'partial'),
            'notes': parsed.get('notes', ''),
            'raw_response': response
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in extraction: {e}")
        return {
            'success': False,
            'error': f'JSON解析失败: {str(e)}',
            'work_items': [],
            'extraction_quality': 'insufficient',
            'raw_response': response if 'response' in dir() else None
        }
    except Exception as e:
        logger.error(f"Work item extraction failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'work_items': [],
            'extraction_quality': 'insufficient'
        }


def generate_star_summary(project_name: str, work_items: list, use_mock: bool = False) -> Dict:
    """
    Generate STAR format summary for a project based on work items.
    
    Args:
        project_name: Name of the project
        work_items: List of work item dicts
        use_mock: Whether to use mock LLM client
        
    Returns:
        Dict with:
        - success: bool
        - summary: STAR format summary text
        - error: error message (if failed)
    """
    if not work_items:
        return {
            'success': False,
            'error': '没有工作项记录',
            'summary': ''
        }
    
    try:
        from prompts import (
            get_star_summary_system_prompt,
            get_star_summary_user_prompt
        )
        
        llm_client = get_llm_client(use_mock=use_mock)
        
        system_prompt = get_star_summary_system_prompt()
        user_prompt = get_star_summary_user_prompt(project_name, work_items)
        
        summary = llm_client.call(user_prompt, system_prompt)
        
        return {
            'success': True,
            'summary': summary
        }
        
    except Exception as e:
        logger.error(f"STAR summary generation failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'summary': ''
        }


def categorize_skills_with_llm(skills: List[Dict], use_mock: bool = False) -> Dict:
    """
    使用 LLM 智能识别技能分类。
    
    Args:
        skills: 技能列表，每个技能包含 id, name, category
        use_mock: 是否使用 mock LLM
        
    Returns:
        Dict with success, categorized_skills, etc.
    """
    try:
        if not skills:
            return {
                'success': True,
                'message': '没有需要分类的技能',
                'categorized_count': 0
            }
        
        llm_client = get_llm_client(use_mock=use_mock)
        
        # 构建技能列表字符串
        skill_names = [s['name'] for s in skills]
        skills_text = '\n'.join([f"- {name}" for name in skill_names])
        
        system_prompt = """你是一个技能分类专家。你需要将技能分类到以下四个类别之一：

1. tech（技术技能）：编程语言、框架、工具、数据库、云服务、DevOps、数据分析工具等技术相关技能
2. soft（软技能）：沟通、协调、管理、领导力、团队协作、文档写作、演讲表达、项目管理等人际和管理技能
3. domain（业务领域）：特定行业知识，如汽车、金融、制造、供应链、质量管理、财务、人力资源等业务知识
4. other（其他）：无法明确归类到以上三类的技能

请严格按照 JSON 格式返回结果，不要包含任何其他内容。"""

        user_prompt = f"""请对以下技能进行分类：

{skills_text}

请返回 JSON 格式，每个技能对应一个分类：
{{
  "技能名1": "tech",
  "技能名2": "soft",
  "技能名3": "domain",
  ...
}}

只返回 JSON，不要有其他文字。"""

        response = llm_client.call(user_prompt, system_prompt)
        
        # 解析 LLM 返回的 JSON
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                categories_map = json.loads(json_match.group())
            else:
                categories_map = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response}")
            return {
                'success': False,
                'error': f'LLM 返回格式错误: {str(e)}',
                'raw_response': response
            }
        
        # 构建结果
        categorized_skills = []
        for skill in skills:
            skill_name = skill['name']
            new_category = categories_map.get(skill_name, 'other')
            # 验证分类值
            if new_category not in ['tech', 'soft', 'domain', 'other']:
                new_category = 'other'
            categorized_skills.append({
                'id': skill['id'],
                'name': skill_name,
                'old_category': skill.get('category'),
                'new_category': new_category
            })
        
        return {
            'success': True,
            'categorized_skills': categorized_skills,
            'categorized_count': len(categorized_skills)
        }
        
    except Exception as e:
        logger.error(f"Skill categorization failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

