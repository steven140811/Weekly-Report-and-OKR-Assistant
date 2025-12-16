#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py - Configuration management for the Weekly Report and OKR Assistant
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables"""
    
    # LLM Configuration
    LLM_API_URL = os.getenv('LLM_API_URL', '').strip()
    LLM_API_KEY = os.getenv('LLM_API_KEY', '').strip()
    LLM_MODEL = os.getenv('LLM_MODEL', 'default/deepseek-v3-2')
    LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '30'))
    LLM_RETRY = int(os.getenv('LLM_RETRY', '2'))
    LLM_TEMPERATURE = 0  # Fixed per spec
    
    # Application Configuration
    MAX_INPUT_CHARS = 20000  # Fixed per spec
    WEEK_MODE = 'current_week'  # Fixed per spec
    
    # Classification Keywords (frozen, extensible)
    KEYWORDS_RESEARCH = ['PoC', '调研']
    KEYWORDS_SERVICE = ['服务化', '接口化']
    
    # Keywords for "Other Affairs" category (Section 3)
    KEYWORDS_TEMPORARY = ['临时工作']
    KEYWORDS_OPS = ['运维', '权限', '工单', '服务器', '迁移', '配置', '公网访问']
    KEYWORDS_ADMIN = ['会议', '沟通', '统计', '填报', '分享', '支持', '论文分享', '技术分享']
    
    @classmethod
    def get_llm_config(cls):
        """Return LLM configuration as dictionary"""
        return {
            'api_url': cls.LLM_API_URL,
            'api_key': cls.LLM_API_KEY,
            'model': cls.LLM_MODEL,
            'timeout': cls.LLM_TIMEOUT,
            'retry': cls.LLM_RETRY,
            'temperature': cls.LLM_TEMPERATURE
        }
    
    @classmethod
    def is_llm_configured(cls):
        """Check if LLM is properly configured"""
        return bool(cls.LLM_API_URL and cls.LLM_API_KEY)
