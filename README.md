# WorkPilot - Productivity Assistant

[中文文档](README_CN.md) | English

An AI-powered intelligent productivity assistant designed to boost workplace efficiency. With six core features - daily report management, intelligent weekly report generation, OKR goal planning, career asset accumulation, and skills radar analysis - it helps you say goodbye to tedious document organization and makes report writing and career development planning simple and efficient.

**Core Value:**
- 📝 **Daily Management**: Calendar-style daily report entry with holiday display, built-in TODO reminder panel
- 🤖 **Smart Weekly Reports**: One-click generation of standardized weekly reports from daily entries, auto-categorize, deduplicate, and extract risks
- 🎯 **OKR Planning**: Intelligently generate quarterly OKRs based on historical materials, with quantitative metrics and milestone nodes
- 💼 **Career Assets**: Auto-extract STAR-format work achievements, accumulate career assets
- 📊 **Skills Radar**: Track skill growth, AI-powered categorization, visualize capability distribution
- 📤 **Multi-format Export**: Support export to CSV, Markdown, TXT formats
- 💾 **Local Storage**: All data stored in local SQLite database, secure and reliable
- 🚀 **One-Click Deployment**: Support Docker or local deployment, Windows users can use batch scripts for one-click start

## 📸 Product Showcase

### Daily Report Entry
![Daily Report Entry](./screenshots/daily-report-entry.png)
*Calendar View + Holiday Display + TODO Tips Panel + Quick Template + Multi-format Export*

### Weekly Report Generator
![Weekly Report Generator](./screenshots/weekly-report-generator.png)
*Import from Daily Reports + Smart Categorization + Risk Analysis*

### Weekly Report Query
![Weekly Report Query](./screenshots/weekly-report-query.png)
*History Query + Edit/Delete Functions + Multi-format Export*

### OKR Management
![OKR Management](./screenshots/okr-generator.png)
*Smart Generation + Quantitative Metrics + Milestone Planning + Multi-format Export*

### Career Assets
![Career Assets](./screenshots/career-assets.png)
*STAR Format Extraction + Project Timeline + Career Asset Management*

### Skills Radar
![Skills Radar](./screenshots/skills-radar.png)
*Skills Distribution Visualization + AI Categorization + Skill Details View*

> 💡 **Tip**: To add screenshots, place image files in the `screenshots/` directory. See [screenshots/README.md](./screenshots/README.md) for details.

## 📋 Features

### 📅 Daily Report Entry
- **Calendar View**: Large calendar interface, click on a date to directly enter daily report
- **Holiday Display**: Calendar shows Chinese traditional holidays and international holidays (Spring Festival, Mid-Autumn, National Day, Christmas, etc.)
- **Weekend Indicator**: Saturdays and Sundays displayed in red text
- **Data Persistence**: Daily reports automatically saved to local SQLite database
- **Quick Template**: Support inserting daily report template for quick filling
- **Status Indicator**: Recorded dates marked in green for clear visibility
- **Statistics**: Display monthly and total entry counts
- **TODO Tips**: Left-side floating note panel, can add/check/delete TODO items
- **Multi-format Export**: Export current or all daily reports to CSV/Markdown/TXT format

### 📋 Weekly Report Generation
- **Automatic Generation**: Generate standardized weekly report email format from text daily reports
- **Import from Daily Reports**: One-click select recorded daily reports, support custom date ranges
- **Flexible Date Range**: Generate reports using actual imported date ranges, not fixed current week range
- **Smart Date Recognition**: Automatically recognize date formats (`20251212 8h` or `2025-12-12 8h`)
- **Smart Categorization**: Auto-categorize into projects, capability building, research, and other administrative work
- **Deduplication & Merging**: Auto deduplicate and merge similar items
- **Risk Analysis**: Extract risk points and provide response suggestions
- **Save Report**: Generated reports can be saved to database

### 🔍 Weekly Report Query
- **History Query**: Query historical weekly reports by date range
- **Edit Function**: Can edit saved weekly reports
- **Delete Function**: Can delete unwanted weekly report records
- **Multi-format Export**: Export to CSV/Markdown/TXT format

### 🎯 OKR Management
- **Smart Generation**: Generate next quarter OKR based on historical materials
- **Clear Date Node**: Each KR contains clear date node (`YYYY-MM-DD before`)
- **Quantitative Metrics**: Each KR contains quantitative expression (threshold/ratio/quantity etc.)
- **Milestone Planning**: Key KRs contain phase milestones (M1/M2/M3)
- **Goal Management**: Generate 2-3 reasonable objectives
- **Save OKR**: Generated OKRs can be saved to database
- **Multi-format Export**: Export to CSV/Markdown/TXT format

### 💼 Career Assets (Resume Building Blocks)
- **STAR Format Extraction**: Intelligently extract Situation-Task-Action-Result format achievements from daily/weekly reports
- **Project Classification**: Auto-identify and categorize projects
- **Timeline View**: Display career achievements in chronological order
- **Achievement Editing**: Support editing STAR summaries to improve career assets
- **Data Cleanup**: Support merging similar projects and cleaning invalid data

### 📊 Skills Radar
- **Skills Distribution Visualization**: Radar chart showing skill usage frequency
- **AI Smart Categorization**: Use LLM to intelligently identify skill categories (Technical/Soft/Domain)
- **Category Filtering**: Filter and view by skill category
- **Skill Details**: Click on skills to view related work items
- **Growth Tracking**: Record first and last use time for each skill

### 💾 Data Storage
- Use SQLite lightweight database
- Database file location: `backend/data/reports.db`
- Tables: daily_reports, weekly_reports, okr_reports, todo_items, work_items, projects, skills, etc.

## 🛠️ Technology Stack

- **Frontend**: React + TypeScript
- **Backend**: Flask + Python
- **LLM**: OpenAI-like chat completions API
- **Deployment**: Docker / Local / Batch Scripts

## 🚀 Quick Start

### Method 1: One-Click Launch Script (Recommended for Windows Users) ⭐

**Simplest way for Windows users:**

1. Clone project and install dependencies
```bash
git clone https://github.com/steven140811/WorkPilot.git
cd WorkPilot

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
cd ..
```

2. Configure environment variables
```bash
# Edit backend\.env file, fill in LLM API configuration
# If not configured, will use mock mode
```

3. One-click launch all services
```bash
# Double-click to run or execute in command line
start_services.bat

# Stop services
stop_services.bat
```

**Features:**
- ✅ Auto-detect and release port conflicts
- ✅ Backend runs completely in background with `pythonw.exe` (no window)
- ✅ Frontend runs in background
- ✅ Auto-open browser
- ✅ Log output to files: `backend\backend.log` and `frontend\frontend.log`
- ✅ Services continue running after script exits

4. Access application
- Frontend: http://localhost:5002
- Backend API: http://localhost:5001

### Method 2: Docker Compose

```bash
# Build Docker images
docker-compose up -d

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

### Method 3: Manual Deployment

#### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## 📁 Project Structure

```
WorkPilot/
├── backend/                 # Flask backend application
│   ├── app.py              # Main application entry
│   ├── config.py           # Configuration management
│   ├── generator.py        # Report generation logic
│   ├── llm_client.py       # LLM client
│   ├── parser.py           # Text parser
│   ├── prompts.py          # AI prompt templates
│   ├── database.py         # SQLite database module
│   ├── requirements.txt    # Python dependencies
│   ├── data/               # Data directory
│   │   └── reports.db      # SQLite database file
│   └── tests/              # Test files
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── DailyReportEntry.tsx      # Daily report entry component
│   │   │   ├── WeeklyReportGenerator.tsx # Weekly report generator component
│   │   │   ├── WeeklyReportQuery.tsx     # Weekly report query component
│   │   │   ├── OKRGenerator.tsx          # OKR generator component
│   │   │   ├── CareerAssets.tsx          # Career assets component
│   │   │   ├── SkillsRadar.tsx           # Skills radar component
│   │   │   └── ExportButton.tsx          # Export button component
│   │   ├── services/
│   │   │   └── api.ts      # API service layer
│   │   ├── utils/
│   │   │   ├── holidays.ts # Holiday data
│   │   │   └── export.ts   # Export utility functions
│   │   └── App.tsx         # Main application component
│   └── package.json
├── docker-compose.yml      # Docker compose file
├── start_services.bat      # Windows one-click start script
├── stop_services.bat       # Windows one-click stop script
└── README.md               # Project documentation
```

## 📡 API Endpoints

### Weekly Report Generation
- `POST /api/generate/weekly-report` - Generate weekly report

### OKR Generation
- `POST /api/generate/okr` - Generate OKR

### Daily Report Management
- `GET /api/daily-reports?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Query daily reports
- `GET /api/daily-report/<date>` - Get daily report for specific date
- `POST /api/daily-report` - Save daily report
- `PUT /api/daily-report/<date>` - Update daily report
- `DELETE /api/daily-report/<date>` - Delete daily report

### Weekly Report Management
- `GET /api/weekly-reports?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Query weekly reports
- `GET /api/weekly-report/<id>` - Get specific weekly report
- `POST /api/weekly-report` - Save weekly report
- `PUT /api/weekly-report/<id>` - Update weekly report
- `DELETE /api/weekly-report/<id>` - Delete weekly report

### OKR Management
- `GET /api/okr-reports?quarter=YYYY-QN` - Query OKRs
- `GET /api/okr-report/<id>` - Get specific OKR
- `POST /api/okr-report` - Save OKR
- `PUT /api/okr-report/<id>` - Update OKR
- `DELETE /api/okr-report/<id>` - Delete OKR

### TODO Management
- `GET /api/todo-items` - Get all TODO items
- `POST /api/todo-items` - Create TODO item
- `PUT /api/todo-items/<id>` - Update TODO item (content/completion status)
- `DELETE /api/todo-items/<id>` - Delete TODO item

## 🔧 Environment Variables Configuration

Configure LLM-related parameters in the `backend/.env` file. You can refer to the `.env.example` file in the project root directory for configuration.

**Configuration Example:**

```bash
# LLM Configuration (Required for real LLM calls)
# If not configured, the application will use mock mode
LLM_API_URL=https://api.deepseek.com/v1    # LLM API URL
LLM_API_KEY=sk-your-api-key-here           # Your API key
LLM_MODEL=deepseek-chat                     # Model name

# Optional: LLM timeout and retry settings
LLM_TIMEOUT=30                              # Timeout in seconds, default 30
LLM_RETRY=2                                 # Retry count, default 2

# Flask Configuration
PORT=5001                                   # Backend service port
FLASK_DEBUG=false                           # Debug mode switch
```

**Configuration Steps:**

1. Copy the example configuration file:
   ```bash
   cp .env.example backend/.env
   ```

2. Edit the `backend/.env` file and fill in your LLM API configuration
   - `LLM_API_URL`: API address of the LLM service
   - `LLM_API_KEY`: Your API key (required)
   - `LLM_MODEL`: Model name to use

3. If LLM is not configured, the application will run in mock mode (returning test data)

**Supported LLM Providers:**
- DeepSeek: `https://api.deepseek.com/v1`
- OpenAI: `https://api.openai.com/v1`
- Azure OpenAI: `https://your-resource.openai.azure.com/`
- Other services compatible with OpenAI API format

## 📝 License

MIT License

