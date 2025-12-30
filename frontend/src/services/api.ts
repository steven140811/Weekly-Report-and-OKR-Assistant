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

export interface TodoItem {
  id: number;
  content: string;
  completed: number;
  sort_order: number;
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

  async generateWeeklyReport(
    content: string, 
    useMock: boolean = false,
    startDate?: string,
    endDate?: string
  ): Promise<WeeklyReportResponse> {
    const requestBody: any = {
      content,
      use_mock: useMock,
    };
    
    // Add date range if provided
    if (startDate && endDate) {
      requestBody.start_date = startDate;
      requestBody.end_date = endDate;
    }
    
    const response = await fetch(`${this.baseUrl}/api/generate/weekly-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
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

  async updateOKRReport(creationDate: string, content: string): Promise<ApiResponse<null>> {
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

  // ========================
  // TODO Items API
  // ========================

  async getTodoItems(): Promise<ApiResponse<TodoItem[]>> {
    const response = await fetch(`${this.baseUrl}/api/todo-items`);
    return response.json();
  }

  async createTodoItem(content: string): Promise<ApiResponse<TodoItem>> {
    const response = await fetch(`${this.baseUrl}/api/todo-items`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    });
    return response.json();
  }

  async updateTodoItem(id: number, updates: { content?: string; completed?: boolean }): Promise<ApiResponse<TodoItem>> {
    const response = await fetch(`${this.baseUrl}/api/todo-items/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    return response.json();
  }

  async deleteTodoItem(id: number): Promise<ApiResponse<null>> {
    const response = await fetch(`${this.baseUrl}/api/todo-items/${id}`, {
      method: 'DELETE',
    });
    return response.json();
  }

  // ========================================
  // Career Asset Management API (新增)
  // ========================================

  // --- Projects API ---

  async getProjects(status?: string): Promise<ApiResponse<Project[]>> {
    const url = status 
      ? `${this.baseUrl}/api/projects?status=${status}`
      : `${this.baseUrl}/api/projects`;
    const response = await fetch(url);
    return response.json();
  }

  async getProjectsSummary(): Promise<ApiResponse<ProjectSummary[]>> {
    const response = await fetch(`${this.baseUrl}/api/projects/summary`);
    return response.json();
  }

  async getProject(projectId: number): Promise<ApiResponse<ProjectWithWorkItems>> {
    const response = await fetch(`${this.baseUrl}/api/projects/${projectId}`);
    return response.json();
  }

  async createProject(name: string, description?: string): Promise<ApiResponse<Project>> {
    const response = await fetch(`${this.baseUrl}/api/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description }),
    });
    return response.json();
  }

  async updateProject(projectId: number, updates: Partial<Project>): Promise<ApiResponse<Project>> {
    const response = await fetch(`${this.baseUrl}/api/projects/${projectId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return response.json();
  }

  async deleteProject(projectId: number): Promise<ApiResponse<null>> {
    const response = await fetch(`${this.baseUrl}/api/projects/${projectId}`, {
      method: 'DELETE',
    });
    return response.json();
  }

  async generateProjectStar(projectId: number): Promise<{ success: boolean; summary?: string; error?: string }> {
    const response = await fetch(`${this.baseUrl}/api/projects/${projectId}/star`, {
      method: 'POST',
    });
    return response.json();
  }

  // --- Project Cleanup API ---

  async cleanupNullProjects(): Promise<{ success: boolean; message: string; merged_count: number; deleted_projects: number }> {
    const response = await fetch(`${this.baseUrl}/api/projects/cleanup/null`, {
      method: 'POST',
    });
    return response.json();
  }

  async getSimilarProjects(threshold: number = 0.6): Promise<{ success: boolean; groups: Array<{ recommended_target: any; projects: any[]; project_ids: number[] }> }> {
    const response = await fetch(`${this.baseUrl}/api/projects/similar?threshold=${threshold}`);
    return response.json();
  }

  async mergeProjects(targetProjectId: number, sourceProjectIds: number[]): Promise<{ success: boolean; message: string; merged_count?: number }> {
    const response = await fetch(`${this.baseUrl}/api/projects/merge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        target_project_id: targetProjectId,
        source_project_ids: sourceProjectIds,
      }),
    });
    return response.json();
  }

  async deleteAllProjects(): Promise<{ success: boolean; message: string; deleted_projects?: number; deleted_work_items?: number }> {
    const response = await fetch(`${this.baseUrl}/api/projects/all`, {
      method: 'DELETE',
    });
    return response.json();
  }

  // --- Work Items API ---

  async getWorkItems(): Promise<ApiResponse<WorkItem[]>> {
    const response = await fetch(`${this.baseUrl}/api/work-items`);
    return response.json();
  }

  async getWorkItemsByRange(startDate: string, endDate: string): Promise<ApiResponse<WorkItem[]>> {
    const response = await fetch(
      `${this.baseUrl}/api/work-items/range?start_date=${startDate}&end_date=${endDate}`
    );
    return response.json();
  }

  async createWorkItem(data: Partial<WorkItem>): Promise<ApiResponse<WorkItem>> {
    const response = await fetch(`${this.baseUrl}/api/work-items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async updateWorkItem(itemId: number, updates: Partial<WorkItem>): Promise<ApiResponse<WorkItem>> {
    const response = await fetch(`${this.baseUrl}/api/work-items/${itemId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return response.json();
  }

  async deleteWorkItem(itemId: number): Promise<ApiResponse<null>> {
    const response = await fetch(`${this.baseUrl}/api/work-items/${itemId}`, {
      method: 'DELETE',
    });
    return response.json();
  }

  // --- Extraction API ---

  async extractWorkItems(
    logContent: string, 
    logDate: string, 
    autoSave: boolean = false
  ): Promise<ExtractionResult> {
    const response = await fetch(`${this.baseUrl}/api/extract-work-items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        log_content: logContent, 
        log_date: logDate,
        auto_save: autoSave 
      }),
    });
    return response.json();
  }

  // --- Skills API ---

  async getSkills(): Promise<ApiResponse<Skill[]>> {
    const response = await fetch(`${this.baseUrl}/api/skills`);
    return response.json();
  }

  async getSkillsStats(): Promise<ApiResponse<SkillsStats>> {
    const response = await fetch(`${this.baseUrl}/api/skills/stats`);
    return response.json();
  }

  async getWorkItemsBySkill(skillName: string): Promise<ApiResponse<WorkItem[]>> {
    const response = await fetch(`${this.baseUrl}/api/skills/${encodeURIComponent(skillName)}/work-items`);
    return response.json();
  }

  async recategorizeSkills(): Promise<{ success: boolean; message: string; updated_count?: number }> {
    const response = await fetch(`${this.baseUrl}/api/skills/recategorize`, {
      method: 'POST',
    });
    return response.json();
  }

  async recategorizeSkillsWithLLM(): Promise<{ success: boolean; message: string; updated_count?: number; details?: any[] }> {
    const response = await fetch(`${this.baseUrl}/api/skills/recategorize-llm`, {
      method: 'POST',
    });
    return response.json();
  }
}

// New interfaces for Career Asset Management
export interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
  start_date?: string;
  end_date?: string;
  star_summary?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ProjectSummary extends Project {
  work_item_count: number;
  first_work_date?: string;
  last_work_date?: string;
}

export interface WorkItem {
  id: number;
  raw_log_date: string;
  project_id?: number;
  project_name?: string;
  action?: string;
  problem?: string;
  result_metric?: string;
  skills_tags?: string;
  extraction_status: string;
  created_at?: string;
  updated_at?: string;
}

export interface ProjectWithWorkItems extends Project {
  work_items: WorkItem[];
}

export interface Skill {
  id: number;
  name: string;
  category?: string;
  count: number;
  first_used_date?: string;
  last_used_date?: string;
}

export interface SkillsStats {
  top_skills: { name: string; count: number }[];
  by_category: Record<string, number>;
  total_unique: number;
}

export interface ExtractedWorkItem {
  project?: string;
  action?: string;
  problem?: string;
  result_metric?: string;
  skills?: string[];
}

export interface ExtractionResult {
  success: boolean;
  work_items: ExtractedWorkItem[];
  extraction_quality: 'good' | 'partial' | 'insufficient';
  notes?: string;
  error?: string;
  saved_items?: WorkItem[];
}

export const apiService = new ApiService();
export default apiService;
