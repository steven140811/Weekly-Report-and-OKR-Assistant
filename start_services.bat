@echo off
chcp 65001 >nul
echo ========================================
echo 启动周报与OKR助手服务
echo ========================================
echo.

REM 设置项目根目录
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo [1/3] 检查端口占用情况...
echo.

REM 检查端口5001（后端）
netstat -ano | findstr ":5001" >nul 2>&1
if %errorlevel% equ 0 (
    echo 警告: 端口 5001 已被占用，将尝试停止...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5001"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM 检查端口5002（前端）
netstat -ano | findstr ":5002" >nul 2>&1
if %errorlevel% equ 0 (
    echo 警告: 端口 5002 已被占用，将尝试停止...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5002"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo [2/3] 启动后端服务（端口 5001）...

REM 使用 pythonw.exe 在后台运行（无窗口）
cd /d "%PROJECT_ROOT%backend"
start /B pythonw.exe app.py > backend.log 2>&1

echo 后端服务已在后台启动
echo    - 地址: http://localhost:5001
echo    - 日志: backend\backend.log
echo.

REM 等待后端启动
echo    等待后端服务就绪...
timeout /t 5 /nobreak >nul

echo [3/3] 启动前端服务（端口 5002）...

REM 设置环境变量并在后台启动前端
cd /d "%PROJECT_ROOT%frontend"
set PORT=5002
set BROWSER=none
start /B cmd /c "npm start > frontend.log 2>&1"

echo 前端服务已在后台启动
echo    - 地址: http://localhost:5002
echo    - 日志: frontend\frontend.log
echo.

REM 等待前端启动
echo    等待前端服务就绪（约30秒）...
timeout /t 30 /nobreak >nul

echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo 服务信息:
echo    后端: http://localhost:5001
echo    前端: http://localhost:5002
echo.
echo 提示: 
echo    - 使用 stop_services.bat 停止所有服务
echo    - 服务在后台运行
echo    - 日志: backend\backend.log 和 frontend\frontend.log
echo.

REM 自动打开浏览器
echo 正在打开浏览器...
timeout /t 2 /nobreak >nul
start http://localhost:5002

echo.
echo 按任意键退出本窗口（服务将继续在后台运行）...
pause >nul
