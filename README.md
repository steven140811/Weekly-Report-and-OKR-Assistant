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

### 方式一：Docker Compose（推荐）

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

### 方式二：手动部署

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

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| LLM_API_URL | LLM API 地址 | - |
| LLM_API_KEY | LLM API 密钥 | - |
| LLM_MODEL | LLM 模型名称 | default/deepseek-v3-2 |
| LLM_TIMEOUT | API 超时时间(秒) | 30 |
| LLM_RETRY | 重试次数 | 2 |
| MAX_INPUT_CHARS | 最大输入字符数 | 20000（冻结） |

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

## License

MIT
