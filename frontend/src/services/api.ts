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
}

export const apiService = new ApiService();
export default apiService;
