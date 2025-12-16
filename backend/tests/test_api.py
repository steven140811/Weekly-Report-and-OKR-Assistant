#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_api.py - Tests for Flask API endpoints
"""

import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint returns expected structure"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'llm_configured' in data
        assert 'max_input_chars' in data


class TestWeekRangeEndpoint:
    """Tests for week range endpoint"""
    
    def test_get_week_range(self, client):
        """Test week range endpoint returns valid dates"""
        response = client.get('/api/week-range')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'monday' in data
        assert 'friday' in data
        
        # Check date format YYYY-MM-DD
        assert len(data['monday']) == 10
        assert len(data['friday']) == 10


class TestParseEndpoint:
    """Tests for parse endpoint"""
    
    def test_parse_success(self, client):
        """Test successful parsing"""
        response = client.post(
            '/api/parse',
            json={'content': '20251212 8h\n完成部署工作'}
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
    
    def test_parse_missing_content(self, client):
        """Test error when content is missing"""
        response = client.post('/api/parse', json={})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False


class TestWeeklyReportEndpoint:
    """Tests for weekly report generation endpoint"""
    
    def test_generate_weekly_report(self, client):
        """Test weekly report generation"""
        content = """20251211 8h
完成O类文档生产环境部署
修复若干提取问题

20251212 8h
临时工作：处理紧急问题
技术分享会"""
        
        response = client.post(
            '/api/generate/weekly-report',
            json={'content': content}
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'report' in data
        assert 'validation' in data
    
    def test_generate_weekly_report_missing_content(self, client):
        """Test error when content is missing"""
        response = client.post('/api/generate/weekly-report', json={})
        assert response.status_code == 400


class TestOKREndpoint:
    """Tests for OKR generation endpoint"""
    
    def test_generate_okr(self, client):
        """Test OKR generation"""
        content = """本周完成O类文档生产环境部署与联调。
下周计划：继续优化准确率。"""
        
        response = client.post(
            '/api/generate/okr',
            json={'content': content}
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'okr' in data
        assert 'validation' in data
    
    def test_generate_okr_with_quarter(self, client):
        """Test OKR generation with custom quarter"""
        response = client.post(
            '/api/generate/okr',
            json={
                'content': '历史材料内容',
                'next_quarter': '2026第二季度'
            }
        )
        assert response.status_code == 200


class TestValidationEndpoints:
    """Tests for validation endpoints"""
    
    def test_validate_weekly_report(self, client):
        """Test weekly report validation"""
        report = """周报（2025-12-09 ~ 2025-12-13）

本周一句话总结：完成部署工作。

1、手上项目、服务化能力建设、预研的主要进展

手上项目
- 完成部署

服务化能力建设

预研

2、是否有风险，哪些风险点？
- 暂无

3、其他的事务性工作
- 会议

4、下周大概的计划
- 继续工作"""
        
        response = client.post(
            '/api/validate/weekly-report',
            json={'report': report}
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'validation' in data
    
    def test_validate_okr(self, client):
        """Test OKR validation"""
        okr = """目标 O1：提升系统稳定性
KR1：2026-01-31前完成优化，准确率≥90%；"""
        
        response = client.post(
            '/api/validate/okr',
            json={'okr': okr}
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'validation' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
