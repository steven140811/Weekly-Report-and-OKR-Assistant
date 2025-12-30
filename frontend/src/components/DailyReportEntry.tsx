import React, { useState, useEffect, useCallback } from 'react';
import apiService, { TodoItem } from '../services/api';
import { getHoliday, Holiday } from '../utils/holidays';
import { ExportFormat, exportDailyReports } from '../utils/export';
import ExportButton from './ExportButton';
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
  
  // TODO Tips states
  const [todoItems, setTodoItems] = useState<TodoItem[]>([]);
  const [newTodoContent, setNewTodoContent] = useState('');
  const [loadingTodos, setLoadingTodos] = useState(false);

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

  // Load all report dates and their contents - called on mount
  const loadReportDatesAndContents = useCallback(async () => {
    try {
      const response = await apiService.getDailyReportDates();
      if (response.success && response.data) {
        const dates = response.data;
        setReportDates(dates);
        
        // Load content for all dates to populate the cache
        const cacheData: Record<string, string> = {};
        await Promise.all(
          dates.map(async (dateStr: string) => {
            try {
              const reportResponse = await apiService.getDailyReport(dateStr);
              if (reportResponse.success && reportResponse.data?.content) {
                cacheData[dateStr] = reportResponse.data.content;
              }
            } catch (error) {
              console.error(`Failed to load report for ${dateStr}:`, error);
            }
          })
        );
        setReportCache(cacheData);
        return { dates, cache: cacheData };
      }
    } catch (error) {
      console.error('Failed to load report dates:', error);
    }
    return { dates: [], cache: {} };
  }, []);

  // Initialize component - only run once on mount
  useEffect(() => {
    const initializeComponent = async () => {
      // Clear cache and reload fresh data every time component mounts
      setReportCache({});
      const { cache } = await loadReportDatesAndContents();
      const today = formatDate(new Date());
      setSelectedDate(today);
      // Set today's content from cache or load it
      if (cache[today]) {
        setContent(cache[today]);
      } else {
        setLoading(true);
        try {
          const response = await apiService.getDailyReport(today);
          if (response.success) {
            const reportContent = response.data?.content || '';
            setContent(reportContent);
            setReportCache(prev => ({ ...prev, [today]: reportContent }));
          }
        } catch (error) {
          console.error('Failed to load report:', error);
        } finally {
          setLoading(false);
        }
      }
    };
    
    initializeComponent();
  }, []); // Empty dependency array - only run on mount

  // Load TODO items
  const loadTodoItems = useCallback(async () => {
    setLoadingTodos(true);
    try {
      const response = await apiService.getTodoItems();
      if (response.success && response.data) {
        setTodoItems(response.data);
      }
    } catch (error) {
      console.error('Failed to load TODO items:', error);
    } finally {
      setLoadingTodos(false);
    }
  }, []);

  // Load TODO items on mount
  useEffect(() => {
    loadTodoItems();
  }, [loadTodoItems]);

  // Add new TODO item
  const handleAddTodo = async () => {
    if (!newTodoContent.trim()) return;
    
    try {
      const response = await apiService.createTodoItem(newTodoContent.trim());
      console.log('Create TODO response:', response);
      if (response.success && response.data) {
        setTodoItems(prev => [...prev, response.data!]);
        setNewTodoContent('');
      } else {
        console.error('Failed to create TODO:', response.error);
        alert(`创建 TODO 失败: ${response.error || '未知错误'}`);
      }
    } catch (error) {
      console.error('Failed to create TODO item:', error);
      alert(`创建 TODO 失败: ${error}`);
    }
  };

  // Toggle TODO completion
  const handleToggleTodo = async (id: number, currentCompleted: number) => {
    try {
      const response = await apiService.updateTodoItem(id, { completed: currentCompleted === 0 });
      if (response.success && response.data) {
        setTodoItems(prev => prev.map(item => item.id === id ? response.data! : item));
      }
    } catch (error) {
      console.error('Failed to update TODO item:', error);
    }
  };

  // Delete TODO item
  const handleDeleteTodo = async (id: number) => {
    try {
      const response = await apiService.deleteTodoItem(id);
      if (response.success) {
        setTodoItems(prev => prev.filter(item => item.id !== id));
      }
    } catch (error) {
      console.error('Failed to delete TODO item:', error);
    }
  };

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

      <div className="main-content-area">
        {/* TODO Tips Panel */}
        <div className="todo-tips-panel">
          <div className="todo-tips-header">
            <h4>📝 TODO Tips</h4>
          </div>
          <div className="todo-tips-body">
            <div className="todo-input-area">
              <input
                type="text"
                className="todo-input"
                value={newTodoContent}
                onChange={(e) => setNewTodoContent(e.target.value)}
                placeholder="添加新的 TODO..."
                onKeyPress={(e) => e.key === 'Enter' && handleAddTodo()}
              />
              <button className="btn btn-primary todo-add-btn" onClick={handleAddTodo}>
                +
              </button>
            </div>
            
            {loadingTodos ? (
              <div className="todo-loading">加载中...</div>
            ) : (
              <ul className="todo-list">
                {todoItems.map(item => (
                  <li key={item.id} className={`todo-item ${item.completed ? 'completed' : ''}`}>
                    <input
                      type="checkbox"
                      checked={item.completed === 1}
                      onChange={() => handleToggleTodo(item.id, item.completed)}
                      className="todo-checkbox"
                    />
                    <span className="todo-content">{item.content}</span>
                    <button
                      className="todo-delete-btn"
                      onClick={() => handleDeleteTodo(item.id)}
                      title="删除"
                    >
                      ×
                    </button>
                  </li>
                ))}
                {todoItems.length === 0 && (
                  <li className="todo-empty">暂无 TODO 项</li>
                )}
              </ul>
            )}
          </div>
        </div>

        {/* Calendar Container */}
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
          {weekdays.map((day, index) => (
            <div 
              key={day} 
              className={`calendar-weekday ${index === 0 || index === 6 ? 'weekend' : ''}`}
            >
              {day}
            </div>
          ))}
          
          {calendarDays.map((day, index) => {
            if (day === null) {
              return <div key={`empty-${index}`} className="calendar-day empty" />;
            }

            const dateObj = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
            const dateStr = formatDate(dateObj);
            const isToday = dateStr === today;
            const isSelected = dateStr === selectedDate;
            const hasReport = reportDates.includes(dateStr);
            const dayOfWeek = dateObj.getDay();
            const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
            const holiday = getHoliday(dateObj);

            return (
              <div
                key={dateStr}
                className={`calendar-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''} ${hasReport ? 'has-report' : ''} ${isWeekend ? 'weekend' : ''} ${holiday ? 'has-holiday' : ''}`}
                onClick={() => handleDateSelect(dateStr)}
                title={holiday ? holiday.name : undefined}
              >
                <div className="day-header">
                  <div className="day-number">{day}</div>
                  {holiday && (
                    <div className="day-holiday" title={holiday.name}>
                      <span className="holiday-emoji">{holiday.emoji}</span>
                    </div>
                  )}
                </div>
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
      </div> {/* End main-content-area */}

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
              {content.trim() && (
                <ExportButton 
                  label="导出当前"
                  onExport={(format) => exportDailyReports(
                    [{ date: selectedDate, content }],
                    format,
                    `daily_report_${selectedDate}`
                  )}
                />
              )}
              {reportDates.length > 0 && (
                <ExportButton 
                  label="导出全部"
                  onExport={(format) => {
                    const reports = reportDates
                      .filter(d => reportCache[d])
                      .map(d => ({ date: d, content: reportCache[d] }));
                    exportDailyReports(reports, format, 'all_daily_reports');
                  }}
                />
              )}
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
