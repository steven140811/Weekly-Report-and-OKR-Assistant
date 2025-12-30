import React, { useState, useEffect } from 'react';
import DailyReportEntry from './components/DailyReportEntry';
import WeeklyReportGenerator from './components/WeeklyReportGenerator';
import WeeklyReportQuery from './components/WeeklyReportQuery';
import OKRGenerator from './components/OKRGenerator';
import CareerAssets from './components/CareerAssets';
import SkillsRadar from './components/SkillsRadar';
import apiService, { HealthResponse } from './services/api';
import './App.css';

// Get version from package.json
const APP_VERSION = process.env.REACT_APP_VERSION || '0.6.0';

type TabType = 'daily-entry' | 'weekly-report' | 'weekly-query' | 'okr' | 'career-assets' | 'skills-radar';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('daily-entry');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string>('');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await apiService.healthCheck();
        setHealth(response);
        setHealthError('');
      } catch (err) {
        setHealthError('无法连接到后端服务，请确保后端已启动');
      }
    };
    checkHealth();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>WorkPilot 效能助手</h1>
        <p className="App-subtitle">
          基于 LLM 的智能日报/周报/OKR/职业资产管理工具
        </p>
        {health && (
          <div className={`status-badge ${health.llm_configured ? 'configured' : 'not-configured'}`}>
            {health.llm_configured ? 'LLM 已配置' : 'LLM 未配置 (使用模拟模式)'}
          </div>
        )}
        {healthError && (
          <div className="health-error">
            {healthError}
          </div>
        )}
      </header>

      <nav className="tab-nav">
        <button
          className={`tab-btn ${activeTab === 'daily-entry' ? 'active' : ''}`}
          onClick={() => setActiveTab('daily-entry')}
        >
          📅 日报录入
        </button>
        <button
          className={`tab-btn ${activeTab === 'weekly-report' ? 'active' : ''}`}
          onClick={() => setActiveTab('weekly-report')}
        >
          📋 周报生成
        </button>
        <button
          className={`tab-btn ${activeTab === 'weekly-query' ? 'active' : ''}`}
          onClick={() => setActiveTab('weekly-query')}
        >
          🔍 周报查询
        </button>
        <button
          className={`tab-btn ${activeTab === 'okr' ? 'active' : ''}`}
          onClick={() => setActiveTab('okr')}
        >
          🎯 OKR 生成
        </button>
        <button
          className={`tab-btn ${activeTab === 'career-assets' ? 'active' : ''}`}
          onClick={() => setActiveTab('career-assets')}
        >
          💼 简历积木
        </button>
        <button
          className={`tab-btn ${activeTab === 'skills-radar' ? 'active' : ''}`}
          onClick={() => setActiveTab('skills-radar')}
        >
          📊 能力雷达
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'daily-entry' && <DailyReportEntry />}
        {activeTab === 'weekly-report' && <WeeklyReportGenerator />}
        {activeTab === 'weekly-query' && <WeeklyReportQuery />}
        {activeTab === 'okr' && <OKRGenerator />}
        {activeTab === 'career-assets' && <CareerAssets />}
        {activeTab === 'skills-radar' && <SkillsRadar />}
      </main>

      <footer className="App-footer">
        <p>
          WorkPilot v{APP_VERSION} | 
          最大输入长度: {health?.max_input_chars || 20000} 字符
        </p>
      </footer>
    </div>
  );
}

export default App;
