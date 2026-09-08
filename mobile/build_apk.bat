@echo off
setlocal
echo =======================================================
echo Building RazorRevive-OS Android APK
echo =======================================================
cd /d "%~dp0"
call gradlew.bat assembleDebug
if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    exit /b %errorlevel%
)
copy /y "app\build\outputs\apk\debug\app-debug.apk" "razorrevive-os.apk" >nul
echo.
echo [SUCCESS] APK built successfully!
echo Output: %~dp0razorrevive-os.apk
echo =======================================================
