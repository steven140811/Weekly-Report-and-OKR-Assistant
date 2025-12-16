# Weekly Report and OKR Assistant

[中文文档](README_CN.md) | English

An intelligent assistant to help you generate weekly reports and manage OKRs (Objectives and Key Results) efficiently.

> **Note**: This project is currently in the planning/documentation phase. The deployment instructions below serve as guidelines for when the implementation is complete.

## 📋 Features

- **Automated Weekly Report Generation**: Automatically generate comprehensive weekly reports based on your work logs
- **OKR Management**: Track and manage your objectives and key results
- **Smart Templates**: Customizable templates for different report formats
- **Progress Tracking**: Visual progress tracking for your goals and tasks
- **Export Options**: Export reports in multiple formats (PDF, Markdown, etc.)

## 🚀 One-Click Deployment

> **Note**: The following deployment methods will be available once the project implementation is complete. These instructions serve as a comprehensive guide for future deployment.

### Prerequisites

Before deployment, ensure you have:
- Node.js 16+ or Python 3.8+ (depending on your implementation)
- Git installed
- A GitHub account (for deployment options)

### Method 1: Deploy with Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/steven140811/Weekly-Report-and-OKR-Assistant)

1. Click the "Deploy with Vercel" button above
2. Sign in with your GitHub account
3. Follow the prompts to complete the deployment
4. Your application will be live in minutes!

### Method 2: Deploy with Netlify

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/steven140811/Weekly-Report-and-OKR-Assistant)

1. Click the "Deploy to Netlify" button above
2. Connect your GitHub account
3. Configure your site settings
4. Click "Deploy site"

### Method 3: Local Deployment

#### Quick Start

```bash
# Clone the repository
git clone https://github.com/steven140811/Weekly-Report-and-OKR-Assistant.git

# Navigate to the project directory
cd Weekly-Report-and-OKR-Assistant

# Install dependencies
npm install
# or if using Python
pip install -r requirements.txt

# Start the development server
npm run dev
# or if using Python
python app.py

# The application will be available at http://localhost:3000
```

#### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Method 4: Docker Deployment

```bash
# Build Docker image
docker build -t weekly-report-okr .

# Run container
docker run -p 3000:3000 weekly-report-okr

# Access at http://localhost:3000
```

### Method 5: Deploy with Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/steven140811/Weekly-Report-and-OKR-Assistant)

1. Click the "Deploy on Railway" button
2. Sign in with your GitHub account
3. Configure environment variables if needed
4. Deploy with one click

## 📖 Usage

### Creating a Weekly Report

1. Log in to the application
2. Navigate to "Weekly Report" section
3. Fill in your work achievements for the week
4. Click "Generate Report"
5. Review and export your report

### Managing OKRs

1. Go to the "OKR" section
2. Click "Add New Objective"
3. Define your objective and key results
4. Track progress throughout the quarter
5. Update status regularly

## 🛠️ Technology Stack

*Note: The specific technologies will be determined during implementation. Suggested options include:*

- **Frontend**: React / Vue.js / Next.js
- **Backend**: Node.js / Python
- **Database**: MongoDB / PostgreSQL
- **AI/ML**: OpenAI API / Custom NLP models
- **Deployment**: Vercel / Netlify / Docker

## 📝 Configuration

Create a `.env` file in the root directory:

```env
# API Configuration
API_KEY=your_api_key_here
DATABASE_URL=your_database_url

# Application Settings
PORT=3000
NODE_ENV=production
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

Project Link: [https://github.com/steven140811/Weekly-Report-and-OKR-Assistant](https://github.com/steven140811/Weekly-Report-and-OKR-Assistant)

## 🙏 Acknowledgments

- Thanks to all contributors
- Inspired by best practices in productivity tools
- Built with modern web technologies
=======
# 周报 & OKR 生成助手 (Weekly Report & OKR Assistant)

基于 LLM 的智能周报和 OKR 生成工具，支持从日报自动生成规范的周报邮件正文，以及根据历史材料生成季度 OKR。

## 功能特性

### 周报生成
- 从文本日报（单天或整周拼接）生成固定结构的周报邮件正文
- 自动识别日期格式（`20251212 8h` 或 `2025-12-12 8h`）
- 智能归类：手上项目、服务化能力建设、预研、其他事务性工作
- 自动去重合并相似条目
- 风险点提取与应对建议

### OKR 生成
- 结合历史材料生成下一季度 OKR
- 每个 KR 包含明确日期节点（`YYYY-MM-DD前`）
- 每个 KR 包含量化表达（阈值/比例/数量等）
- 关键 KR 包含阶段里程碑（M1/M2/M3）
- 生成 2-3 个目标

## 技术栈

- **前端**: React + TypeScript
- **后端**: Flask + Python
- **LLM**: OpenAI-like chat completions API

## 快速开始

### 方式一：一键启动脚本（推荐 Windows 用户）

**Windows 用户最简单的方式：**

1. 克隆项目并安装依赖
```bash
git clone https://github.com/steven140811/Weekly-Report-and-OKR-Assistant.git
cd Weekly-Report-and-OKR-Assistant

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
cd ..
```

2. 配置环境变量
```bash
# 编辑 backend\.env 文件，填入 LLM API 配置
# 如果不配置，将使用模拟模式
```

3. 一键启动所有服务
```bash
# 双击运行或在命令行执行
start_services.bat

# 停止服务
stop_services.bat
```

**特性：**
- ✅ 自动检测并释放端口冲突
- ✅ 后端使用 `pythonw.exe` 完全后台运行（无窗口）
- ✅ 前端后台运行
- ✅ 自动打开浏览器
- ✅ 日志输出到文件：`backend\backend.log` 和 `frontend\frontend.log`
- ✅ 启动脚本退出后服务继续运行

4. 访问应用
- 前端: http://localhost:5002
- 后端 API: http://localhost:5001

### 方式二：Docker Compose

1. 克隆项目
```bash
git clone https://github.com/steven140811/Weekly-Report-and-OKR-Assistant.git
cd Weekly-Report-and-OKR-Assistant
```

2. 配置环境变量（可选，不配置将使用模拟模式）
```bash
cp .env.example .env
# 编辑 .env 文件，填入 LLM API 配置
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端: http://localhost:3000
- 后端 API: http://localhost:5000

### 方式三：手动部署

#### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
export LLM_API_URL=https://your-llm-api-url/v1
export LLM_API_KEY=your-api-key

# 启动开发服务器
python app.py

# 或使用 gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

#### 前端

```bash
cd frontend
npm install

# 开发模式
npm start

# 生产构建
npm run build
```

## API 文档

### 健康检查
```
GET /api/health
```

### 获取周范围
```
GET /api/week-range
```

### 生成周报
```
POST /api/generate/weekly-report
Content-Type: application/json

{
  "content": "日报内容...",
  "use_mock": false
}
```

### 生成 OKR
```
POST /api/generate/okr
Content-Type: application/json

{
  "content": "历史材料...",
  "next_quarter": "2026第一季度",
  "use_mock": false
}
```

## 配置说明

### 环境变量

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| LLM_API_URL | LLM API 地址 | - |
| LLM_API_KEY | LLM API 密钥 | - |
| LLM_MODEL | LLM 模型名称 | default/deepseek-v3-2 |
| LLM_TIMEOUT | API 超时时间(秒) | 120 |
| LLM_RETRY | 重试次数 | 3 |
| MAX_INPUT_CHARS | 最大输入字符数 | 20000（冻结） |
| PORT | 后端端口 | 5001（脚本启动）/ 5000（Docker） |

### 端口配置

- **脚本启动方式**：
  - 后端：5001
  - 前端：5002
  
- **Docker 启动方式**：
  - 后端：5000
  - 前端：3000

### 配置文件位置

- 后端配置：`backend\.env`
- 前端配置：`frontend\.env`（可选）

## 周报输出格式

```
周报（YYYY-MM-DD ~ YYYY-MM-DD）

本周一句话总结：[进展 + 风险，不超过100字]

1、手上项目、服务化能力建设、预研的主要进展

手上项目
- ...

服务化能力建设
- ...

预研
- ...

2、是否有风险，哪些风险点？
- 风险1 + 应对建议
- ...

3、其他的事务性工作
- ...

4、下周大概的计划
- ...
```

**注意**：系统会自动清理 LLM 可能生成的多余序号，确保输出格式统一。

## OKR 输出格式

```
2026第一季度OKR：

目标 O1：...
KR1：YYYY-MM-DD前...（量化表达）；
KR2：YYYY-MM-DD前...；

目标 O2：...
KR1：M1阶段(日期前)...；M2阶段(日期前)...；M3阶段(日期前)...；
```

## 开发

### 运行测试

```bash
cd backend
python -m pytest tests/ -v
```

### 脚本说明

- **`start_services.bat`**：Windows 一键启动脚本
  - 自动检测端口占用
  - 使用 `pythonw.exe` 后台启动后端（无窗口）
  - 后台启动前端
  - 自动打开浏览器
  
- **`stop_services.bat`**：Windows 一键停止脚本
  - 停止所有相关服务
  - 清理残留进程

- **`start_backend.bat`**：单独启动后端
- **`QUICK_START.md`**：详细使用指南
- **`使用说明.txt`**：快速参考

### 项目结构

```
.
├── backend/
│   ├── app.py          # Flask 应用主入口
│   ├── config.py       # 配置管理
│   ├── parser.py       # 日报解析模块
│   ├── generator.py    # 周报/OKR 生成逻辑
│   ├── llm_client.py   # LLM API 客户端
│   ├── prompts.py      # Prompt 模板
│   └── tests/          # 测试文件
├── frontend/
│   ├── src/
│   │   ├── components/ # React 组件
│   │   ├── services/   # API 服务
│   │   └── App.tsx     # 主应用
│   └── public/
├── docker-compose.yml
└── README.md
```

