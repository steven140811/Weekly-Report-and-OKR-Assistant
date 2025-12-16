import React, { useState, useEffect } from 'react';
import WeeklyReportGenerator from './components/WeeklyReportGenerator';
import OKRGenerator from './components/OKRGenerator';
import apiService, { HealthResponse } from './services/api';
import './App.css';

// Get version from package.json
const APP_VERSION = process.env.REACT_APP_VERSION || '0.4.0';

type TabType = 'weekly-report' | 'okr';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('weekly-report');
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
        <h1>周报 & OKR 生成助手</h1>
        <p className="App-subtitle">
          基于 LLM 的智能周报和 OKR 生成工具
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
          className={`tab-btn ${activeTab === 'weekly-report' ? 'active' : ''}`}
          onClick={() => setActiveTab('weekly-report')}
        >
          📋 周报生成
        </button>
        <button
          className={`tab-btn ${activeTab === 'okr' ? 'active' : ''}`}
          onClick={() => setActiveTab('okr')}
        >
          🎯 OKR 生成
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'weekly-report' && <WeeklyReportGenerator />}
        {activeTab === 'okr' && <OKRGenerator />}
      </main>

      <footer className="App-footer">
        <p>
          Weekly Report & OKR Assistant v{APP_VERSION} | 
          最大输入长度: {health?.max_input_chars || 20000} 字符
        </p>
      </footer>
    </div>
  );
}

export default App;
