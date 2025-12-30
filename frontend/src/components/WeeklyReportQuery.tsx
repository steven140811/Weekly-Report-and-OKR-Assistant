import React, { useState, useEffect } from 'react';
import apiService, { WeeklyReport } from '../services/api';
import { ExportFormat, exportWeeklyReport } from '../utils/export';
import ExportButton from './ExportButton';
import './WeeklyReportQuery.css';

const WeeklyReportQuery: React.FC = () => {
  const [reports, setReports] = useState<WeeklyReport[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchStartDate, setSearchStartDate] = useState<string>('');
  const [searchEndDate, setSearchEndDate] = useState<string>('');
  
  // Editor states
  const [editingReport, setEditingReport] = useState<WeeklyReport | null>(null);
  const [editContent, setEditContent] = useState<string>('');
  const [saving, setSaving] = useState<boolean>(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Load all reports on mount
  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    try {
      const response = await apiService.getAllWeeklyReports();
      if (response.success && response.data) {
        setReports(response.data);
      }
    } catch (error) {
      console.error('Failed to load weekly reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchStartDate && !searchEndDate) {
      loadReports();
      return;
    }

    if (searchStartDate && searchEndDate) {
      setLoading(true);
      try {
        const response = await apiService.getWeeklyReportByDate(searchStartDate, searchEndDate);
        if (response.success) {
          if (response.data) {
            setReports([response.data]);
          } else {
            setReports([]);
          }
        }
      } catch (error) {
        console.error('Failed to search weekly reports:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEdit = (report: WeeklyReport) => {
    setEditingReport(report);
    setEditContent(report.content);
    setMessage(null);
  };

  const handleCancelEdit = () => {
    setEditingReport(null);
    setEditContent('');
    setMessage(null);
  };

  const handleSave = async () => {
    if (!editingReport) return;

    setSaving(true);
    setMessage(null);

    try {
      const response = await apiService.saveWeeklyReport(
        editingReport.start_date,
        editingReport.end_date,
        editContent
      );

      if (response.success) {
        setMessage({ type: 'success', text: '周报保存成功！' });
        // Update local state
        setReports(prev => prev.map(r => 
          r.start_date === editingReport.start_date && r.end_date === editingReport.end_date
            ? { ...r, content: editContent }
            : r
        ));
        // Exit edit mode after short delay
        setTimeout(() => {
          setEditingReport(null);
          setEditContent('');
          setMessage(null);
        }, 1500);
      } else {
        setMessage({ type: 'error', text: response.error || '保存失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '保存失败，请检查网络连接' });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (report: WeeklyReport) => {
    if (!window.confirm(`确定要删除 ${report.start_date} ~ ${report.end_date} 的周报吗？`)) {
      return;
    }

    try {
      const response = await apiService.deleteWeeklyReport(report.start_date, report.end_date);
      if (response.success) {
        setReports(prev => prev.filter(r => 
          !(r.start_date === report.start_date && r.end_date === report.end_date)
        ));
        if (editingReport?.start_date === report.start_date && editingReport?.end_date === report.end_date) {
          handleCancelEdit();
        }
      }
    } catch (error) {
      console.error('Failed to delete weekly report:', error);
    }
  };

  const handleCopy = () => {
    if (editContent) {
      navigator.clipboard.writeText(editContent);
      setMessage({ type: 'success', text: '内容已复制到剪贴板' });
      setTimeout(() => setMessage(null), 2000);
    }
  };

  const formatDateRange = (startDate: string, endDate: string): string => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    return `${start.getMonth() + 1}月${start.getDate()}日 - ${end.getMonth() + 1}月${end.getDate()}日`;
  };

  const getPreview = (content: string): string => {
    const firstLine = content.split('\n').find(line => line.trim()) || '';
    return firstLine.length > 60 ? firstLine.substring(0, 60) + '...' : firstLine;
  };

  return (
    <div className="weekly-report-query">
      <h2>📋 周报查询</h2>

      {/* Search Section */}
      <div className="query-section">
        <div className="query-form">
          <div className="form-group">
            <label>周开始日期</label>
            <input
              type="date"
              value={searchStartDate}
              onChange={(e) => setSearchStartDate(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>周结束日期</label>
            <input
              type="date"
              value={searchEndDate}
              onChange={(e) => setSearchEndDate(e.target.value)}
            />
          </div>
          <button className="query-btn" onClick={handleSearch} disabled={loading}>
            {loading ? '查询中...' : '🔍 查询'}
          </button>
          <button 
            className="query-btn" 
            onClick={() => {
              setSearchStartDate('');
              setSearchEndDate('');
              loadReports();
            }}
            style={{ background: '#6c757d' }}
          >
            显示全部
          </button>
        </div>
      </div>

      {/* Reports List */}
      <div className="reports-list-section">
        <div className="section-header">
          <h3>历史周报</h3>
          <span className="report-count">共 {reports.length} 份周报</span>
        </div>

        {loading ? (
          <div className="loading-overlay">加载中...</div>
        ) : reports.length === 0 ? (
          <div className="empty-message">暂无周报记录</div>
        ) : (
          <table className="reports-table">
            <thead>
              <tr>
                <th className="date-cell">日期范围</th>
                <th className="preview-cell">内容预览</th>
                <th>创建时间</th>
                <th className="actions-cell">操作</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((report) => (
                <tr key={`${report.start_date}-${report.end_date}`}>
                  <td className="date-cell">
                    {formatDateRange(report.start_date, report.end_date)}
                  </td>
                  <td className="preview-cell" title={report.content.substring(0, 200)}>
                    {getPreview(report.content)}
                  </td>
                  <td>{report.created_at?.split('T')[0] || '-'}</td>
                  <td className="actions-cell">
                    <button 
                      className="action-btn edit"
                      onClick={() => handleEdit(report)}
                    >
                      编辑
                    </button>
                    <button 
                      className="action-btn delete"
                      onClick={() => handleDelete(report)}
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Editor Section */}
      {editingReport && (
        <div className="editor-section">
          <div className="editor-header">
            <h3>
              ✏️ 编辑周报 - 
              <span className="editor-date-range">
                {formatDateRange(editingReport.start_date, editingReport.end_date)}
              </span>
            </h3>
            <div className="editor-actions">
              <ExportButton 
                onExport={(format) => exportWeeklyReport(
                  editingReport.start_date,
                  editingReport.end_date,
                  editContent,
                  format
                )}
              />
              <button className="btn btn-secondary" onClick={handleCopy}>
                复制
              </button>
              <button className="btn btn-secondary" onClick={handleCancelEdit}>
                取消
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? '保存中...' : '保存修改'}
              </button>
            </div>
          </div>

          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}

          <div className="stats-info">
            <div className="stat-item">
              <span className="label">开始日期: </span>
              {editingReport.start_date}
            </div>
            <div className="stat-item">
              <span className="label">结束日期: </span>
              {editingReport.end_date}
            </div>
            <div className="stat-item">
              <span className="label">字符数: </span>
              {editContent.length}
            </div>
          </div>

          <textarea
            className="report-textarea"
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            placeholder="周报内容..."
          />
        </div>
      )}
    </div>
  );
};

export default WeeklyReportQuery;
