#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_parser.py - Tests for daily report parsing
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import (
    parse_date_block,
    categorize_entry,
    categorize_entries,
    deduplicate_entries,
    parse_and_categorize,
    get_current_week_range,
    format_date
)


class TestDateBlockParsing:
    """Tests for date block extraction"""
    
    def test_parse_compact_date_format(self):
        """Test parsing YYYYMMDD format"""
        text = """20251212 8h
完成O类文档生产环境部署
修复若干提取问题"""
        
        blocks = parse_date_block(text)
        assert len(blocks) == 1
        assert blocks[0]['date'] == '2025-12-12'
        assert blocks[0]['hours'] == 8.0
        assert len(blocks[0]['content']) == 2
    
    def test_parse_hyphen_date_format(self):
        """Test parsing YYYY-MM-DD format"""
        text = """2025-12-12 8h
完成O类文档生产环境部署"""
        
        blocks = parse_date_block(text)
        assert len(blocks) == 1
        assert blocks[0]['date'] == '2025-12-12'
        assert blocks[0]['hours'] == 8.0
    
    def test_parse_date_without_hours(self):
        """Test default hours = 8 when not specified"""
        text = """20251212
完成部署工作"""
        
        blocks = parse_date_block(text)
        assert len(blocks) == 1
        assert blocks[0]['hours'] == 8.0
    
    def test_parse_multiple_date_blocks(self):
        """Test parsing multiple date blocks"""
        text = """20251211 8h
周一工作内容

20251212 8h
周二工作内容

20251213 8h
周三工作内容"""
        
        blocks = parse_date_block(text)
        assert len(blocks) == 3
        assert blocks[0]['date'] == '2025-12-11'
        assert blocks[1]['date'] == '2025-12-12'
        assert blocks[2]['date'] == '2025-12-13'
    
    def test_parse_fractional_hours(self):
        """Test parsing fractional hours like 7.5h"""
        text = """20251212 7.5h
工作内容"""
        
        blocks = parse_date_block(text)
        assert blocks[0]['hours'] == 7.5


class TestEntryCategorization:
    """Tests for entry categorization logic"""
    
    def test_categorize_project_default(self):
        """Default category should be 'project'"""
        entry = "完成O类文档生产环境部署"
        assert categorize_entry(entry) == 'project'
    
    def test_categorize_research_poc(self):
        """PoC keyword should categorize as 'research'"""
        entry = "完成新算法PoC验证"
        assert categorize_entry(entry) == 'research'
    
    def test_categorize_research_diaoyan(self):
        """调研 keyword should categorize as 'research'"""
        entry = "进行技术调研"
        assert categorize_entry(entry) == 'research'
    
    def test_categorize_service(self):
        """服务化 keyword should categorize as 'service'"""
        entry = "完成模块服务化改造"
        assert categorize_entry(entry) == 'service'
    
    def test_categorize_service_interface(self):
        """接口化 keyword should categorize as 'service'"""
        entry = "完成接口化设计"
        assert categorize_entry(entry) == 'service'
    
    def test_categorize_temporary_work(self):
        """临时工作 should categorize as 'other_affairs'"""
        entry = "临时工作：处理紧急问题"
        assert categorize_entry(entry) == 'other_affairs'
    
    def test_categorize_ops_work(self):
        """运维 work should categorize as 'other_affairs'"""
        entry = "处理服务器运维问题"
        assert categorize_entry(entry) == 'other_affairs'
    
    def test_categorize_meeting(self):
        """会议 should categorize as 'other_affairs'"""
        entry = "参加项目评审会议"
        assert categorize_entry(entry) == 'other_affairs'
    
    def test_categorize_tech_sharing(self):
        """技术分享 should categorize as 'other_affairs'"""
        entry = "进行技术分享"
        assert categorize_entry(entry) == 'other_affairs'
    
    def test_categorize_paper_sharing(self):
        """论文分享 should categorize as 'other_affairs'"""
        entry = "论文分享会"
        assert categorize_entry(entry) == 'other_affairs'


class TestDeduplication:
    """Tests for entry deduplication"""
    
    def test_exact_duplicate_removal(self):
        """Exact duplicates should be removed"""
        entries = ["完成部署", "完成部署", "修复问题"]
        result = deduplicate_entries(entries)
        assert len(result) == 2
    
    def test_substring_removal(self):
        """Substring entries should be removed"""
        entries = ["完成部署工作任务", "完成部署工作"]
        result = deduplicate_entries(entries)
        # The shorter one is a substring of the longer, should be deduplicated
        assert len(result) == 1
    
    def test_empty_input(self):
        """Empty input should return empty list"""
        result = deduplicate_entries([])
        assert result == []


class TestFullParsing:
    """Integration tests for full parsing pipeline"""
    
    def test_parse_and_categorize_complete(self):
        """Test complete parsing and categorization"""
        text = """20251211 8h
完成O类文档生产环境部署
进行技术调研

20251212 8h
临时工作：处理紧急问题
完成服务化改造
参加项目会议"""
        
        result = parse_and_categorize(text)
        
        assert 'blocks' in result
        assert 'categories' in result
        assert 'week_range' in result
        
        cats = result['categories']
        assert 'project' in cats
        assert 'research' in cats
        assert 'service' in cats
        assert 'other_affairs' in cats
        
        # Check categorization
        assert any('调研' in e for e in cats['research'])
        assert any('服务化' in e for e in cats['service'])
        assert any('会议' in e for e in cats['other_affairs'])


class TestWeekRange:
    """Tests for week range calculation"""
    
    def test_week_range_format(self):
        """Week range should return valid dates"""
        monday, friday = get_current_week_range()
        
        assert monday.weekday() == 0  # Monday
        assert friday.weekday() == 4  # Friday
        
        monday_str = format_date(monday)
        friday_str = format_date(friday)
        
        # Check format YYYY-MM-DD
        assert len(monday_str) == 10
        assert monday_str[4] == '-'
        assert monday_str[7] == '-'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
