import React, { useState } from 'react';
import { ExportFormat } from '../utils/export';
import './ExportButton.css';

interface ExportButtonProps {
  onExport: (format: ExportFormat) => void;
  disabled?: boolean;
  label?: string;
}

const ExportButton: React.FC<ExportButtonProps> = ({ 
  onExport, 
  disabled = false,
  label = '导出'
}) => {
  const [showMenu, setShowMenu] = useState(false);

  const handleExport = (format: ExportFormat) => {
    onExport(format);
    setShowMenu(false);
  };

  return (
    <div className="export-button-container">
      <button 
        className="btn btn-secondary export-btn"
        onClick={() => setShowMenu(!showMenu)}
        disabled={disabled}
      >
        📤 {label}
      </button>
      
      {showMenu && (
        <div className="export-menu">
          <button 
            className="export-menu-item"
            onClick={() => handleExport('csv')}
          >
            📊 导出为 CSV
          </button>
          <button 
            className="export-menu-item"
            onClick={() => handleExport('md')}
          >
            📝 导出为 Markdown
          </button>
          <button 
            className="export-menu-item"
            onClick={() => handleExport('txt')}
          >
            📄 导出为 TXT
          </button>
        </div>
      )}
      
      {showMenu && (
        <div 
          className="export-menu-overlay"
          onClick={() => setShowMenu(false)}
        />
      )}
    </div>
  );
};

export default ExportButton;
