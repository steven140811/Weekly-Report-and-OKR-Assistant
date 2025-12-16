import React, { useState } from 'react';
import apiService, { WeeklyReportResponse, ValidationResult } from '../services/api';
import './WeeklyReportGenerator.css';

const WeeklyReportGenerator: React.FC = () => {
  const [dailyContent, setDailyContent] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<WeeklyReportResponse | null>(null);
  const [error, setError] = useState<string>('');

  const handleGenerate = async () => {
    if (!dailyContent.trim()) {
      setError('请输入日报内容');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

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

  return (
    <div className="generator-container">
      <h2>周报生成</h2>
      <p className="description">
        输入您的日报内容，系统将自动生成规范的周报邮件正文。
        支持格式：20251212 8h 或 2025-12-12 8h
      </p>

      <div className="input-section">
        <div className="input-header">
          <label>日报内容</label>
          <button 
            className="sample-btn"
            onClick={() => setDailyContent(sampleInput)}
          >
            填充示例
          </button>
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
            <button className="copy-btn" onClick={handleCopy}>
              复制内容
            </button>
          </div>
          
          {result.validation && renderValidation(result.validation)}
          
          <pre className="report-content">
            {result.report}
          </pre>
        </div>
      )}
    </div>
  );
};

export default WeeklyReportGenerator;
