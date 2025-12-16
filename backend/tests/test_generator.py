#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_generator.py - Tests for weekly report and OKR generation
"""

import pytest
import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator import (
    generate_weekly_report,
    generate_okr,
    validate_weekly_report,
    validate_okr
)


class TestWeeklyReportGeneration:
    """Tests for weekly report generation"""
    
    @pytest.fixture
    def sample_daily_report(self):
        return """20251211 8h
完成O类文档生产环境部署与联调
修复若干提取问题

20251212 8h
根据业务方准确率报告，排查I_C-I_E类文档准确率下降原因
临时工作：处理紧急服务器问题

20251213 8h
完成17服务器迁移
配置nexus私服与rsync
技术分享：深度学习模型优化"""
    
    def test_weekly_report_generation_mock(self, sample_daily_report):
        """Test weekly report generation with mock LLM"""
        result = generate_weekly_report(sample_daily_report, use_mock=True)
        
        assert result['success'] is True
        assert 'report' in result
        assert len(result['report']) > 0
    
    def test_weekly_report_structure(self, sample_daily_report):
        """Test that generated report has required structure"""
        result = generate_weekly_report(sample_daily_report, use_mock=True)
        report = result['report']
        
        # Check required sections exist
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
        
        for section in required_sections:
            assert section in report, f"Missing section: {section}"
    
    def test_weekly_report_date_range(self, sample_daily_report):
        """Test that report contains correct week date range"""
        result = generate_weekly_report(sample_daily_report, use_mock=True)
        report = result['report']
        
        # Check for date range pattern YYYY-MM-DD ~ YYYY-MM-DD
        date_pattern = r'周报（\d{4}-\d{2}-\d{2}\s*~\s*\d{4}-\d{2}-\d{2}）'
        assert re.search(date_pattern, report), "Week date range not found in report"
    
    def test_weekly_report_input_too_long(self):
        """Test input length validation"""
        long_content = "x" * 25000  # Exceeds MAX_INPUT_CHARS
        result = generate_weekly_report(long_content, use_mock=True)
        
        assert result['success'] is False
        assert '超过最大长度' in result['error']


class TestWeeklyReportValidation:
    """Tests for weekly report structure validation"""
    
    def test_valid_report(self):
        """Test validation of a correctly structured report"""
        valid_report = """周报（2025-12-09 ~ 2025-12-13）

本周一句话总结：本周完成了O类文档部署工作，需关注准确率下降问题。

1、手上项目、服务化能力建设、预研的主要进展

手上项目
- 完成O类文档生产环境部署

服务化能力建设
- 完成接口设计

预研
- 技术调研

2、是否有风险，哪些风险点？
- 资源紧张

3、其他的事务性工作
- 服务器迁移
- 技术分享

4、下周大概的计划
- 继续优化
- 完成测试"""
        
        validation = validate_weekly_report(valid_report)
        assert validation['valid'] is True
        assert len(validation['missing_sections']) == 0
        assert validation['order_valid'] is True
    
    def test_invalid_report_missing_sections(self):
        """Test validation catches missing sections"""
        incomplete_report = """周报（2025-12-09 ~ 2025-12-13）

本周一句话总结：完成部署工作。

1、手上项目、服务化能力建设、预研的主要进展

手上项目
- 完成部署"""
        
        validation = validate_weekly_report(incomplete_report)
        assert validation['valid'] is False
        assert len(validation['missing_sections']) > 0


class TestOKRGeneration:
    """Tests for OKR generation"""
    
    @pytest.fixture
    def sample_material(self):
        return """本周完成O类文档生产环境部署与联调，修复若干提取问题。
根据业务方准确率报告，排查I_C-I_E类文档准确率下降原因。
完成17服务器迁移，配置nexus私服与rsync。
下周计划：继续优化准确率，完成服务化改造。"""
    
    def test_okr_generation_mock(self, sample_material):
        """Test OKR generation with mock LLM"""
        result = generate_okr(sample_material, use_mock=True)
        
        assert result['success'] is True
        assert 'okr' in result
        assert len(result['okr']) > 0
    
    def test_okr_has_objectives(self, sample_material):
        """Test that generated OKR has 2-3 objectives"""
        result = generate_okr(sample_material, use_mock=True)
        okr = result['okr']
        
        # Count objectives
        objective_pattern = r'目标\s*O\d+'
        objectives = re.findall(objective_pattern, okr)
        
        assert 2 <= len(objectives) <= 3, f"Expected 2-3 objectives, found {len(objectives)}"
    
    def test_okr_has_date_nodes(self, sample_material):
        """Test that KRs have date nodes"""
        result = generate_okr(sample_material, use_mock=True)
        okr = result['okr']
        
        # Check for date pattern YYYY-MM-DD前
        date_pattern = r'\d{4}-\d{2}-\d{2}前'
        dates = re.findall(date_pattern, okr)
        
        assert len(dates) > 0, "No date nodes found in OKR"
    
    def test_okr_has_quantitative_expressions(self, sample_material):
        """Test that KRs have quantitative expressions"""
        result = generate_okr(sample_material, use_mock=True)
        okr = result['okr']
        
        # Check for quantitative patterns
        quant_patterns = [
            r'≥|>=|≤|<=',
            r'\d+%',
            r'准确率',
            r'覆盖',
            r'数量',
            r'上线',
            r'验收',
            r'性能',
            r'可用性'
        ]
        
        found = False
        for pattern in quant_patterns:
            if re.search(pattern, okr):
                found = True
                break
        
        assert found, "No quantitative expressions found in OKR"
    
    def test_okr_input_too_long(self):
        """Test input length validation"""
        long_content = "x" * 25000
        result = generate_okr(long_content, use_mock=True)
        
        assert result['success'] is False
        assert '超过最大长度' in result['error']


class TestOKRValidation:
    """Tests for OKR structure validation"""
    
    def test_valid_okr(self):
        """Test validation of a correctly structured OKR"""
        valid_okr = """2026第一季度OKR：

目标 O1：提升文档智能提取系统的准确率和稳定性
KR1：2026-01-31前完成根因分析，准确率回升至≥90%；2026-02-28前完成优化验证，准确率稳定在≥92%；2026-03-31前全类型平均准确率≥93%；
KR2：2026-02-15前完成监控告警体系搭建，覆盖100%核心接口；

目标 O2：推进服务化能力建设
KR1：2026-02-01前完成设计方案评审；2026-02-28前完成核心模块开发，覆盖≥80%功能；2026-03-31前完成全量上线；"""
        
        validation = validate_okr(valid_okr)
        
        assert validation['objectives_valid'] is True
        assert validation['has_date_nodes'] is True
        assert validation['has_quantitative'] is True
        assert validation['has_milestones'] is True
    
    def test_invalid_okr_no_objectives(self):
        """Test validation catches missing objectives"""
        invalid_okr = """2026第一季度OKR：
KR1：完成一些工作"""
        
        validation = validate_okr(invalid_okr)
        assert validation['objectives_valid'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
