@echo off
chcp 65001 >nul
echo ========================================
echo 停止周报与OKR助手服务
echo ========================================
echo.

echo [1/3] 查找并停止后端服务（端口 5001）...

REM 查找占用端口5001的进程
set "backend_found=0"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5001" 2^>nul') do (
    set "backend_found=1"
    echo    - 正在停止进程 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

if %backend_found% equ 0 (
    echo    后端服务未运行
) else (
    echo    后端服务已停止
)
echo.

echo [2/3] 查找并停止前端服务（端口 5002）...

REM 查找占用端口5002的进程
set "frontend_found=0"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5002" 2^>nul') do (
    set "frontend_found=1"
    echo    - 正在停止进程 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

if %frontend_found% equ 0 (
    echo    前端服务未运行
) else (
    echo    前端服务已停止
)
echo.

echo [3/3] 清理残留的进程...

REM 停止所有python进程中包含app.py的
for /f "tokens=2" %%a in ('tasklist ^| findstr /I "python.exe"') do (
    wmic process where ProcessId=%%a get CommandLine 2>nul | findstr /C:"app.py" >nul 2>&1
    if not errorlevel 1 (
        echo    - 停止 Python 进程 PID: %%a
        taskkill /F /PID %%a >nul 2>&1
    )
)

REM 停止所有node进程中包含react-scripts的
for /f "tokens=2" %%a in ('tasklist ^| findstr /I "node.exe"') do (
    wmic process where ProcessId=%%a get CommandLine 2>nul | findstr /C:"react-scripts" >nul 2>&1
    if not errorlevel 1 (
        echo    - 停止 Node 进程 PID: %%a
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo    清理完成
echo.

echo ========================================
echo 所有服务已停止！
echo ========================================
echo.
echo 提示: 
echo    - 使用 start_services.bat 重新启动服务
echo.

echo 按任意键退出...
pause >nul
