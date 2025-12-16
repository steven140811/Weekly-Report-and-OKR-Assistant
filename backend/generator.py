#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generator.py - Weekly report and OKR generation logic
"""

import logging
from typing import Dict, Optional
from parser import parse_and_categorize, get_current_week_range, format_date
from llm_client import get_llm_client, LLMClient
from prompts import (
    get_weekly_report_system_prompt,
    get_weekly_report_user_prompt,
    get_okr_system_prompt,
    get_okr_user_prompt
)
from config import Config
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_weekly_report_format(report: str) -> str:
    """
    Clean up the weekly report format by removing unnecessary numbering.
    Remove patterns like "1.", "2.", "3.", "4.", "5." at the beginning of lines.
    
    Args:
        report: Raw report text from LLM
        
    Returns:
        Cleaned report text
    """
    lines = report.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove leading number patterns like "1.", "2.", etc. only at the very start of the line
        # But preserve them within the section titles like "1、手上项目"
        stripped = line.lstrip()
        
        # Check if line starts with a number followed by a dot and space (e.g., "1. ")
        # This pattern indicates a list item we want to remove
        if re.match(r'^\d+\.\s+', stripped):
            # Remove the "1. " pattern
            cleaned = re.sub(r'^\d+\.\s+', '', stripped)
            cleaned_lines.append(cleaned)
        else:
            # Keep the line as is (preserving original indentation intent)
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def generate_weekly_report(daily_content: str, use_mock: bool = False) -> Dict:
    """
    Generate weekly report from daily report content.
    
    Args:
        daily_content: Raw daily report text
        use_mock: Whether to use mock LLM client
        
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
        
        # Get week range
        monday = parsed_data['week_range']['monday']
        friday = parsed_data['week_range']['friday']
        
        # Get LLM client
        llm_client = get_llm_client(use_mock=use_mock)
        
        # Generate prompts
        system_prompt = get_weekly_report_system_prompt()
        user_prompt = get_weekly_report_user_prompt(monday, friday, daily_content)
        
        # Call LLM
        report = llm_client.call(user_prompt, system_prompt)
        
        # Clean up the report format
        report = clean_weekly_report_format(report)
        
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
