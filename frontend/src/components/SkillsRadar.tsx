import React, { useState, useEffect } from 'react';
import apiService, { Skill, SkillsStats, WorkItem } from '../services/api';
import './SkillsRadar.css';

const SkillsRadar: React.FC = () => {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [stats, setStats] = useState<SkillsStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  
  // 技能详情模态框
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [skillWorkItems, setSkillWorkItems] = useState<WorkItem[]>([]);
  const [loadingWorkItems, setLoadingWorkItems] = useState<boolean>(false);
  const [showSkillModal, setShowSkillModal] = useState<boolean>(false);
  
  // 智能分类状态
  const [categorizing, setCategorizing] = useState<boolean>(false);
  const [categorizeMessage, setCategorizeMessage] = useState<string>('');

  useEffect(() => {
    loadData();
  }, []);

  // 过滤无效技能的辅助函数
  const isValidSkill = (skill: Skill): boolean => {
    if (!skill.name) return false;
    const lowerName = skill.name.toLowerCase();
    return !['null', 'none', '待补充', ''].includes(lowerName);
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [skillsRes, statsRes] = await Promise.all([
        apiService.getSkills(),
        apiService.getSkillsStats()
      ]);
      
      if (skillsRes.success && skillsRes.data) {
        // 前端额外过滤无效技能
        const validSkills = skillsRes.data.filter(isValidSkill);
        setSkills(validSkills);
      }
      if (statsRes.success && statsRes.data) {
        // 过滤 top_skills 中的无效数据
        const filteredStats = {
          ...statsRes.data,
          top_skills: (statsRes.data.top_skills || []).filter(
            (s: {name: string, count: number}) => 
              s.name && !['null', 'none', '待补充'].includes(s.name.toLowerCase())
          )
        };
        setStats(filteredStats);
      }
    } catch (err) {
      setError('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 点击技能加载相关工作条目
  const handleSkillClick = async (skill: Skill) => {
    setSelectedSkill(skill);
    setShowSkillModal(true);
    setLoadingWorkItems(true);
    
    try {
      const response = await apiService.getWorkItemsBySkill(skill.name);
      if (response.success && response.data) {
        setSkillWorkItems(response.data);
      }
    } catch (err) {
      setError('加载工作条目失败');
    } finally {
      setLoadingWorkItems(false);
    }
  };

  const closeSkillModal = () => {
    setShowSkillModal(false);
    setSelectedSkill(null);
    setSkillWorkItems([]);
  };

  // 使用 LLM 智能分类所有技能
  const handleSmartCategorize = async () => {
    if (categorizing) return;
    
    setCategorizing(true);
    setCategorizeMessage('正在使用 AI 智能分类技能...');
    setError('');
    
    try {
      const response = await apiService.recategorizeSkillsWithLLM();
      if (response.success) {
        setCategorizeMessage(`✓ 智能分类完成！更新了 ${response.updated_count || 0} 个技能`);
        // 重新加载数据
        await loadData();
        // 3秒后清除消息
        setTimeout(() => setCategorizeMessage(''), 3000);
      } else {
        setError(response.message || '智能分类失败');
        setCategorizeMessage('');
      }
    } catch (err) {
      setError('智能分类请求失败');
      setCategorizeMessage('');
    } finally {
      setCategorizing(false);
    }
  };

  const getCategoryColor = (category?: string) => {
    switch (category) {
      case 'tech': return '#007aff';
      case 'soft': return '#34c759';
      case 'domain': return '#ff9500';
      default: return '#8e8e93';
    }
  };

  const getCategoryLabel = (category?: string) => {
    switch (category) {
      case 'tech': return '技术技能';
      case 'soft': return '软技能';
      case 'domain': return '业务领域';
      default: return '其他';
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('zh-CN', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const maxCount = skills.length > 0 ? Math.max(...skills.map(s => s.count)) : 1;

  // 修复分类过滤逻辑
  const filteredSkills = (() => {
    if (selectedCategory === 'all') {
      return skills;
    } else if (selectedCategory === 'other') {
      // "其他" 分类：category 为 null、undefined 或空
      return skills.filter(s => !s.category || s.category === '');
    } else {
      // 指定分类：精确匹配
      return skills.filter(s => s.category === selectedCategory);
    }
  })();

  // Calculate radar data for visualization
  const topSkills = stats?.top_skills.slice(0, 8) || [];
  const radarMax = topSkills.length > 0 ? Math.max(...topSkills.map(s => s.count)) : 1;


  return (
    <div className="skills-radar">
      {/* Header */}
      <div className="sr-header">
        <div className="sr-header-content">
          <h2>能力成长雷达</h2>
          <p className="sr-subtitle">追踪你的技能发展轨迹</p>
        </div>
      </div>

      {error && <div className="sr-error">{error}</div>}

      {loading ? (
        <div className="sr-loading">
          <div className="sr-loading-spinner"></div>
          <p>加载中...</p>
        </div>
      ) : (
        <>
          {/* Stats Overview */}
          <div className="sr-overview">
            <div className="sr-stat-card">
              <div className="sr-stat-icon">🎯</div>
              <div className="sr-stat-content">
                <div className="sr-stat-value">{stats?.total_unique || 0}</div>
                <div className="sr-stat-label">技能总数</div>
              </div>
            </div>
            
            {Object.entries(stats?.by_category || {}).map(([category, count]) => (
              <div key={category} className="sr-stat-card">
                <div 
                  className="sr-stat-icon" 
                  style={{ backgroundColor: `${getCategoryColor(category)}20` }}
                >
                  {category === 'tech' ? '💻' : category === 'soft' ? '🤝' : '📊'}
                </div>
                <div className="sr-stat-content">
                  <div className="sr-stat-value">{count}</div>
                  <div className="sr-stat-label">{getCategoryLabel(category)}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Main Content */}
          <div className="sr-main">
            {/* Radar Chart Area */}
            <div className="sr-radar-section">
              <div className="sr-section-header">
                <h3>技能分布</h3>
              </div>
              
              {topSkills.length > 0 ? (
                <div className="sr-radar-chart">
                  {/* Simple bar-based radar visualization */}
                  <div className="sr-radar-bars">
                    {topSkills.map((skill, index) => (
                      <div key={skill.name} className="sr-radar-bar-item">
                        <div className="sr-radar-bar-label">{skill.name}</div>
                        <div className="sr-radar-bar-track">
                          <div 
                            className="sr-radar-bar-fill"
                            style={{ 
                              width: `${(skill.count / radarMax) * 100}%`,
                              animationDelay: `${index * 0.05}s`
                            }}
                          />
                        </div>
                        <div className="sr-radar-bar-count">{skill.count}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="sr-empty">
                  <div className="sr-empty-icon">📊</div>
                  <p>暂无技能数据</p>
                  <p className="sr-empty-hint">通过智能提取工作项来积累技能标签</p>
                </div>
              )}
            </div>

            {/* Skills List */}
            <div className="sr-skills-section">
              <div className="sr-section-header">
                <div className="sr-section-title-row">
                  <h3>技能详情</h3>
                  <button 
                    className={`sr-smart-btn ${categorizing ? 'loading' : ''}`}
                    onClick={handleSmartCategorize}
                    disabled={categorizing}
                    title="使用 AI 智能分类所有技能"
                  >
                    {categorizing ? (
                      <>
                        <span className="sr-smart-spinner"></span>
                        分类中...
                      </>
                    ) : (
                      <>🤖 智能分类</>
                    )}
                  </button>
                </div>
                {categorizeMessage && (
                  <div className="sr-categorize-message">{categorizeMessage}</div>
                )}
                <div className="sr-filter">
                  <button 
                    className={`sr-filter-btn ${selectedCategory === 'all' ? 'active' : ''}`}
                    onClick={() => setSelectedCategory('all')}
                  >
                    全部
                  </button>
                  <button 
                    className={`sr-filter-btn ${selectedCategory === 'tech' ? 'active' : ''}`}
                    onClick={() => setSelectedCategory('tech')}
                  >
                    技术
                  </button>
                  <button 
                    className={`sr-filter-btn ${selectedCategory === 'soft' ? 'active' : ''}`}
                    onClick={() => setSelectedCategory('soft')}
                  >
                    软技能
                  </button>
                  <button 
                    className={`sr-filter-btn ${selectedCategory === 'domain' ? 'active' : ''}`}
                    onClick={() => setSelectedCategory('domain')}
                  >
                    业务
                  </button>
                  <button 
                    className={`sr-filter-btn ${selectedCategory === 'other' ? 'active' : ''}`}
                    onClick={() => setSelectedCategory('other')}
                  >
                    其他
                  </button>
                </div>
              </div>
              
              <div className="sr-skills-list">
                {filteredSkills.length > 0 ? (
                  filteredSkills.map(skill => (
                    <div 
                      key={skill.id} 
                      className="sr-skill-item sr-skill-clickable"
                      onClick={() => handleSkillClick(skill)}
                      title="点击查看相关工作内容"
                    >
                      <div className="sr-skill-main">
                        <div className="sr-skill-name">
                          <span 
                            className="sr-skill-dot"
                            style={{ backgroundColor: getCategoryColor(skill.category) }}
                          />
                          {skill.name}
                        </div>
                        <div className="sr-skill-progress">
                          <div 
                            className="sr-skill-progress-bar"
                            style={{ 
                              width: `${(skill.count / maxCount) * 100}%`,
                              backgroundColor: getCategoryColor(skill.category)
                            }}
                          />
                        </div>
                      </div>
                      <div className="sr-skill-meta">
                        <span className="sr-skill-count">{skill.count} 次</span>
                        <span className="sr-skill-date">
                          {formatDate(skill.first_used_date)} - {formatDate(skill.last_used_date)}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="sr-empty-list">
                    <p>暂无该类别的技能</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Growth Tips */}
          <div className="sr-tips">
            <div className="sr-tips-header">
              <span className="sr-tips-icon">💡</span>
              <h4>成长建议</h4>
            </div>
            <div className="sr-tips-content">
              {skills.length === 0 ? (
                <p>开始记录你的日常工作，系统会自动分析并积累你的技能标签。</p>
              ) : skills.length < 5 ? (
                <p>继续积累更多工作记录，让系统更全面地了解你的技能分布。</p>
              ) : (
                <p>
                  你已积累了 <strong>{stats?.total_unique}</strong> 项技能！
                  {topSkills[0] && (
                    <> 最常使用的是 <strong>{topSkills[0].name}</strong>，共出现 {topSkills[0].count} 次。</>
                  )}
                </p>
              )}
            </div>
          </div>
        </>
      )}

      {/* Skill Work Items Modal */}
      {showSkillModal && selectedSkill && (
        <div className="sr-modal-overlay" onClick={closeSkillModal}>
          <div className="sr-modal" onClick={e => e.stopPropagation()}>
            <div className="sr-modal-header">
              <h3>
                <span 
                  className="sr-skill-dot"
                  style={{ backgroundColor: getCategoryColor(selectedSkill.category) }}
                />
                {selectedSkill.name}
              </h3>
              <button className="sr-modal-close" onClick={closeSkillModal}>×</button>
            </div>
            <div className="sr-modal-meta">
              <span className="sr-modal-tag">{getCategoryLabel(selectedSkill.category)}</span>
              <span className="sr-modal-count">使用 {selectedSkill.count} 次</span>
            </div>
            <div className="sr-modal-body">
              {loadingWorkItems ? (
                <div className="sr-modal-loading">
                  <div className="sr-loading-spinner"></div>
                  <p>加载中...</p>
                </div>
              ) : skillWorkItems.length > 0 ? (
                <div className="sr-work-items">
                  {skillWorkItems.map(item => (
                    <div key={item.id} className="sr-work-item">
                      <div className="sr-work-item-header">
                        <span className="sr-work-item-date">{item.raw_log_date}</span>
                        {item.project_name && (
                          <span className="sr-work-item-project">{item.project_name}</span>
                        )}
                      </div>
                      {item.action && (
                        <p className="sr-work-item-action">{item.action}</p>
                      )}
                      {item.result_metric && (
                        <p className="sr-work-item-result">✓ {item.result_metric}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="sr-modal-empty">
                  <p>暂无相关工作记录</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SkillsRadar;
