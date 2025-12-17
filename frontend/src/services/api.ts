const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export interface WeekRange {
  monday: string;
  friday: string;
}

export interface ParsedData {
  blocks: Array<{
    date: string | null;
    hours: number;
    content: string[];
  }>;
  categories: {
    project: string[];
    service: string[];
    research: string[];
    other_affairs: string[];
  };
  week_range: WeekRange;
}

export interface ValidationResult {
  valid: boolean;
  missing_sections?: string[];
  order_valid?: boolean;
  objective_count?: number;
  objectives_valid?: boolean;
  date_nodes_count?: number;
  has_date_nodes?: boolean;
  quantitative_expressions?: string[];
  has_quantitative?: boolean;
  has_milestones?: boolean;
}

export interface WeeklyReportResponse {
  success: boolean;
  report?: string;
  parsed_data?: ParsedData;
  validation?: ValidationResult;
  error?: string;
}

export interface OKRResponse {
  success: boolean;
  okr?: string;
  validation?: ValidationResult;
  error?: string;
}

export interface HealthResponse {
  status: string;
  llm_configured: boolean;
  max_input_chars: number;
}

// Database record interfaces
export interface DailyReport {
  entry_date: string;
  content: string;
  created_at?: string;
  updated_at?: string;
}

export interface WeeklyReport {
  start_date: string;
  end_date: string;
  content: string;
  created_at?: string;
  updated_at?: string;
}

export interface OKRReport {
  creation_date: string;
  content: string;
  created_at?: string;
  updated_at?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    if (!response.ok) {
      throw new Error('API health check failed');
    }
    return response.json();
  }

  async getWeekRange(): Promise<WeekRange> {
    const response = await fetch(`${this.baseUrl}/api/week-range`);
    if (!response.ok) {
      throw new Error('Failed to get week range');
    }
    return response.json();
  }

  async generateWeeklyReport(content: string, useMock: boolean = false): Promise<WeeklyReportResponse> {
    const response = await fetch(`${this.baseUrl}/api/generate/weekly-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        use_mock: useMock,
      }),
    });
    return response.json();
  }

  async generateOKR(content: string, nextQuarter: string = '2026第一季度', useMock: boolean = false): Promise<OKRResponse> {
    const response = await fetch(`${this.baseUrl}/api/generate/okr`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        next_quarter: nextQuarter,
        use_mock: useMock,
      }),
    });
    return response.json();
  }

  async parseContent(content: string): Promise<{ success: boolean; data?: ParsedData; error?: string }> {
    const response = await fetch(`${this.baseUrl}/api/parse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    });
    return response.json();
  }

  // ========================
  // Daily Reports API
  // ========================

  async saveDailyReport(entryDate: string, content: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${this.baseUrl}/api/daily-reports`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        entry_date: entryDate,
        content,
      }),
    });
    return response.json();
  }

  async getDailyReport(entryDate: string): Promise<ApiResponse<DailyReport | null>> {
    const response = await fetch(`${this.baseUrl}/api/daily-reports/${entryDate}`);
    return response.json();
  }

  async getDailyReportsByRange(startDate: string, endDate: string): Promise<ApiResponse<DailyReport[]>> {
    const response = await fetch(
      `${this.baseUrl}/api/daily-reports/range?start_date=${startDate}&end_date=${endDate}`
    );
    return response.json();
  }

  async getDailyReportDates(): Promise<ApiResponse<string[]>> {
    const response = await fetch(`${this.baseUrl}/api/daily-reports/dates`);
    return response.json();
  }

  async deleteDailyReport(entryDate: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${this.baseUrl}/api/daily-reports/${entryDate}`, {
      method: 'DELETE',
    });
    return response.json();
  }

  // ========================
  // Weekly Reports API
  // ========================

  async saveWeeklyReport(startDate: string, endDate: string, content: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${this.baseUrl}/api/weekly-reports`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        start_date: startDate,
        end_date: endDate,
        content,
      }),
    });
    return response.json();
  }

  async getWeeklyReportByDate(startDate: string, endDate: string): Promise<ApiResponse<WeeklyReport | null>> {
    const response = await fetch(
      `${this.baseUrl}/api/weekly-reports/query?start_date=${startDate}&end_date=${endDate}`
    );
    return response.json();
  }

  async getLatestWeeklyReport(): Promise<ApiResponse<WeeklyReport | null>> {
    const response = await fetch(`${this.baseUrl}/api/weekly-reports/latest`);
    return response.json();
  }

  async getAllWeeklyReports(): Promise<ApiResponse<WeeklyReport[]>> {
    const response = await fetch(`${this.baseUrl}/api/weekly-reports`);
    return response.json();
  }

  async deleteWeeklyReport(startDate: string, endDate: string): Promise<ApiResponse<null>> {
    const response = await fetch(
      `${this.baseUrl}/api/weekly-reports?start_date=${startDate}&end_date=${endDate}`,
      {
        method: 'DELETE',
      }
    );
    return response.json();
  }

  // ========================
  // OKR Reports API
  // ========================

  async saveOKRReport(creationDate: string, content: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${this.baseUrl}/api/okr-reports`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        creation_date: creationDate,
        content,
      }),
    });
    return response.json();
  }

  async getOKRReport(creationDate: string): Promise<ApiResponse<OKRReport | null>> {
    const response = await fetch(`${this.baseUrl}/api/okr-reports/${creationDate}`);
    return response.json();
  }

  async getLatestOKRReport(): Promise<ApiResponse<OKRReport | null>> {
    const response = await fetch(`${this.baseUrl}/api/okr-reports/latest`);
    return response.json();
  }

  async getAllOKRReports(): Promise<ApiResponse<OKRReport[]>> {
    const response = await fetch(`${this.baseUrl}/api/okr-reports`);
    return response.json();
  }

  async deleteOKRReport(creationDate: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${this.baseUrl}/api/okr-reports/${creationDate}`, {
      method: 'DELETE',
    });
    return response.json();
  }
}

export const apiService = new ApiService();
export default apiService;
