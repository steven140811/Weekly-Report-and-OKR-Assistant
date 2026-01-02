#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py - Configuration management for the Weekly Report and OKR Assistant
"""

import os
from dotenv import load_dotenv

load_dotenv()


# 数据库配置缓存（避免循环导入）
_db_config_cache = None
_db_config_loaded = False


def _load_db_config():
    """从数据库加载 LLM 配置（延迟加载避免循环导入）"""
    global _db_config_cache, _db_config_loaded
    
    if _db_config_loaded:
        return _db_config_cache
    
    try:
        from database import get_config
        _db_config_cache = get_config('llm')
        _db_config_loaded = True
    except Exception:
        _db_config_cache = None
        _db_config_loaded = True
    
    return _db_config_cache


def reload_db_config():
    """强制重新加载数据库配置"""
    global _db_config_cache, _db_config_loaded
    _db_config_loaded = False
    return _load_db_config()


class Config:
    """Application configuration loaded from environment variables"""
    
    # LLM Configuration
    LLM_API_URL = os.getenv('LLM_API_URL', '').strip()
    LLM_API_KEY = os.getenv('LLM_API_KEY', '').strip()
    LLM_MODEL = os.getenv('LLM_MODEL', 'default/deepseek-v3-2')
    LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '30'))
    LLM_RETRY = int(os.getenv('LLM_RETRY', '2'))
    LLM_TEMPERATURE = 0  # Fixed per spec
    
    # DeepSeek API Configuration (optional, for direct DeepSeek integration)
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '').strip()
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com').strip()
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat').strip()
    
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
        """Return LLM configuration as dictionary, prioritizing database config"""
        # 首先检查数据库配置
        db_config = _load_db_config()
        if db_config and db_config.get('api_url') and db_config.get('api_key'):
            return {
                'api_url': db_config.get('api_url', ''),
                'api_key': db_config.get('api_key', ''),
                'model': db_config.get('model', cls.LLM_MODEL),
                'timeout': cls.LLM_TIMEOUT,
                'retry': cls.LLM_RETRY,
                'temperature': cls.LLM_TEMPERATURE,
                'use_deepseek': False
            }
        
        # 检查是否配置了 DeepSeek API
        if cls.DEEPSEEK_API_KEY:
            return {
                'api_url': cls.DEEPSEEK_BASE_URL,
                'api_key': cls.DEEPSEEK_API_KEY,
                'model': cls.DEEPSEEK_MODEL,
                'timeout': cls.LLM_TIMEOUT,
                'retry': cls.LLM_RETRY,
                'temperature': cls.LLM_TEMPERATURE,
                'use_deepseek': True
            }
        
        # 回退到通用 LLM 配置
        return {
            'api_url': cls.LLM_API_URL,
            'api_key': cls.LLM_API_KEY,
            'model': cls.LLM_MODEL,
            'timeout': cls.LLM_TIMEOUT,
            'retry': cls.LLM_RETRY,
            'temperature': cls.LLM_TEMPERATURE,
            'use_deepseek': False
        }
    
    @classmethod
    def is_llm_configured(cls):
        """Check if LLM is properly configured (from database or environment)"""
        # 首先检查数据库配置
        db_config = _load_db_config()
        if db_config and db_config.get('api_url') and db_config.get('api_key'):
            return True
        
        # 检查 DeepSeek API 配置
        if cls.DEEPSEEK_API_KEY:
            return True
        
        # 回退到通用 LLM 配置
        return bool(cls.LLM_API_URL and cls.LLM_API_KEY)
