# 周报与OKR助手

中文文档 | [English](README.md)

一个智能助手，帮助您高效生成周报和管理OKR（目标与关键成果）。基于 LLM 的智能周报和 OKR 生成工具，支持从日报自动生成规范的周报邮件正文，以及根据历史材料生成季度 OKR。

## 📋 功能特性

### 周报生成
- **自动周报生成**：从文本日报（单天或整周拼接）生成固定结构的周报邮件正文
- **智能日期识别**：自动识别日期格式（`20251212 8h` 或 `2025-12-12 8h`）
- **智能分类**：自动归类手上项目、服务化能力建设、预研、其他事务性工作
- **去重合并**：自动去重合并相似条目
- **风险分析**：风险点提取与应对建议
- **格式规范**：统一的周报输出格式

### OKR 管理
- **智能 OKR 生成**：结合历史材料生成下一季度 OKR
- **明确时间节点**：每个 KR 包含明确日期节点（`YYYY-MM-DD前`）
- **量化指标**：每个 KR 包含量化表达（阈值/比例/数量等）
- **里程碑规划**：关键 KR 包含阶段里程碑（M1/M2/M3）
- **目标管理**：生成 2-3 个合理目标

## 🛠️ 技术栈

- **前端**: React + TypeScript
- **后端**: Flask + Python
- **LLM**: OpenAI-like chat completions API
- **部署**: Docker / 本地 / 批处理脚本

## 🚀 快速开始

### 方式一：一键启动脚本（推荐 Windows 用户）⭐

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

### 方式二：Docker 部署

```bash
# 构建 Docker 镜像
docker-compose up -d

# 访问应用
# 前端: http://localhost:3000
# 后端 API: http://localhost:5000
```

### 方式三：手动部署

#### 后端
