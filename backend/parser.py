#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parser.py - Daily report parsing module

Handles:
- Date block extraction (YYYYMMDD or YYYY-MM-DD formats)
- Hours parsing (default 8h if not specified)
- Entry categorization based on keywords
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from config import Config


def get_current_week_range() -> Tuple[datetime, datetime]:
    """
    Get the current week's Monday to Friday date range
    based on the system date.
    
    Returns:
        Tuple of (monday_date, friday_date)
    """
    today = datetime.now()
    # Calculate days since Monday (Monday = 0)
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    friday = monday + timedelta(days=4)
    return monday, friday


def format_date(dt: datetime) -> str:
    """Format datetime as YYYY-MM-DD"""
    return dt.strftime('%Y-%m-%d')


def parse_date_block(text: str) -> List[Dict]:
    """
    Parse daily report text into date blocks.
    
    Supported formats:
    - 20251212 8h
    - 2025-12-12 8h
    - 20251212 (hours defaults to 8)
    
    Args:
        text: Raw daily report text
        
    Returns:
        List of dicts with keys: date, hours, content
    """
    # Patterns for date line detection
    pattern_compact = r'^\s*(\d{8})\s*(\d+(?:\.\d+)?\s*h)?\s*$'
    pattern_hyphen = r'^\s*(\d{4}-\d{2}-\d{2})\s*(\d+(?:\.\d+)?\s*h)?\s*$'
    
    lines = text.split('\n')
    blocks = []
    current_block = None
    
    for line in lines:
        line_stripped = line.strip()
        
        # Try compact format (YYYYMMDD)
        match = re.match(pattern_compact, line_stripped, re.IGNORECASE)
        if match:
            if current_block:
                blocks.append(current_block)
            
            date_str = match.group(1)
            hours_str = match.group(2)
            
            # Parse date
            try:
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                formatted_date = format_date(date_obj)
            except ValueError:
                formatted_date = date_str
            
            # Parse hours (default 8)
            hours = 8.0
            if hours_str:
                hours = float(hours_str.lower().replace('h', '').strip())
            
            current_block = {
                'date': formatted_date,
                'hours': hours,
                'content': []
            }
            continue
        
        # Try hyphen format (YYYY-MM-DD)
        match = re.match(pattern_hyphen, line_stripped, re.IGNORECASE)
        if match:
            if current_block:
                blocks.append(current_block)
            
            date_str = match.group(1)
            hours_str = match.group(2)
            
            hours = 8.0
            if hours_str:
                hours = float(hours_str.lower().replace('h', '').strip())
            
            current_block = {
                'date': date_str,
                'hours': hours,
                'content': []
            }
            continue
        
        # Add content to current block
        if current_block and line_stripped:
            current_block['content'].append(line_stripped)
        elif not current_block and line_stripped:
            # Content before any date block - create undated block
            if not blocks or blocks[-1].get('date'):
                blocks.append({
                    'date': None,
                    'hours': 8.0,
                    'content': []
                })
            if blocks:
                blocks[-1]['content'].append(line_stripped)
    
    # Don't forget the last block
    if current_block:
        blocks.append(current_block)
    
    return blocks


def categorize_entry(entry: str) -> str:
    """
    Categorize a single entry based on keywords.
    
    Categories:
    - 'research': PoC, 调研
    - 'service': 服务化, 接口化  
    - 'other_affairs': 临时工作, 运维, 权限, 工单, etc.
    - 'project': default
    
    Args:
        entry: Single entry text
        
    Returns:
        Category string
    """
    entry_lower = entry.lower()
    
    # Check for "other affairs" keywords first (Section 3)
    for keyword in Config.KEYWORDS_TEMPORARY:
        if keyword.lower() in entry_lower or keyword in entry:
            return 'other_affairs'
    
    for keyword in Config.KEYWORDS_OPS:
        if keyword.lower() in entry_lower or keyword in entry:
            return 'other_affairs'
    
    for keyword in Config.KEYWORDS_ADMIN:
        if keyword.lower() in entry_lower or keyword in entry:
            return 'other_affairs'
    
    # Check for research keywords
    for keyword in Config.KEYWORDS_RESEARCH:
        if keyword.lower() in entry_lower or keyword in entry:
            return 'research'
    
    # Check for service keywords
    for keyword in Config.KEYWORDS_SERVICE:
        if keyword.lower() in entry_lower or keyword in entry:
            return 'service'
    
    # Default to project
    return 'project'


def categorize_entries(blocks: List[Dict]) -> Dict[str, List[str]]:
    """
    Categorize all entries from parsed blocks.
    
    Args:
        blocks: List of parsed date blocks
        
    Returns:
        Dict with categories as keys and lists of entries as values
    """
    categories = {
        'project': [],
        'service': [],
        'research': [],
        'other_affairs': []
    }
    
    for block in blocks:
        for entry in block.get('content', []):
            category = categorize_entry(entry)
            categories[category].append(entry)
    
    return categories


def deduplicate_entries(entries: List[str]) -> List[str]:
    """
    Remove duplicate or highly similar entries.
    Uses simple exact match and substring deduplication.
    
    Args:
        entries: List of entry strings
        
    Returns:
        Deduplicated list
    """
    if not entries:
        return []
    
    seen = set()
    result = []
    
    for entry in entries:
        # Normalize: strip and lowercase for comparison
        normalized = entry.strip().lower()
        
        # Skip if exact duplicate
        if normalized in seen:
            continue
        
        # Skip if substring of existing entry
        is_substring = False
        for existing in seen:
            if normalized in existing or existing in normalized:
                is_substring = True
                break
        
        if not is_substring:
            seen.add(normalized)
            result.append(entry)
    
    return result


def parse_and_categorize(text: str) -> Dict:
    """
    Full parsing pipeline: parse text, categorize entries, deduplicate.
    
    Args:
        text: Raw daily report text
        
    Returns:
        Dict with:
        - blocks: raw parsed blocks
        - categories: categorized and deduplicated entries
        - week_range: current week Monday-Friday
    """
    monday, friday = get_current_week_range()
    
    blocks = parse_date_block(text)
    categories = categorize_entries(blocks)
    
    # Deduplicate each category
    for cat in categories:
        categories[cat] = deduplicate_entries(categories[cat])
    
    return {
        'blocks': blocks,
        'categories': categories,
        'week_range': {
            'monday': format_date(monday),
            'friday': format_date(friday)
        }
    }
