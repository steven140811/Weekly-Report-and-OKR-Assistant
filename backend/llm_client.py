#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llm_client.py - LLM API client with retry and timeout handling
"""

import time
import logging
import requests
from typing import Optional, Dict, Any
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMClient:
    """Client for OpenAI-like chat completions API"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize LLM client.
        
        Args:
            config: Optional config dict, defaults to Config.get_llm_config()
        """
        self.config = config or Config.get_llm_config()
        self.api_url = self.config.get('api_url', '').rstrip('/')
        self.api_key = self.config.get('api_key', '')
        self.model = self.config.get('model', 'default/deepseek-v3-2')
        self.timeout = self.config.get('timeout', 30)
        self.retry = self.config.get('retry', 2)
        self.temperature = self.config.get('temperature', 0)
    
    def is_configured(self) -> bool:
        """Check if LLM client is properly configured"""
        return bool(self.api_url and self.api_key)
    
    def call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call LLM API with retry and exponential backoff.
        
        Args:
            prompt: User message/prompt
            system_prompt: Optional system message
            
        Returns:
            LLM response content string
            
        Raises:
            RuntimeError: If LLM is not configured
            Exception: If all retries fail
        """
        if not self.is_configured():
            raise RuntimeError('LLM_API_URL or LLM_API_KEY not configured')
        
        url = f"{self.api_url}/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': self.temperature
        }
        
        headers = {
            'Authorization': f"Bearer {self.api_key}",
            'Content-Type': 'application/json'
        }
        
        last_error = None
        
        for attempt in range(self.retry + 1):
            try:
                logger.info(f"LLM API call attempt {attempt + 1}/{self.retry + 1}")
                
                resp = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                resp.raise_for_status()
                
                data = resp.json()
                choices = data.get('choices', [])
                
                if choices:
                    msg = choices[0].get('message', {})
                    content = msg.get('content', '') or choices[0].get('text', '') or ''
                    logger.info(f"LLM API call successful, response length: {len(content)}")
                    return content
                
                return ''
                
            except Exception as e:
                last_error = e
                logger.warning(f"LLM API call attempt {attempt + 1} failed: {e}")
                
                if attempt < self.retry:
                    # Exponential backoff: 1s, 2s, 4s...
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        raise last_error or Exception("LLM API call failed after all retries")


# Mock LLM client for testing/demo without real API
class MockLLMClient:
    """Mock LLM client that returns predefined responses for testing"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def is_configured(self) -> bool:
        return True
    
    def call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Return mock response based on prompt content"""
        
        # Combine prompt and system_prompt for checking
        combined = prompt + (system_prompt or '')
        
        # Check if this is an OKR request (check first - more specific)
        # The OKR system prompt contains "OKR生成助手"
        if 'OKR生成助手' in combined or '生成{}'.format('OKR') in prompt:
            return self._mock_okr(prompt)
        
        # Check if this is a weekly report request
        if '周报生成助手' in combined or '周报' in prompt:
            return self._mock_weekly_report(prompt)
        
        # Fallback checks
        if 'OKR' in combined or 'okr' in combined.lower():
            return self._mock_okr(prompt)
        
        return "Mock response: 收到您的请求，这是模拟响应。"
    
    def _mock_weekly_report(self, prompt: str) -> str:
        """Generate mock weekly report"""
        # Extract week range from prompt if possible
        import re
        from parser import get_current_week_range, format_date
        
        monday, friday = get_current_week_range()
        monday_str = format_date(monday)
        friday_str = format_date(friday)
        
        return f"""周报（{monday_str} ~ {friday_str}）

本周一句话总结：本周完成了O类文档生产环境部署和服务器迁移配置工作，需关注I_C-I_E类文档准确率下降问题。

1、手上项目、服务化能力建设、预研的主要进展

手上项目
- 完成O类文档生产环境部署与联调，修复若干提取问题
- 根据业务方准确率报告，排查I_C-I_E类文档准确率下降原因

服务化能力建设

预研

2、是否有风险，哪些风险点？
- 资源紧张：准确率修复与新功能并行开发，建议优先级排序并集中资源
- I_C-I_E准确率下降原因未明确，需进一步定位根因

3、其他的事务性工作
- 完成17服务器迁移，配置nexus私服与rsync同步
- 完成服务器公网访问工单申请

4、下周大概的计划
- 继续排查并修复I_C-I_E准确率问题
- 监控O类生产环境运行稳定性
- 完善服务器配置与运维文档"""
    
    def _mock_okr(self, prompt: str) -> str:
        """Generate mock OKR"""
        return """2026第一季度OKR：

目标 O1：提升文档智能提取系统的准确率和稳定性
KR1：2026-01-31前完成I_C-I_E类文档准确率问题根因分析，准确率回升至≥90%；2026-02-28前完成优化验证，准确率稳定在≥92%；2026-03-31前全类型文档平均准确率≥93%；
KR2：2026-02-15前完成生产环境监控告警体系搭建，覆盖100%核心接口；2026-03-31前系统可用性≥99.5%；
KR3：2026-01-15前完成性能基准测试，2026-02-28前优化响应时间≤2秒（P95）；

目标 O2：推进服务化能力建设与基础设施优化
KR1：2026-02-01前完成服务接口化改造设计方案评审；2026-02-28前完成核心模块接口化开发，覆盖≥80%功能；2026-03-31前完成全量上线与文档交付；
KR2：2026-01-20前完成服务器环境标准化配置，覆盖100%生产节点；2026-03-15前完成自动化部署流程，部署时间缩短≥50%；"""


def get_llm_client(use_mock: bool = False) -> LLMClient:
    """
    Get appropriate LLM client based on configuration.
    
    Args:
        use_mock: Force use of mock client
        
    Returns:
        LLMClient or MockLLMClient instance
    """
    if use_mock or not Config.is_llm_configured():
        logger.info("Using MockLLMClient (LLM not configured or mock requested)")
        return MockLLMClient()
    
    return LLMClient()
