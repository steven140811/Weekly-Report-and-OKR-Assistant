import React, { useState, useEffect, useCallback } from 'react';
import apiService, { WeeklyReportResponse, ValidationResult, DailyReport, WeekRange } from '../services/api';
import './WeeklyReportGenerator.css';

const WeeklyReportGenerator: React.FC = () => {
  const [dailyContent, setDailyContent] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<WeeklyReportResponse | null>(null);
  const [error, setError] = useState<string>('');
  
  // New states for enhanced features
  const [showDailyModal, setShowDailyModal] = useState<boolean>(false);
  const [weekRange, setWeekRange] = useState<WeekRange | null>(null);
  const [modalStartDate, setModalStartDate] = useState<string>('');
  const [modalEndDate, setModalEndDate] = useState<string>('');
  // Store the actual imported date range for report generation
  const [importedStartDate, setImportedStartDate] = useState<string>('');
  const [importedEndDate, setImportedEndDate] = useState<string>('');
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [selectedDates, setSelectedDates] = useState<string[]>([]);
  const [dailyReportsMap, setDailyReportsMap] = useState<Record<string, DailyReport>>({});
  const [loadingDailyReports, setLoadingDailyReports] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Load week range on mount
  useEffect(() => {
    loadWeekRange();
    loadAvailableDates();
  }, []);

  const loadWeekRange = async () => {
    try {
      const range = await apiService.getWeekRange();
      setWeekRange(range);
    } catch (err) {
      console.error('Failed to load week range:', err);
    }
  };

  const loadAvailableDates = async () => {
    try {
      const response = await apiService.getDailyReportDates();
      if (response.success && response.data) {
        setAvailableDates(response.data);
      }
    } catch (err) {
      console.error('Failed to load daily report dates:', err);
    }
  };

  // Load daily reports for date range
  const loadDailyReportsForRange = useCallback(async (startDate: string, endDate: string) => {
    setLoadingDailyReports(true);
    try {
      const response = await apiService.getDailyReportsByRange(startDate, endDate);
      if (response.success && response.data) {
        const map: Record<string, DailyReport> = {};
        response.data.forEach(report => {
          map[report.entry_date] = report;
        });
        setDailyReportsMap(map);
        // Pre-select all dates that have reports
        setSelectedDates(response.data.map(r => r.entry_date));
      }
    } catch (err) {
      console.error('Failed to load daily reports:', err);
    } finally {
      setLoadingDailyReports(false);
    }
  }, []);

  // Open modal and load data for current week by default
  const handleOpenDailyModal = () => {
    setShowDailyModal(true);
    if (weekRange) {
      setModalStartDate(weekRange.monday);
      setModalEndDate(weekRange.friday);
      loadDailyReportsForRange(weekRange.monday, weekRange.friday);
    }
  };

  // Handle date range change in modal
  const handleModalDateRangeChange = () => {
    if (modalStartDate && modalEndDate) {
      loadDailyReportsForRange(modalStartDate, modalEndDate);
    }
  };

  // Toggle date selection
  const toggleDateSelection = (date: string) => {
    setSelectedDates(prev => 
      prev.includes(date) 
        ? prev.filter(d => d !== date)
        : [...prev, date].sort()
    );
  };

  // Import selected daily reports
  const handleImportDailyReports = () => {
    const sortedDates = [...selectedDates].sort();
    const importedContent = sortedDates.map(date => {
      const report = dailyReportsMap[date];
      if (report) {
        // Format: YYYYMMDD 8h
        const dateFormatted = date.replace(/-/g, '');
        return `${dateFormatted} 8h\n${report.content}`;
      }
      return '';
    }).filter(Boolean).join('\n\n');

    // Store the imported date range for report generation
    setImportedStartDate(modalStartDate);
    setImportedEndDate(modalEndDate);
    
    setDailyContent(importedContent);
    setShowDailyModal(false);
  };

  // Generate dates for the selected range in modal
  const getModalDates = (): string[] => {
    if (!modalStartDate || !modalEndDate) return [];
    
    const dates: string[] = [];
    const start = new Date(modalStartDate);
    const end = new Date(modalEndDate);
    
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      dates.push(`${year}-${month}-${day}`);
    }
    
    return dates;
  };

  const formatDisplayDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return `${date.getMonth() + 1}月${date.getDate()}日 ${weekdays[date.getDay()]}`;
  };

  const handleGenerate = async () => {
    if (!dailyContent.trim()) {
      setError('请输入日报内容');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setSaveMessage(null);

    try {
      const response = await apiService.generateWeeklyReport(dailyContent);
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
    if (result?.report) {
      navigator.clipboard.writeText(result.report);
    }
  };

  // Save weekly report to database
  const handleSaveReport = async () => {
    if (!result?.report) return;
    
    // Use imported date range if available, otherwise use current week range
    const startDate = importedStartDate || weekRange?.monday;
    const endDate = importedEndDate || weekRange?.friday;
    
    if (!startDate || !endDate) return;

    setSaving(true);
    setSaveMessage(null);

    try {
      const response = await apiService.saveWeeklyReport(
        startDate,
        endDate,
        result.report
      );

      if (response.success) {
        setSaveMessage({ type: 'success', text: '周报保存成功！' });
      } else {
        setSaveMessage({ type: 'error', text: response.error || '保存失败' });
      }
    } catch (err) {
      setSaveMessage({ type: 'error', text: '保存失败，请检查网络连接' });
    } finally {
      setSaving(false);
    }
  };

  const renderValidation = (validation: ValidationResult) => {
    return (
      <div className="validation-result">
        <h4>验证结果</h4>
        <ul>
          <li className={validation.valid ? 'valid' : 'invalid'}>
            整体结构: {validation.valid ? '✓ 通过' : '✗ 不通过'}
          </li>
          <li className={validation.order_valid ? 'valid' : 'invalid'}>
            标题顺序: {validation.order_valid ? '✓ 正确' : '✗ 错误'}
          </li>
          {validation.missing_sections && validation.missing_sections.length > 0 && (
            <li className="invalid">
              缺少章节: {validation.missing_sections.join(', ')}
            </li>
          )}
        </ul>
      </div>
    );
  };

  const sampleInput = `20251211 8h
完成O类文档生产环境部署与联调
修复若干提取问题

20251212 8h
根据业务方准确率报告，排查I_C-I_E类文档准确率下降原因
临时工作：处理紧急服务器问题

20251213 8h
完成17服务器迁移
配置nexus私服与rsync
技术分享：深度学习模型优化

20251214 8h
继续优化准确率问题
进行技术调研

20251215 8h
完成服务化接口设计
进行项目会议`;

  const modalDates = getModalDates();

  return (
    <div className="generator-container">
      <h2>周报生成</h2>
      <p className="description">
        输入您的日报内容，系统将自动生成规范的周报邮件正文。
        支持格式：20251212 8h 或 2025-12-12 8h
      </p>

      {weekRange && (
        <div className="week-range-info">
          📅 本周范围: {weekRange.monday} ~ {weekRange.friday}
          {importedStartDate && importedEndDate && (importedStartDate !== weekRange.monday || importedEndDate !== weekRange.friday) && (
            <span className="imported-range">
              &nbsp;| 📝 已导入日期范围: {importedStartDate} ~ {importedEndDate}
            </span>
          )}
        </div>
      )}

      <div className="input-section">
        <div className="input-header">
          <label>日报内容</label>
          <div className="input-actions">
            <button 
              className="import-daily-btn"
              onClick={handleOpenDailyModal}
            >
              📥 从日报导入
            </button>
            <button 
              className="sample-btn"
              onClick={() => setDailyContent(sampleInput)}
            >
              填充示例
            </button>
          </div>
        </div>
        <textarea
          value={dailyContent}
          onChange={(e) => setDailyContent(e.target.value)}
          placeholder="请输入日报内容，每天以日期行开头（如：20251212 8h）"
          rows={12}
        />
        <div className="char-count">
          {dailyContent.length} / 20000 字符
        </div>
      </div>

      <button 
        className="generate-btn"
        onClick={handleGenerate}
        disabled={loading}
      >
        {loading ? '生成中...' : '生成周报'}
      </button>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {result?.success && result.report && (
        <div className="result-section">
          <div className="result-header">
            <h3>生成结果</h3>
            <div className="result-actions">
              <button className="copy-btn" onClick={handleCopy}>
                复制内容
              </button>
              <button 
                className="save-btn" 
                onClick={handleSaveReport}
                disabled={saving}
              >
                {saving ? '保存中...' : '💾 保存周报'}
              </button>
            </div>
          </div>

          {saveMessage && (
            <div className={`save-message ${saveMessage.type}`}>
              {saveMessage.text}
            </div>
          )}
          
          {result.validation && renderValidation(result.validation)}
          
          <pre className="report-content">
            {result.report}
          </pre>
        </div>
      )}

      {/* Daily Reports Selection Modal */}
      {showDailyModal && (
        <div className="modal-overlay" onClick={() => setShowDailyModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>选择日报</h3>
              <button className="modal-close" onClick={() => setShowDailyModal(false)}>×</button>
            </div>
            
            <div className="modal-body">
              {/* Date Range Selector */}
              <div className="date-range-selector">
                <div className="date-range-inputs">
                  <div className="date-input-group">
                    <label>开始日期:</label>
                    <input
                      type="date"
                      value={modalStartDate}
                      onChange={(e) => setModalStartDate(e.target.value)}
                    />
                  </div>
                  <div className="date-input-group">
                    <label>结束日期:</label>
                    <input
                      type="date"
                      value={modalEndDate}
                      onChange={(e) => setModalEndDate(e.target.value)}
                    />
                  </div>
                  <button 
                    className="btn-load-range"
                    onClick={handleModalDateRangeChange}
                    disabled={!modalStartDate || !modalEndDate}
                  >
                    加载日报
                  </button>
                </div>
                <p className="current-week-hint">
                  本周: {weekRange?.monday} ~ {weekRange?.friday}
                  <button 
                    className="btn-reset-week"
                    onClick={() => {
                      if (weekRange) {
                        setModalStartDate(weekRange.monday);
                        setModalEndDate(weekRange.friday);
                        loadDailyReportsForRange(weekRange.monday, weekRange.friday);
                      }
                    }}
                  >
                    重置为本周
                  </button>
                </p>
              </div>

              {loadingDailyReports ? (
                <div className="loading-text">加载中...</div>
              ) : (
                <>
                  <p className="modal-hint">
                    选择要导入的日报（当前范围: {modalStartDate} ~ {modalEndDate}）
                  </p>
                  <div className="daily-list">
                    {modalDates.map((date: string) => {
                      const hasReport = !!dailyReportsMap[date];
                      const isSelected = selectedDates.includes(date);
                      
                      return (
                        <div 
                          key={date}
                          className={`daily-item ${hasReport ? 'has-report' : 'no-report'} ${isSelected ? 'selected' : ''}`}
                          onClick={() => hasReport && toggleDateSelection(date)}
                        >
                          <div className="daily-item-header">
                            <input 
                              type="checkbox" 
                              checked={isSelected}
                              onChange={() => hasReport && toggleDateSelection(date)}
                              disabled={!hasReport}
                            />
                            <span className="daily-date">{formatDisplayDate(date)}</span>
                            {hasReport ? (
                              <span className="status-badge has">已录入</span>
                            ) : (
                              <span className="status-badge no">未录入</span>
                            )}
                          </div>
                          {hasReport && dailyReportsMap[date] && (
                            <div className="daily-preview">
                              {dailyReportsMap[date].content.substring(0, 100)}...
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </div>
            
            <div className="modal-footer">
              <button className="btn-cancel" onClick={() => setShowDailyModal(false)}>
                取消
              </button>
              <button 
                className="btn-confirm"
                onClick={handleImportDailyReports}
                disabled={selectedDates.length === 0}
              >
                导入 ({selectedDates.length}) 条日报
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WeeklyReportGenerator;
