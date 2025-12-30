/**
 * 导出功能工具函数
 * 支持导出为 CSV、Markdown、TXT 格式
 */

export type ExportFormat = 'csv' | 'md' | 'txt';

export interface ExportOptions {
  filename: string;
  format: ExportFormat;
  content: string;
}

/**
 * 将日报数据转换为指定格式
 */
export function formatDailyReport(date: string, content: string, format: ExportFormat): string {
  const formattedDate = new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  });

  switch (format) {
    case 'csv':
      // CSV格式：日期,内容
      const escapedContent = content.replace(/"/g, '""').replace(/\n/g, '\\n');
      return `"${date}","${formattedDate}","${escapedContent}"`;
    
    case 'md':
      return `# 日报 - ${formattedDate}\n\n${content}\n`;
    
    case 'txt':
      return `【日报】${formattedDate}\n${'='.repeat(40)}\n\n${content}\n`;
    
    default:
      return content;
  }
}

/**
 * 将周报数据转换为指定格式
 */
export function formatWeeklyReport(
  startDate: string,
  endDate: string,
  content: string,
  format: ExportFormat
): string {
  const formatDateStr = (d: string) => new Date(d).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const dateRange = `${formatDateStr(startDate)} - ${formatDateStr(endDate)}`;

  switch (format) {
    case 'csv':
      const escapedContent = content.replace(/"/g, '""').replace(/\n/g, '\\n');
      return `"${startDate}","${endDate}","${dateRange}","${escapedContent}"`;
    
    case 'md':
      return `# 周报\n\n**日期范围**: ${dateRange}\n\n---\n\n${content}\n`;
    
    case 'txt':
      return `【周报】${dateRange}\n${'='.repeat(50)}\n\n${content}\n`;
    
    default:
      return content;
  }
}

/**
 * 将OKR数据转换为指定格式
 */
export function formatOKR(
  quarter: string,
  content: string,
  format: ExportFormat
): string {
  switch (format) {
    case 'csv':
      const escapedContent = content.replace(/"/g, '""').replace(/\n/g, '\\n');
      return `"${quarter}","${escapedContent}"`;
    
    case 'md':
      return `# OKR - ${quarter}\n\n${content}\n`;
    
    case 'txt':
      return `【OKR】${quarter}\n${'='.repeat(40)}\n\n${content}\n`;
    
    default:
      return content;
  }
}

/**
 * 获取文件扩展名
 */
export function getFileExtension(format: ExportFormat): string {
  return format;
}

/**
 * 获取MIME类型
 */
export function getMimeType(format: ExportFormat): string {
  switch (format) {
    case 'csv':
      return 'text/csv;charset=utf-8';
    case 'md':
      return 'text/markdown;charset=utf-8';
    case 'txt':
      return 'text/plain;charset=utf-8';
    default:
      return 'text/plain;charset=utf-8';
  }
}

/**
 * 触发文件下载
 */
export function downloadFile(filename: string, content: string, format: ExportFormat): void {
  const mimeType = getMimeType(format);
  const blob = new Blob(['\ufeff' + content], { type: mimeType }); // 添加 BOM 以支持中文
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.${getFileExtension(format)}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * 批量导出日报
 */
export function exportDailyReports(
  reports: Array<{ date: string; content: string }>,
  format: ExportFormat,
  filename: string = 'daily_reports'
): void {
  let content = '';
  
  if (format === 'csv') {
    content = '"日期","格式化日期","内容"\n';
    content += reports.map(r => formatDailyReport(r.date, r.content, format)).join('\n');
  } else {
    content = reports.map(r => formatDailyReport(r.date, r.content, format)).join('\n\n---\n\n');
  }
  
  downloadFile(filename, content, format);
}

/**
 * 导出单个周报
 */
export function exportWeeklyReport(
  startDate: string,
  endDate: string,
  content: string,
  format: ExportFormat,
  filename?: string
): void {
  const defaultFilename = `weekly_report_${startDate}_${endDate}`;
  const formattedContent = formatWeeklyReport(startDate, endDate, content, format);
  downloadFile(filename || defaultFilename, formattedContent, format);
}

/**
 * 导出OKR
 */
export function exportOKR(
  quarter: string,
  content: string,
  format: ExportFormat,
  filename?: string
): void {
  const defaultFilename = `okr_${quarter.replace(/\s/g, '_')}`;
  const formattedContent = formatOKR(quarter, content, format);
  downloadFile(filename || defaultFilename, formattedContent, format);
}

export default {
  formatDailyReport,
  formatWeeklyReport,
  formatOKR,
  downloadFile,
  exportDailyReports,
  exportWeeklyReport,
  exportOKR,
};
