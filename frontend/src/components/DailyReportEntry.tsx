import React, { useState, useEffect, useCallback } from 'react';
import apiService from '../services/api';
import './DailyReportEntry.css';

interface DailyReportEntryProps {}

const DailyReportEntry: React.FC<DailyReportEntryProps> = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [content, setContent] = useState('');
  const [reportDates, setReportDates] = useState<string[]>([]);
  const [reportCache, setReportCache] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];

  // Format date to YYYY-MM-DD
  const formatDate = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // Format date for display
  const formatDisplayDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
  };

  // Get current month/year display
  const getMonthYearDisplay = (): string => {
    return `${currentDate.getFullYear()}年${currentDate.getMonth() + 1}月`;
  };

  // Load all report dates - called on mount and when coming back to this tab
  const loadReportDates = useCallback(async () => {
    try {
      const response = await apiService.getDailyReportDates();
      if (response.success && response.data) {
        setReportDates(response.data);
        return response.data;
      }
    } catch (error) {
      console.error('Failed to load report dates:', error);
    }
    return [];
  }, []);

  // Initialize component - only run once on mount
  useEffect(() => {
    const initializeComponent = async () => {
      // Clear cache and reload fresh data every time component mounts
      setReportCache({});
      await loadReportDates();
      const today = formatDate(new Date());
      setSelectedDate(today);
      // Load today's report without using cache
      setLoading(true);
      try {
        const response = await apiService.getDailyReport(today);
        if (response.success) {
          const reportContent = response.data?.content || '';
          setContent(reportContent);
          setReportCache({ [today]: reportContent });
        }
      } catch (error) {
        console.error('Failed to load report:', error);
      } finally {
        setLoading(false);
      }
    };
    
    initializeComponent();
  }, []); // Empty dependency array - only run on mount

  // Handle date selection - directly load the report for selected date
  const handleDateSelect = async (dateStr: string) => {
    if (dateStr === selectedDate) return; // Already selected
    
    setSelectedDate(dateStr);
    setMessage(null);
    
    // Load report for the selected date
    setLoading(true);
    try {
      const response = await apiService.getDailyReport(dateStr);
      if (response.success) {
        const reportContent = response.data?.content || '';
        setContent(reportContent);
        setReportCache(prev => ({ ...prev, [dateStr]: reportContent }));
      }
    } catch (error) {
      console.error('Failed to load report:', error);
      setMessage({ type: 'error', text: '加载日报失败' });
    } finally {
      setLoading(false);
    }
  };

  // Handle save
  const handleSave = async () => {
    if (!selectedDate) return;

    setSaving(true);
    setMessage(null);

    try {
      const response = await apiService.saveDailyReport(selectedDate, content);
      if (response.success) {
        setMessage({ type: 'success', text: '日报保存成功！' });
        // Update cache
        setReportCache(prev => ({ ...prev, [selectedDate]: content }));
        // Refresh report dates
        if (content.trim() && !reportDates.includes(selectedDate)) {
          setReportDates(prev => [...prev, selectedDate].sort().reverse());
        }
      } else {
        setMessage({ type: 'error', text: response.error || '保存失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '保存失败，请检查网络连接' });
    } finally {
      setSaving(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!selectedDate || !window.confirm('确定要删除这天的日报吗？')) return;

    try {
      const response = await apiService.deleteDailyReport(selectedDate);
      if (response.success) {
        setMessage({ type: 'success', text: '日报已删除' });
        setContent('');
        setReportCache(prev => {
          const newCache = { ...prev };
          delete newCache[selectedDate];
          return newCache;
        });
        setReportDates(prev => prev.filter(d => d !== selectedDate));
      } else {
        setMessage({ type: 'error', text: response.error || '删除失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '删除失败' });
    }
  };

  // Navigate months
  const navigateMonth = (direction: number) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  // Go to today
  const goToToday = () => {
    setCurrentDate(new Date());
    const today = formatDate(new Date());
    handleDateSelect(today);
  };

  // Generate calendar days
  const generateCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // First day of month
    const firstDay = new Date(year, month, 1);
    const startingDay = firstDay.getDay();
    
    // Last day of month
    const lastDay = new Date(year, month + 1, 0);
    const totalDays = lastDay.getDate();

    const days: (number | null)[] = [];
    
    // Add empty cells for days before first of month
    for (let i = 0; i < startingDay; i++) {
      days.push(null);
    }
    
    // Add days of month
    for (let i = 1; i <= totalDays; i++) {
      days.push(i);
    }

    return days;
  };

  const calendarDays = generateCalendarDays();
  const today = formatDate(new Date());

  // Template for new daily report
  const insertTemplate = () => {
    const template = `## 今日工作
- 

## 遇到的问题
- 

## 明日计划
- 
`;
    setContent(template);
  };

  return (
    <div className="daily-report-entry">
      <h2>📅 日报录入</h2>
      
      <div className="stats-bar">
        <div className="stat-item">
          本月已录入: <span className="count">
            {reportDates.filter(d => d.startsWith(`${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`)).length}
          </span> 篇
        </div>
        <div className="stat-item">
          总计: <span className="count">{reportDates.length}</span> 篇
        </div>
      </div>

      <div className="calendar-container">
        <div className="calendar-header">
          <h3>{getMonthYearDisplay()}</h3>
          <div className="calendar-nav">
            <button onClick={() => navigateMonth(-1)}>◀ 上月</button>
            <button onClick={goToToday}>今天</button>
            <button onClick={() => navigateMonth(1)}>下月 ▶</button>
          </div>
        </div>

        <div className="calendar-grid">
          {weekdays.map(day => (
            <div key={day} className="calendar-weekday">{day}</div>
          ))}
          
          {calendarDays.map((day, index) => {
            if (day === null) {
              return <div key={`empty-${index}`} className="calendar-day empty" />;
            }

            const dateStr = formatDate(new Date(currentDate.getFullYear(), currentDate.getMonth(), day));
            const isToday = dateStr === today;
            const isSelected = dateStr === selectedDate;
            const hasReport = reportDates.includes(dateStr);

            return (
              <div
                key={dateStr}
                className={`calendar-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''} ${hasReport ? 'has-report' : ''}`}
                onClick={() => handleDateSelect(dateStr)}
              >
                <div className="day-number">{day}</div>
                {hasReport && (
                  <>
                    <div className="day-indicator">✓</div>
                    {reportCache[dateStr] && (
                      <div className="day-preview">
                        {reportCache[dateStr].substring(0, 50)}...
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {selectedDate && (
        <div className="report-editor">
          <div className="editor-header">
            <h3>
              📝 <span className="editor-date">{formatDisplayDate(selectedDate)}</span> 的日报
            </h3>
            <div className="editor-actions">
              <button className="btn btn-secondary template-btn" onClick={insertTemplate}>
                插入模板
              </button>
              {reportDates.includes(selectedDate) && (
                <button className="btn btn-danger" onClick={handleDelete}>
                  删除
                </button>
              )}
              <button 
                className="btn btn-primary" 
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? '保存中...' : '保存日报'}
              </button>
            </div>
          </div>

          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}

          {loading ? (
            <div className="loading-overlay">加载中...</div>
          ) : (
            <textarea
              className="report-textarea"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="在这里输入今天的工作内容...

支持的格式示例：
- 完成了XXX功能开发
- 修复了XXX问题
- 参加了XXX会议"
            />
          )}
        </div>
      )}

      {!selectedDate && (
        <div className="placeholder-text">
          请在日历中选择一个日期开始录入日报
        </div>
      )}
    </div>
  );
};

export default DailyReportEntry;
