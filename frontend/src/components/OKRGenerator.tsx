import React, { useState, useEffect } from 'react';
import apiService, { OKRResponse, ValidationResult, OKRReport } from '../services/api';
import { ExportFormat, exportOKR } from '../utils/export';
import ExportButton from './ExportButton';
import './OKRGenerator.css';

const OKRGenerator: React.FC = () => {
  // Tab state
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate');
  
  // Generate tab states
  const [content, setContent] = useState<string>('');
  const [nextQuarter, setNextQuarter] = useState<string>('2026第一季度');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<OKRResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [saving, setSaving] = useState<boolean>(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // History tab states
  const [okrList, setOkrList] = useState<OKRReport[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);
  const [selectedOKR, setSelectedOKR] = useState<OKRReport | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editContent, setEditContent] = useState<string>('');
  const [updateMessage, setUpdateMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Load OKR history when switching to history tab
  useEffect(() => {
    if (activeTab === 'history') {
      loadOKRHistory();
    }
  }, [activeTab]);

  const loadOKRHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await apiService.getAllOKRReports();
      if (response.success && response.data) {
        setOkrList(response.data);
      }
    } catch (err) {
      console.error('加载OKR历史失败', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleGenerate = async () => {
    if (!content.trim()) {
      setError('请输入历史材料内容');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setSaveMessage(null);

    try {
      const response = await apiService.generateOKR(content, nextQuarter);
      setResult(response);
      if (!response.success) {
        setError(response.error || '生成失败');
      }
    } catch (err) {
      setError('网络错误，请检查后端服务是否启动');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result?.okr) {
      navigator.clipboard.writeText(result.okr);
    }
  };

  const handleSave = async () => {
    if (!result?.okr) return;

    setSaving(true);
    setSaveMessage(null);

    try {
      const today = new Date().toISOString().split('T')[0];
      const response = await apiService.saveOKRReport(today, result.okr);

      if (response.success) {
        setSaveMessage({ type: 'success', text: 'OKR保存成功！' });
        // Reload history if on history tab
        if (activeTab === 'history') {
          loadOKRHistory();
        }
      } else {
        setSaveMessage({ type: 'error', text: response.error || '保存失败' });
      }
    } catch (err) {
      setSaveMessage({ type: 'error', text: '保存失败，请检查网络连接' });
    } finally {
      setSaving(false);
    }
  };

  // History tab handlers
  const handleViewOKR = (okr: OKRReport) => {
    setSelectedOKR(okr);
    setEditContent(okr.content);
    setIsEditing(false);
    setUpdateMessage(null);
  };

  const handleEditOKR = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    if (selectedOKR) {
      setEditContent(selectedOKR.content);
    }
    setIsEditing(false);
    setUpdateMessage(null);
  };

  const handleUpdateOKR = async () => {
    if (!selectedOKR || !editContent.trim()) return;

    try {
      const response = await apiService.updateOKRReport(selectedOKR.creation_date, editContent);
      if (response.success) {
        setUpdateMessage({ type: 'success', text: 'OKR更新成功！' });
        setIsEditing(false);
        // Update local state
        setSelectedOKR({ ...selectedOKR, content: editContent });
        // Reload list
        loadOKRHistory();
      } else {
        setUpdateMessage({ type: 'error', text: response.error || '更新失败' });
      }
    } catch (err) {
      setUpdateMessage({ type: 'error', text: '更新失败，请检查网络连接' });
    }
  };

  const handleDeleteOKR = async (creationDate: string) => {
    if (!window.confirm('确定要删除这个OKR吗？')) return;

    try {
      const response = await apiService.deleteOKRReport(creationDate);
      if (response.success) {
        // Close detail view if deleted item was selected
        if (selectedOKR?.creation_date === creationDate) {
          setSelectedOKR(null);
        }
        // Reload list
        loadOKRHistory();
      } else {
        alert(response.error || '删除失败');
      }
    } catch (err) {
      alert('删除失败，请检查网络连接');
    }
  };

  const handleCloseDetail = () => {
    setSelectedOKR(null);
    setIsEditing(false);
    setUpdateMessage(null);
  };

  const renderValidation = (validation: ValidationResult) => {
    return (
      <div className="okr-validation-result">
        <h4>验证结果</h4>
        <ul>
          <li className={validation.objectives_valid ? 'valid' : 'invalid'}>
            目标数量: {validation.objective_count} 个 ({validation.objectives_valid ? '✓ 符合要求(2-3个)' : '✗ 不符合要求'})
          </li>
          <li className={validation.has_date_nodes ? 'valid' : 'invalid'}>
            日期节点: {validation.date_nodes_count} 个 ({validation.has_date_nodes ? '✓ 存在' : '✗ 缺失'})
          </li>
          <li className={validation.has_quantitative ? 'valid' : 'invalid'}>
            量化表达: {validation.has_quantitative ? '✓ 存在' : '✗ 缺失'}
            {validation.quantitative_expressions && validation.quantitative_expressions.length > 0 && (
              <span className="details"> ({validation.quantitative_expressions.slice(0, 3).join(', ')})</span>
            )}
          </li>
          <li className={validation.has_milestones ? 'valid' : 'warning'}>
            阶段里程碑: {validation.has_milestones ? '✓ 存在' : '⚠ 未检测到多阶段节点'}
          </li>
        </ul>
      </div>
    );
  };

  const sampleInput = `周报内容摘要：
本周完成O类文档生产环境部署与联调，修复若干提取问题。
根据业务方准确率报告，排查I_C-I_E类文档准确率下降原因。
完成17服务器迁移，配置nexus私服与rsync。
技术分享：深度学习模型优化。

下周计划：
- 继续修复I_C-I_E准确率问题
- 监控O类生产环境运行稳定性
- 完善服务器配置与运维文档
- 推进服务化改造设计

风险点：
- 资源紧张：准确率修复与新功能并行
- 依赖外部LLM服务的可用性
- 公网访问开通需要工单审批`;

  const quarterOptions = [
    '2025第四季度',
    '2026第一季度',
    '2026第二季度',
    '2026第三季度',
    '2026第四季度',
  ];

  return (
    <div className="okr-generator-container">
      <h2>OKR 管理</h2>
      
      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'generate' ? 'active' : ''}`}
          onClick={() => setActiveTab('generate')}
        >
          生成 OKR
        </button>
        <button 
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          历史 OKR
        </button>
      </div>

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <div className="generate-tab">
          <p className="description">
            输入历史周报、月报或项目材料，系统将自动生成下一季度的OKR。
            每个KR将包含日期节点和量化指标，关键KR包含阶段里程碑。
          </p>

          <div className="quarter-selector">
            <label>目标季度:</label>
            <select 
              value={nextQuarter}
              onChange={(e) => setNextQuarter(e.target.value)}
            >
              {quarterOptions.map(q => (
                <option key={q} value={q}>{q}</option>
              ))}
            </select>
          </div>

          <div className="input-section">
            <div className="input-header">
              <label>历史材料内容</label>
              <button 
                className="sample-btn"
                onClick={() => setContent(sampleInput)}
              >
                填充示例
              </button>
            </div>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="请输入历史周报、月报、项目材料等内容..."
              rows={12}
            />
            <div className="char-count">
              {content.length} / 20000 字符
            </div>
          </div>

          <button 
            className="generate-btn"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? '生成中...' : '生成 OKR'}
          </button>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {result?.success && result.okr && (
            <div className="result-section">
              <div className="result-header">
                <h3>生成结果</h3>
                <div className="result-actions">
                  <ExportButton 
                    onExport={(format) => exportOKR(nextQuarter, result.okr!, format)}
                  />
                  <button className="copy-btn" onClick={handleCopy}>
                    复制内容
                  </button>
                  <button 
                    className="save-btn" 
                    onClick={handleSave}
                    disabled={saving}
                  >
                    {saving ? '保存中...' : '💾 保存OKR'}
                  </button>
                </div>
              </div>

              {saveMessage && (
                <div className={`save-message ${saveMessage.type}`}>
                  {saveMessage.text}
                </div>
              )}
              
              {result.validation && renderValidation(result.validation)}
              
              <pre className="okr-content">
                {result.okr}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="history-tab">
          <div className="history-header">
            <h3>已保存的 OKR</h3>
            <button className="refresh-btn" onClick={loadOKRHistory} disabled={loadingHistory}>
              {loadingHistory ? '加载中...' : '🔄 刷新'}
            </button>
          </div>

          {loadingHistory ? (
            <div className="loading-message">加载中...</div>
          ) : okrList.length === 0 ? (
            <div className="empty-message">
              <p>暂无保存的OKR记录</p>
              <p className="hint">在"生成 OKR"页签中生成并保存OKR后，可以在此查看</p>
            </div>
          ) : (
            <div className="history-content">
              <div className="okr-list">
                {okrList.map((okr) => (
                  <div 
                    key={okr.creation_date} 
                    className={`okr-item ${selectedOKR?.creation_date === okr.creation_date ? 'selected' : ''}`}
                    onClick={() => handleViewOKR(okr)}
                  >
                    <div className="okr-item-date">
                      📅 {okr.creation_date}
                    </div>
                    <div className="okr-item-preview">
                      {okr.content.substring(0, 100)}...
                    </div>
                    <div className="okr-item-actions">
                      <button 
                        className="delete-btn-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteOKR(okr.creation_date);
                        }}
                      >
                        🗑️ 删除
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {selectedOKR && (
                <div className="okr-detail">
                  <div className="detail-header">
                    <div>
                      <h3>OKR 详情</h3>
                      <p className="detail-date">创建日期: {selectedOKR.creation_date}</p>
                    </div>
                    <div className="detail-actions">
                      {!isEditing ? (
                        <>
                          <ExportButton 
                            onExport={(format) => exportOKR(
                              selectedOKR.creation_date,
                              selectedOKR.content,
                              format
                            )}
                          />
                          <button className="edit-btn" onClick={handleEditOKR}>
                            ✏️ 编辑
                          </button>
                          <button className="close-btn" onClick={handleCloseDetail}>
                            ✕
                          </button>
                        </>
                      ) : (
                        <>
                          <button className="save-edit-btn" onClick={handleUpdateOKR}>
                            💾 保存
                          </button>
                          <button className="cancel-edit-btn" onClick={handleCancelEdit}>
                            取消
                          </button>
                        </>
                      )}
                    </div>
                  </div>

                  {updateMessage && (
                    <div className={`update-message ${updateMessage.type}`}>
                      {updateMessage.text}
                    </div>
                  )}

                  {isEditing ? (
                    <textarea
                      className="edit-textarea"
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      rows={20}
                    />
                  ) : (
                    <pre className="okr-content">
                      {selectedOKR.content}
                    </pre>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default OKRGenerator;
